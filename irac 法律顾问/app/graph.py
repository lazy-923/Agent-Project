# app/graph.py
from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.agents.chat_agent import normal_chat_agent
# 浠庡瓙鍥惧寘涓鍏ュ悇鑷殑鏋勫缓鍑芥暟
from app.subgraphs import legal_clause, criminal_case, civil_case


# --- 璺敱閫昏緫 ---

def intent_recognition_router(state: GraphState) -> str:
    """
    椤跺眰璺敱锛氭牴鎹敤鎴烽棶棰橈紝鍐冲畾杩涘叆鍝釜瀛愬浘鎴栬妭鐐广€?
    (瀹為檯搴旂敤涓簲鏇挎崲涓篖LM璋冪敤)
    """
    print("---ROUTER: Top-Level Intent Recognition---")
    question = state["question"].lower()

    # 杩欓噷鐨勮矾鐢遍€昏緫淇濇寔涓嶅彉
    if "浣犲ソ" in question or "鍐嶈" in question:
        print("---ROUTING to normal_chat---")
        return "normal_chat"
    elif "娉曞緥" in question or "瑙勫畾" in question:
        print("---ROUTING to legal_clause_subgraph---")
        return "legal_clause_subgraph"
    else:
        print("---ROUTING to case_adjudication_router---")
        return "case_adjudication_router"

def case_adjudication_router(state: GraphState) -> str:
    """
    妗堜欢瀹″垽璺敱锛氬喅瀹氭槸杩涘叆鍒戜簨杩樻槸姘戜簨瀛愬浘銆?
    (瀹為檯搴旂敤涓簲鏇挎崲涓篖LM璋冪敤)
    """
    print("---ROUTER: Case Adjudication Type---")
    question = state["question"].lower()
    if "鐩楃獌" in question or "鏁呮剰浼ゅ" in question:
        print("---ROUTING to criminal_case_subgraph---")
        return "criminal_case_subgraph"
    else:
        print("---ROUTING to civil_case_subgraph---")
        return "civil_case_subgraph"

# --- 鏋勫缓涓诲浘 ---

def build_graph():
    """
    鏋勫缓骞惰繑鍥炰富鍥?(Top-Level Graph)銆?
    涓诲浘璐熻矗楂樼骇璺敱锛屽苟灏嗕换鍔″垎鍙戠粰涓嶅悓鐨勫瓙鍥俱€?
    """
    # 1. 鏋勫缓鎵€鏈夊瓙鍥?
    legal_clause_subgraph = build_legal_clause_graph()
    criminal_case_subgraph = build_criminal_case_graph()
    civil_case_subgraph = build_civil_case_graph()

    # 2. 鏋勫缓涓诲浘
    workflow = StateGraph(GraphState)

    # 3. 灏嗗瓙鍥惧拰鏅€氳妭鐐规坊鍔犲埌涓诲浘涓?
    workflow.add_node("normal_chat", normal_chat_agent)
    workflow.add_node("legal_clause_subgraph", legal_clause_subgraph)
    workflow.add_node("criminal_case_subgraph", criminal_case_subgraph)
    workflow.add_node("civil_case_subgraph", civil_case_subgraph)

    # 4. 璁剧疆鍏ュ彛鐐瑰拰璺敱
    workflow.set_entry_point("intent_recognition_router")

    # 5. 娣诲姞鏉′欢杈?
    workflow.add_conditional_edges(
        "intent_recognition_router",
        intent_recognition_router,
        {
            "normal_chat": "normal_chat",
            "legal_clause_subgraph": "legal_clause_subgraph",
            "case_adjudication_router": "case_adjudication_router"
        }
    )
    workflow.add_conditional_edges(
        "case_adjudication_router",
        case_adjudication_router,
        {
            "criminal_case_subgraph": "criminal_case_subgraph",
            "civil_case_subgraph": "civil_case_subgraph"
        }
    )

    # 6. 灏嗘墍鏈夌粓鐐硅繛鎺ュ埌 END
    workflow.add_edge("normal_chat", END)
    workflow.add_edge("legal_clause_subgraph", END)
    workflow.add_edge("criminal_case_subgraph", END)
    workflow.add_edge("civil_case_subgraph", END)

    # 7. 缂栬瘧涓诲浘
    app = workflow.compile()

    print("---Main Graph Compiled Successfully with Subgraphs---")
    return app
