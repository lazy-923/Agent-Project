# app/subgraphs/civil_case/graph.py
from langgraph.graph import StateGraph, END
from app.state import GraphState
from .nodes import (
    analyze_legal_relation_node,
    analyze_claim_basis_node,
    synthesize_result_node,
)

def build_graph():
    """
    鏋勫缓骞惰繑鍥炴皯浜嬫浠跺垎鏋愬瓙鍥俱€?
    """
    subgraph = StateGraph(GraphState)

    subgraph.add_node("analyze_legal_relation", analyze_legal_relation_node)
    subgraph.add_node("analyze_claim_basis", analyze_claim_basis_node)
    subgraph.add_node("synthesize_result", synthesize_result_node)

    subgraph.set_entry_point("analyze_legal_relation")
    subgraph.add_edge("analyze_legal_relation", "analyze_claim_basis")
    subgraph.add_edge("analyze_claim_basis", "synthesize_result")
    subgraph.add_edge("synthesize_result", END)

    return subgraph.compile()
