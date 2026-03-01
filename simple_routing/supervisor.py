from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import MessagesState, START, END
from langgraph.types import Command
from config import llm
from langchain_core.runnables import RunnableConfig
# Define available agents
members = [
    "web_search",
    "colheita"
]
# Add FINISH as an option for task completion
options = members + ["FINISH"]

# Create system prompt for supervisor
system_prompt = (
    "Você é um supervisor agrícola responsável por rotear tarefas para dois agentes especializados:\n"
    "1. COLHEITA - especialista em planejamento agrícola que pode:\n"
    "   - Listar cultivares apropriadas por região\n"
    "   - Validar agrotoxicos permitidos para cada cultura\n"
    "   USE ESTE AGENTE para: perguntas sobre cultivares, regiões, agrotoxicos, produtos químicos permitidos\n"
    "2. WEB_SEARCH - especialista em pesquisa na internet\n"
    "   USE ESTE AGENTE para: informações gerais que precisam de pesquisa na web\n"
    "\n"
    "Dado o pedido do usuário, escolha qual agente deve responder:\n"
    "- Se for sobre agrotoxicos, cultivares ou regiões → use COLHEITA\n"
    "- Se for pesquisa geral na internet → use WEB_SEARCH\n"
    "- Assim que obter os dados necessários para responder a solicitação → responda FINISH\n"
)

# Define router type for structured output
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["web_search", "colheita", "FINISH"]

# Create supervisor node function
def supervisor_node(state: MessagesState, config: RunnableConfig) -> Command[Literal["web_search", "colheita", "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages, config=config)
    goto = response["next"]
    print(f"Next Worker: {goto}")
    if goto == "FINISH":
        goto = END
    return Command(goto=goto)
