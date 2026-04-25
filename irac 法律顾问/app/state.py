from typing import List, TypedDict, Optional

class GraphState(TypedDict):
    """
    图的共享状态。
    Attributes:
        question: 用户的原始问题
        chat_history: 对话历史
        intent: 识别出的用户意图
        case_type: 如果是案件审判，案件的类型 (criminal 或 civil)
        retrieved_documents: RAG检索到的文档
        analysis_result: 案件分析的结果
        final_answer: 最终生成给用户的答案
    """
    question: str
    chat_history: Optional[List[tuple[str, str]]] = None
    intent: str
    case_type: Optional[str] = None
    retrieved_documents: Optional[List[str]] = None
    analysis_result: Optional[str] = None
    final_answer: str

    case_facts: Optional[dict] = None
    element_analysis: Optional[dict] = None