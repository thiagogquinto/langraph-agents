from langgraph.graph import StateGraph, add_messages, MessagesState, START, END
from agents import colheita_node, web_search_node
from supervisor import supervisor_node
from langchain_core.messages import HumanMessage
from rich import print
builder = StateGraph(MessagesState)

builder.add_node("supervisor", supervisor_node)
builder.add_node("web_search", web_search_node)
builder.add_node("colheita", colheita_node)
builder.add_edge(START, "supervisor")
graph = builder.compile()
graph.get_graph().draw_mermaid_png(output_file_path="graph.png")