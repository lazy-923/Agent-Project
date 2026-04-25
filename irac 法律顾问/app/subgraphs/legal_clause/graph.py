# app/subgraphs/legal_clause/graph.py
from langgraph.graph import StateGraph, END
from app.state import GraphState
from .nodes import retrieve_node, generate_answer_node

def build_graph():
    """
    鏋勫缓骞惰繑鍥炴硶寰嬫潯鏂囨煡璇?(RAG) 瀛愬浘銆?
    """
    subgraph = StateGraph(GraphState)

    subgraph.add_node("retrieve", retrieve_node)
    subgraph.add_node("generate_answer", generate_answer_node)

    subgraph.set_entry_point("retrieve")
    subgraph.add_edge("retrieve", "generate_answer")
    subgraph.add_edge("generate_answer", END)

    return subgraph.compile()
