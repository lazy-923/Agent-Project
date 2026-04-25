"""Mini Deep Research graph.

This module exposes `graph` for LangGraph Studio / LangGraph dev server and
also provides a small CLI for local testing.
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field, TypeAdapter, ValidationError


load_dotenv()


def build_llm() -> ChatOpenAI:
    """Create an OpenAI-compatible chat model from environment variables."""
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "qwen3-max"),
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("API_KEY"),
    )


llm = build_llm()

planner_prompt = ChatPromptTemplate(
    [
        (
            "system",
            """你是一名乐于助人的研究助理。根据给定的问题，提出一组需要进行的网页搜索，尽可能全面地回答该问题。请输出 3 到 4 个搜索关键词。

你必须输出 JSON，并严格按照如下格式：
{{
  "searches": [
    {{
      "query": "搜索关键词",
      "reason": "这样搜索的理由"
    }}
  ]
}}

请严格使用 JSON Schema 结构，不要添加额外字段。""",
        ),
        ("human", "{query}"),
    ]
)


class WebSearchItem(BaseModel):
    query: str = Field(description="用于网络搜索的关键词")
    reason: str = Field(description="为什么这个搜索对于解答该问题很重要")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="需要执行的网页搜索列表")


planner_chain = planner_prompt | llm.with_structured_output(WebSearchPlan)

SEARCH_INSTRUCTIONS = (
    "你是一名研究助理。根据提供的搜索词在网络上搜索，并生成一份简明摘要。"
    "摘要应包含 2 到 3 个段落，总字数不超过 300 字。"
    "务必抓住主要观点，忽略无关信息。除摘要本身外，不要添加额外评论。"
)

search_tool = TavilySearch(max_results=5, topic="general")
search_agent = create_agent(
    model=llm,
    system_prompt=SEARCH_INSTRUCTIONS,
    tools=[search_tool],
)


class ReportData(BaseModel):
    short_summary: str = Field(description="2 到 3 句话的研究结论摘要")
    markdown_report: str = Field(description="最终生成的 Markdown 报告")
    follow_up_question: str = Field(description="建议进一步研究的相关主题")


WRITER_PROMPT = (
    "你是一名高级研究员，负责为一个研究问题撰写一份连贯的中文研究报告。"
    "你必须使用 JSON 格式输出结果，并严格包含以下字段："
    "short_summary, markdown_report, follow_up_question。"
    "你将获得原始问题以及由研究助理完成的初步搜索摘要。"
    "请先组织清晰的大纲，再生成完整报告。"
    "最终报告应使用 Markdown 格式，内容详尽，至少 1500 字。"
)

writer_prompt = ChatPromptTemplate(
    [
        ("system", WRITER_PROMPT),
        ("human", "{query}"),
    ]
)
writer_chain = writer_prompt | llm.with_structured_output(ReportData)


def _coerce_plan(raw: object) -> WebSearchPlan:
    """Normalize structured-output variants into a WebSearchPlan."""
    try:
        return TypeAdapter(WebSearchPlan).validate_python(raw)
    except ValidationError:
        if isinstance(raw, dict) and isinstance(raw.get("searches"), list):
            return WebSearchPlan.model_validate(raw)
        raise


def planner_node(state: MessagesState) -> dict:
    user_query = state["messages"][-1].content
    raw = planner_chain.invoke({"query": user_query})
    plan = _coerce_plan(raw)
    return {"messages": [AIMessage(content=plan.model_dump_json())]}


def search_node(state: MessagesState) -> dict:
    plan_json = state["messages"][-1].content
    plan = WebSearchPlan.model_validate_json(plan_json)

    summaries = []
    for item in plan.searches:
        run = search_agent.invoke({"messages": [HumanMessage(content=item.query)]})
        messages = run["messages"]
        readable = next(
            (m for m in reversed(messages) if isinstance(m, (ToolMessage, AIMessage))),
            messages[-1],
        )
        summaries.append(f"## {item.query}\n\n{readable.content}")

    return {"messages": [AIMessage(content="\n\n".join(summaries))]}


def writer_node(state: MessagesState) -> dict:
    original_query = state["messages"][0].content
    combined_summary = state["messages"][-1].content
    writer_input = f"原始问题: {original_query}\n\n搜索摘要:\n{combined_summary}"

    report: ReportData = writer_chain.invoke({"query": writer_input})
    return {
        "messages": [
            AIMessage(content=json.dumps(report.model_dump(), ensure_ascii=False, indent=2))
        ]
    }


builder = StateGraph(MessagesState)
builder.add_node("planner_node", planner_node)
builder.add_node("search_node", search_node)
builder.add_node("writer_node", writer_node)

builder.add_edge(START, "planner_node")
builder.add_edge("planner_node", "search_node")
builder.add_edge("search_node", "writer_node")
builder.add_edge("writer_node", END)

graph = builder.compile()


def main() -> None:
    """Run one research query from the command line."""
    query = input("请输入研究问题：").strip()
    if not query:
        print("问题不能为空。")
        return

    result = graph.invoke({"messages": [HumanMessage(content=query)]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
