# app/subgraphs/civil_case/nodes.py
from app.state import GraphState

def analyze_legal_relation_node(state: GraphState) -> dict:
    """
    鑺傜偣1: 鍒嗘瀽褰撲簨浜轰箣闂寸殑娉曞緥鍏崇郴銆?
    """
    print("---SUBGRAPH (Civil): Analyzing Legal Relation---")
    question = state["question"]
    relation = "鍚堝悓鍏崇郴" if "鍚堝悓" in question else "渚垫潈鍏崇郴"
    return {"case_facts": {"relation": relation, "details": question}}

def analyze_claim_basis_node(state: GraphState) -> dict:
    """
    鑺傜偣2: 鍒嗘瀽璇锋眰鏉冨熀纭€銆?
    """
    print("---SUBGRAPH (Civil): Analyzing Claim Basis---")
    facts = state["case_facts"]
    analysis = {
        "璇锋眰鏉冨熀纭€": "鍒嗘瀽涓?..",
        "璇夎璇锋眰": "鍒嗘瀽涓?..",
    }
    return {"element_analysis": analysis}

def synthesize_result_node(state: GraphState) -> dict:
    """
    鑺傜偣3: 缁煎悎淇℃伅锛屽舰鎴愭渶缁堢粨璁恒€?
    """
    print("---SUBGRAPH (Civil): Synthesizing Result---")
    facts = state["case_facts"]
    analysis = state["element_analysis"]

    final_answer = (
        f"姘戜簨妗堜欢鍒嗘瀽鎶ュ憡锛歕n"
        f"1. 娉曞緥鍏崇郴鍒嗘瀽: {facts['relation']}\n"
        f"2. 璇锋眰鏉冨熀纭€鍒嗘瀽: {analysis}\n"
        f"缁撹: (杩欐槸涓€涓患鍚堢粨璁?..)"
    )
    return {"final_answer": final_answer}
