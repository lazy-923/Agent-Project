# app/subgraphs/legal_clause/nodes.py
from app.state import GraphState
from app.utils.retriever import get_retriever

def retrieve_node(state: GraphState) -> dict:
    """
    鑺傜偣1: 浠庡悜閲忔暟鎹簱妫€绱㈡枃妗ｃ€?
    """
    print("---SUBGRAPH (RAG): Retrieving Documents---")
    question = state["question"]

    retriever = get_retriever()
    documents = retriever.invoke(question)

    return {"retrieved_documents": documents}

def generate_answer_node(state: GraphState) -> dict:
    """
    鑺傜偣2: 鍩轰簬妫€绱㈠埌鐨勬枃妗ｇ敓鎴愮瓟妗堛€?
    """
    print("---SUBGRAPH (RAG): Generating Answer---")
    question = state["question"]
    documents = state["retrieved_documents"]

    final_answer = (
        f"鍏充簬 '{question}' 鐨勬硶寰嬭瀹氬涓嬶細\n"
        f"- {documents[0]}\n"
        f"- {documents[1]}\n"
        f"(浠ヤ笂鍐呭鐢盧AG绯荤粺鐢熸垚)"
    )
    return {"final_answer": final_answer}
