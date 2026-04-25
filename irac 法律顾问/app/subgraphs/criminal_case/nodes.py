from prompts import issue_prompt, rule_prompt, application_prompt, conlusion_prompt,case_fact
from typing import List, Optional
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
import os
import dotenv
dotenv.load_dotenv()

llm = init_chat_model(
    model='qwen3-max',
    model_provider='openai',
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url=os.getenv('DASHSCOPE_BASE_URL'),
)


class IssueSchema(BaseModel):
    """璁璇嗗埆杈撳嚭妯″瀷"""
    legal_domains: List[str] = Field(description='娑夊強鐨勬硶寰嬮鍩熷垪琛?)
    core_legal_issues: List[str] = Field(description='鏍稿績娉曞緥璁鍒楄〃')
    issues_relationship: str = Field('绠€瑕佽鏄庡悇璁涔嬮棿鐨勯€昏緫鍏崇郴')
    clarification_needed: Optional[List[str]] = Field("闇€瑕佹緞娓呯殑浜嬪疄鐐?)


class LegalRule(BaseModel):
    """娉曞緥瑙勫垯妯″瀷"""
    rule_text: str = Field(description="瑙勫垯鏂囨湰")
    source: str = Field(description="鍑哄锛堟硶鏉℃垨妗堜緥锛?)
    elements: List[str] = Field(description="鏋勬垚瑕佷欢鍒楄〃")
    explanation: str = Field(description="瑙勫垯瑙ｉ噴")


class IssueRules(BaseModel):
    """璁瀵瑰簲鐨勮鍒?""
    issue: str = Field(description="璁鍘熸枃")
    relevant_rules: List[LegalRule] = Field(description="鐩稿叧娉曞緥瑙勫垯")


class RuleSchema(BaseModel):
    """瑙勫垯妫€绱㈣緭鍑烘ā鍨?""
    rules_by_issue: List[IssueRules] = Field(description="鎸夎棰樼粍缁囩殑瑙勫垯")


class ElementApplication(BaseModel):
    """瑕佷欢閫傜敤鍒嗘瀽"""
    element: str = Field(description="娉曞緥瑕佷欢")
    fact_linkage: str = Field(description="浜嬪疄閾炬帴")
    plaintiff_argument: str = Field(description="鍘熷憡鏂硅璇?)
    defendant_argument: str = Field(description="琚憡鏂硅璇?)
    strength_score: float = Field(description="璁鸿瘉寮哄害璇勫垎", ge=0.0, le=1.0)
    preliminary_conclusion: str = Field(description="鍒濇缁撹")


class RuleApplication(BaseModel):
    """瑙勫垯閫傜敤鍒嗘瀽"""
    rule: str = Field(description="閫傜敤鐨勮鍒?)
    elements_application: List[ElementApplication] = Field(description="瑕佷欢閫傜敤鍒嗘瀽")
    overall_analysis: str = Field(description="鏁翠綋鍒嗘瀽")


class IssueApplication(BaseModel):
    """璁閫傜敤鍒嗘瀽"""
    issue: str = Field(description="璁鏂囨湰")
    analysis: List[RuleApplication] = Field(description="瑙勫垯閫傜敤鍒嗘瀽鍒楄〃")
    key_disputes: List[str] = Field(description="涓昏浜夎鐐?)


class ApplicationSchema(BaseModel):
    """閫傜敤鍒嗘瀽杈撳嚭妯″瀷"""
    application_by_issue: List[IssueApplication] = Field(description="鎸夎棰樼粍缁囩殑閫傜敤鍒嗘瀽")
    conflicting_interpretations: str = Field(description="鍐茬獊瑙ｉ噴鎽樿")


class JudicialReasoning(BaseModel):
    """瑁佸喅鐞嗙敱"""
    issue: str = Field(description="璁鏂囨湰")
    ruling: str = Field(description="瑁佸喅缁撴灉锛堟垚绔?涓嶆垚绔嬶級")
    reasoning: str = Field(description="璇︾粏鐨勮鍐崇悊鐢?)
    key_facts: List[str] = Field(description="鍏抽敭浜嬪疄")
    key_legal_principles: List[str] = Field(description="鍏抽敭娉曞緥鍘熷垯")


class ConclusionSchema(BaseModel):
    """缁撹杈撳嚭妯″瀷"""
    case_title: str = Field(description="妗堜欢鍚嶇О")
    key_facts_summary: str = Field(description="鍏抽敭浜嬪疄鎽樿")
    judicial_reasoning: List[JudicialReasoning] = Field(description="瑁佸喅鐞嗙敱鍒楄〃")
    final_judgment: str = Field(description="鏈€缁堝垽鍐?)
    potential_appeal_points: List[str] = Field(description="娼滃湪涓婅瘔鐐?)
    confidence_score: float = Field(description="缃俊搴﹁瘎鍒?, ge=0.0, le=1.0)
    recommendations: List[str] = Field(description="寤鸿")


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
            ('human', "璇峰熀浜庝互涓嬫浠朵簨瀹炶繘琛岃棰樿瘑鍒細\n{case_fact}")
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
            ('human', '妗堜欢浜嬪疄:{case_fact}\n璇嗗埆鍑虹殑娉曞緥璁:{issues_summary}')
        ])
        chain = prompt | llm.with_structured_output(RuleSchema)
        response = chain.invoke({'case_fact': state['case_fact'], 'issues_summary': issues_summary})
        rules = response
        rules_summary = ""
        if rules and rules.rules_by_issue:
            for issue_rules in rules.rules_by_issue:
                rules_summary += f"\n璁: {issue_rules.issue}\n"
                for rule in issue_rules.relevant_rules:
                    rules_summary += f"  -瑙勫垯闄堣堪锛歿rule.rule_text}\n  -鍑哄: {rule.source}\n  -瑕佷欢鍒楄〃锛歿rule.elements}\n  -瑙勫垯瑙ｉ噴锛歿rule.explanation}\n\n"
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
            ('human', '妗堜欢浜嬪疄:{case_fact}\n鐩稿叧娉曞緥璁鍜屽搴旇鍒欒鍒?{rules_summary}'),
        ])
        chain = prompt | llm.with_structured_output(ApplicationSchema)
        response = chain.invoke({'case_fact': state['case_fact'], 'rules_summary': rules_summary})
        application = response
        application_summary = ""
        if application and application.application_by_issue:
            for issue_app in application.application_by_issue:
                application_summary += f"\n璁: {issue_app.issue}\n"
                for analysis in issue_app.analysis:
                    application_summary += f"  -瑙勫垯: {analysis.rule}\n  -瑙勫垯閫傜敤鐨勬暣浣撳垎鏋愶細 {analysis.overall_analysis}\n\n"
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
            ('human', f'妗堜欢浜嬪疄:{case_fact}\n娉曞緥閫傜敤鍒嗘瀽:{application_summary}')
        ])
        chain = prompt | llm.with_structured_output(ConclusionSchema)
        response = chain.invoke({'case_fact': state['case_fact'], 'application_summary': application_summary})
        return {
            'messages': [AIMessage(content=response.final_judgment)],
            'conclusion': response,
            'current_step': 'conclusion_complete',
        }

def issue_node(state: AgentState):
    print("馃攳 姝ｅ湪鎵ц璁璇嗗埆...")
    agent = IssueAgent()
    return agent.invoke(state)


def rule_node(state: AgentState):
    print("馃摎 姝ｅ湪妫€绱㈡硶寰嬭鍒?..")
    agent = RuleAgent()
    return agent.invoke(state)


def application_node(state: AgentState):
    print("鈿栵笍 姝ｅ湪杩涜娉曞緥閫傜敤鍒嗘瀽...")
    agent = ApplicationAgent()
    return agent.invoke(state)


def conclusion_node(state: AgentState):
    print("馃彌锔?姝ｅ湪璧疯崏鏈€缁堢粨璁?..")
    agent = ConclusionAgent()
    return agent.invoke(state)
