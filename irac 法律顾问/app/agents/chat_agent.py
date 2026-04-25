# app/agents/chat_agent.py
from app.state import GraphState

def normal_chat_agent(state: GraphState) -> dict:
    """
    澶勭悊鏅€氬璇濈殑鏅鸿兘浣撱€?
    """
    print("---AGENT: Normal Chat---")
    question = state["question"]

    # 鍦ㄨ繖閲屽疄鐜颁竴涓畝鍗曠殑瀵硅瘽閾?
    # ...

    final_answer = f"杩欐槸涓€涓櫘閫氬璇濈殑鍥炲: {question}"

    return {"final_answer": final_answer}
