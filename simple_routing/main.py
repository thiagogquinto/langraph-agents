from graph import graph
from langchain_core.messages import HumanMessage
from rich import print
from config import langfuse_handler

if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [
                # HumanMessage(content="Valide se os produtos glifosato, atrazina são permitidos para a cultura da soja. Além disso, verifique quais as melhores regiões do Paraná para plantar soja", name="user"),
                HumanMessage(content="Quais as 10 maiores empresas de agropecuária do Paraná?", name="user"),
            ]
        },
        config={
            "callbacks": [langfuse_handler],
            "tags": ["ex4", "multi-agent"],
            "metadata": {"project": "langgraph-ex4"},
        },
    )
    print(result)