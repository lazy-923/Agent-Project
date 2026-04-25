from prompts import issue_prompt, rule_prompt, application_prompt, conlusion_prompt,case_fact
from typing import List, Optional
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
import os
import dotenv

dotenv.load_dotenv()

llm = init_chat_model(
    model='qwen3-max',
    api_key=os.getenv('API_KEY'),
    base_url=os.getenv('BASE_URL'),
)


class IssueSchema(BaseModel):
    """议题识别输出模型"""
    legal_domains: List[str] = Field(description='涉及的法律领域列表')
    core_legal_issues: List[str] = Field(description='核心法律议题列表')
    issues_relationship: str = Field('简要说明各议题之间的逻辑关系')
    clarification_needed: Optional[List[str]] = Field("需要澄清的事实点")


class LegalRule(BaseModel):
    """法律规则模型"""
    rule_text: str = Field(description="规则文本")
    source: str = Field(description="出处（法条或案例）")
    elements: List[str] = Field(description="构成要件列表")
    explanation: str = Field(description="规则解释")


class IssueRules(BaseModel):
    """议题对应的规则"""
    issue: str = Field(description="议题原文")
    relevant_rules: List[LegalRule] = Field(description="相关法律规则")


class RuleSchema(BaseModel):
    """规则检索输出模型"""
    rules_by_issue: List[IssueRules] = Field(description="按议题组织的规则")


class ElementApplication(BaseModel):
    """要件适用分析"""
    element: str = Field(description="法律要件")
    fact_linkage: str = Field(description="事实链接")
    plaintiff_argument: str = Field(description="原告方论证")
    defendant_argument: str = Field(description="被告方论证")
    strength_score: float = Field(description="论证强度评分", ge=0.0, le=1.0)
    preliminary_conclusion: str = Field(description="初步结论")


class RuleApplication(BaseModel):
    """规则适用分析"""
    rule: str = Field(description="适用的规则")
    elements_application: List[ElementApplication] = Field(description="要件适用分析")
    overall_analysis: str = Field(description="整体分析")


class IssueApplication(BaseModel):
    """议题适用分析"""
    issue: str = Field(description="议题文本")
    analysis: List[RuleApplication] = Field(description="规则适用分析列表")
    key_disputes: List[str] = Field(description="主要争议点")


class ApplicationSchema(BaseModel):
    """适用分析输出模型"""
    application_by_issue: List[IssueApplication] = Field(description="按议题组织的适用分析")
    conflicting_interpretations: str = Field(description="冲突解释摘要")


class JudicialReasoning(BaseModel):
    """裁决理由"""
    issue: str = Field(description="议题文本")
    ruling: str = Field(description="裁决结果（成立/不成立）")
    reasoning: str = Field(description="详细的裁决理由")
    key_facts: List[str] = Field(description="关键事实")
    key_legal_principles: List[str] = Field(description="关键法律原则")


class ConclusionSchema(BaseModel):
    """结论输出模型"""
    case_title: str = Field(description="案件名称")
    key_facts_summary: str = Field(description="关键事实摘要")
    judicial_reasoning: List[JudicialReasoning] = Field(description="裁决理由列表")
    final_judgment: str = Field(description="最终判决")
    potential_appeal_points: List[str] = Field(description="潜在上诉点")
    confidence_score: float = Field(description="置信度评分", ge=0.0, le=1.0)
    recommendations: List[str] = Field(description="建议")


class AgentState(MessagesState):
    case_fact: str
    issues: List[IssueSchema]
    rules: List[RuleSchema]
    application: Optional[ApplicationSchema]
    conclusion: Optional[ConclusionSchema]
    current_step: str


class IssueAgent:
    def __init__(self):
        self.llm = llm
        self.system_prompt = issue_prompt

    def invoke(self, state: AgentState):
        prompt = ChatPromptTemplate([
            ('system', self.system_prompt),
            ('human', "请基于以下案件事实进行议题识别：\n{case_fact}")
        ])
        chain = prompt | llm.with_structured_output(IssueSchema)
        response = chain.invoke({'case_fact': state['case_fact']})
        issues = response
        issues_summary = ""
        if issues and issues.core_legal_issues:
            for issue in issues.core_legal_issues:
                issues_summary += f"- {issue}\n"
        return {
            'messages': [AIMessage(content=issues_summary)],
            'issues': response,
            'current_step': 'issue_complete',
        }


