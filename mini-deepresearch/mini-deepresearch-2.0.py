from langchain.agents import create_agent
from pydantic import BaseModel,Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
import os
import dotenv
dotenv.load_dotenv()

llm=ChatOpenAI(
    model="qwen3-max",
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

planner_prompt = ChatPromptTemplate([
    ('system',
     '''你是一名乐于助人的研究助理。根据给定的问题，提出一组需要进行的网页搜索，尽可能全面地回答该问题。请输出3到4个搜索关键词。你必须输出 JSON，并严格按照如下格式：
{{
  "searches": [
    {{
      "query": "搜索关键词",
      "reason": "这样搜索的理由"
    }}
  ]
}}
请严格使用JSONSchema 结构，不要有空格，不要添加额外字段。'''
     ),
    ('human','{query}')
])
class WebSearchItem(BaseModel):
    query: str=Field(description="用于网络搜索的关键词")
    reason: str=Field(description="为什么这个搜索对于解答该问题很重要的理由")
class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]=Field(description="为了尽可能全面回答该问题而需要执行的网页搜索列表")
planner_chain=planner_prompt | llm.with_structured_output(WebSearchPlan)

SEARCH_INSTRUCTIONS = (
    '你是一名研究助理。根据提供的搜索词，你需要在网络上进行搜索，并生成一份简明扼要的结果摘要。摘要应包含2到3个段落，总字数不超过300字。务必抓住主要观点，表述简洁，无需使用完整句子或优美语法。这份摘要将供他人用于整合研究报告，因此至关重要的是，你要准确提炼核心内容，忽略任何无关信息。除摘要本身外，不要添加任何额外评论。')
search_tool=TavilySearch(max_results=5,topics='general')
search_agent=create_agent(
    model=llm,
    system_prompt=SEARCH_INSTRUCTIONS,
    tools=[search_tool],
)

class ReportData(BaseModel):
    short_summary: str = Field(description="一份2-3句话的简短研究结论摘要")
    markdown_report: str = Field(description="最终生成的报告(markdown格式)")
    follow_up_question: str = Field(description="建议进一步研究的相关主题")
WRITER_PROMPT = (
    "你是一名高级研究员，负责为一个研究问题撰写一份连贯的报告。"
    "你必须使用 **JSON** 格式输出结果，并严格包含以下字段：\n"
    "short_summary, markdown_report, follow_up_question。\n"
    "你将获得原始的研究问题以及由研究助理完成的初步研究内容。"
    "首先，你需要制定一份报告大纲，说明报告的结构和逻辑流程。"
    "接着，生成完整的报告并将其作为最终输出返回。"
    "最终输出应使用Markdown格式，内容应详尽且篇幅较长，目标为10到20页，至少1500字。最终结果请用中文输出"
)
writer_prompt = ChatPromptTemplate([
    ('system', WRITER_PROMPT),
    ('human', '{query}')
])
writer_chain = writer_prompt | llm.with_structured_output(ReportData)

import json
from pydantic import TypeAdapter, ValidationError
from langgraph.graph import StateGraph, MessagesState,START,END
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage

def planner_node(state: MessagesState):
    user_query = state['messages'][-1].content
    raw = planner_chain.invoke({
        'query': user_query
    })
    # 这里要注意的是 执行结果可能是WebSearchPlan类型，也可能是字典类型（被python解析了), 为了严谨性，这里加一个捕捉一场逻辑
    try:
        plan = TypeAdapter(WebSearchPlan).validate_python(raw)
    except ValidationError:
        if isinstance(raw, dict) and isinstance(raw.get('searches'), list):
            plan = WebSearchPlan(searches = [WebSearchItem(query=q, reason=r) for q,r in raw['searches']])
        else:
            raise

    return {
        # 'plan': plan, # 保存原生对象到状态中，后面节点也可以直接使用
        'messages': [AIMessage(content=plan.model_dump_json())]
    }

def search_node(state: MessagesState):
    plan_json = state["messages"][-1].content
    plan = WebSearchPlan.model_validate_json(plan_json)

    summaries = []
    for item in plan.searches:
        run = search_agent.invoke({"messages": [HumanMessage(content=item.query)]})
        msgs = run['messages']
        # 取可读内容：也就是最后一条ToolMessage 或 AIMessage的内容
        readable = next(
            (m for m in reversed(msgs) if isinstance(m,(ToolMessage, AIMessage))), msgs[-1]
        )
        summaries.append(f'## {item.query}\n\n{readable.content}')
    combined = "\n\n".join(summaries)
    return {
        'messages': [AIMessage(content=combined)]
    }

def writer_node(state: MessagesState):
    original_query = state['messages'][0].content
    combined_summary = state['messages'][-1].content

    writer_input = (
        f'原始问题: {original_query}\n\n'
        f'搜索摘要：\n{combined_summary}'
    )

    report:ReportData = writer_chain.invoke({'query': writer_input})

    return {
        'messages': [AIMessage(content=json.dumps(report.model_dump(), ensure_ascii=False, indent=2))]
    }

# 构建图
builder=StateGraph(MessagesState)
builder.add_node("planner_node", planner_node)
builder.add_node("search_node",search_node)
builder.add_node("writer_node", writer_node)

builder.add_edge(START, 'planner_node')
builder.add_edge('planner_node', 'search_node')
builder.add_edge('search_node', 'writer_node')
builder.add_edge('writer_node', END)

graph = builder.compile()