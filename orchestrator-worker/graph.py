from orchestrator import build_graph

graph = build_graph()
graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
