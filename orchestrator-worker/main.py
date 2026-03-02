from langchain_core.messages import HumanMessage

from states import WorkflowState
from config import langfuse_handler
from graph import graph


def main():
	while True:
		user_input = input("Digite o pedido (ou 'sair' para encerrar): ")
		if user_input.strip().lower() == "sair":
			break
		input_state = WorkflowState(
			messages=[
				HumanMessage(content=user_input)
			]
		)
		output = graph.invoke(
			input_state,
			config={
				"callbacks": [langfuse_handler],
				"tags": ["orchestrator-worker", "plantio"],
				"metadata": {"project": "langgraph-orchestrator-worker"},
			},
		)
		print("\n--- RESPOSTA FINAL ---")
		print(output.get("final_report", "Sem relatório final."))
		print("\n======================\n")


if __name__ == "__main__":
	main()
