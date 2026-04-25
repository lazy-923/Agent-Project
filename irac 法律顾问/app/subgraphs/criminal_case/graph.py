# app/subgraphs/criminal_case/graph.py
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState, StateGraph, START, END
from nodes import issue_node,rule_node,application_node,conclusion_node, AgentState

def build_graph():
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
    return graph

# for chunk in graph.stream({"messages":"开始","case_fact": case_fact}, stream_mode="values"):
#     chunk['messages'][-1].pretty_print()