class RuleAgent:
    def __init__(self):
        self.llm = llm
        self.system_prompt = rule_prompt

    def invoke(self, state: AgentState):
        issues_summary = state["messages"][-1].content
        prompt = ChatPromptTemplate([
            ('system', self.system_prompt),
            ('human', '案件事实:{case_fact}\n识别出的法律议题:{issues_summary}')
        ])
        chain = prompt | llm.with_structured_output(RuleSchema)
        response = chain.invoke({'case_fact': state['case_fact'], 'issues_summary': issues_summary})
        rules = response
        rules_summary = ""
        if rules and rules.rules_by_issue:
            for issue_rules in rules.rules_by_issue:
                rules_summary += f"\n议题: {issue_rules.issue}\n"
                for rule in issue_rules.relevant_rules:
                    rules_summary += f"  -规则陈述：{rule.rule_text}\n  -出处: {rule.source}\n  -要件列表：{rule.elements}\n  -规则解释：{rule.explanation}\n\n"
        return {
            "messages": [AIMessage(content=rules_summary)],
            "rules": response,
            "current_step": "rule_research_complete",
        }


class ApplicationAgent:
    def __init__(self):
        self.llm = llm
        self.system_prompt = application_prompt

    def invoke(self, state: AgentState):
        rules_summary = state["messages"][-1].content
        prompt = ChatPromptTemplate([
            ('system', self.system_prompt),
            ('human', '案件事实:{case_fact}\n相关法律议题和对应规则规则:{rules_summary}'),
        ])
        chain = prompt | llm.with_structured_output(ApplicationSchema)
        response = chain.invoke({'case_fact': state['case_fact'], 'rules_summary': rules_summary})
        application = response
        application_summary = ""
        if application and application.application_by_issue:
            for issue_app in application.application_by_issue:
                application_summary += f"\n议题: {issue_app.issue}\n"
                for analysis in issue_app.analysis:
                    application_summary += f"  -规则: {analysis.rule}\n  -规则适用的整体分析： {analysis.overall_analysis}\n\n"
        return {
            'messages': [AIMessage(content=application_summary)],
            "application": response,
            "current_step": "application_research_complete",
        }


class ConclusionAgent:
    def __init__(self):
        self.llm = llm
        self.system_prompt = conlusion_prompt

    def invoke(self, state: AgentState):
        application_summary = state["messages"][-1].content
        prompt = ChatPromptTemplate([
            ('system', self.system_prompt),
            ('human', f'案件事实:{case_fact}\n法律适用分析:{application_summary}')
        ])
        chain = prompt | llm.with_structured_output(ConclusionSchema)
        response = chain.invoke({'case_fact': state['case_fact'], 'application_summary': application_summary})
        return {
            'messages': [AIMessage(content=response.final_judgment)],
            'conclusion': response,
            'current_step': 'conclusion_complete',
        }


def issue_node(state: AgentState):
    print("🔍 正在执行议题识别...")
    agent = IssueAgent()
    return agent.invoke(state)


def rule_node(state: AgentState):
    print("📚 正在检索法律规则...")
    agent = RuleAgent()
    return agent.invoke(state)


def application_node(state: AgentState):
    print("⚖️ 正在进行法律适用分析...")
    agent = ApplicationAgent()
    return agent.invoke(state)


def conclusion_node(state: AgentState):
    print("🏛️ 正在起草最终结论...")
    agent = ConclusionAgent()
    return agent.invoke(state)


builder = StateGraph(AgentState)
builder.add_node('issue_node', issue_node)
builder.add_node('rule_node', rule_node)
builder.add_node('application_node', application_node)
builder.add_node('conclusion_node', conclusion_node)
builder.add_edge(START, 'issue_node')
builder.add_edge('issue_node', 'rule_node')
builder.add_edge('rule_node', 'application_node')
builder.add_edge('application_node', 'conclusion_node')
builder.add_edge('conclusion_node', END)
graph = builder.compile()
