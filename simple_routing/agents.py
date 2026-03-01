from typing import Literal, Sequence, Annotated, TypedDict
from langgraph.types import Command
from langgraph.graph import StateGraph, add_messages, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from pathlib import Path
import sys
from rich import print
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from config import llm
from langchain_core.runnables import RunnableConfig

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]

def create_agent(llm, tools):
    llm_with_tools = llm.bind_tools(tools)
    def chatbot(state: AgentState, config: RunnableConfig):
        return {"messages": [llm_with_tools.invoke(state["messages"], config=config)]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )
    graph_builder.add_edge("tools", "agent")
    graph_builder.set_entry_point("agent")
    final_graph = graph_builder.compile()
    final_graph.get_graph().draw_mermaid_png(output_file_path="agent_graph.png")
    return final_graph

SERVER_PATH = Path(__file__).with_name("mcp_server.py")

client = MultiServerMCPClient(
    {
        "prototipo": {
            "command": sys.executable,
            "args": [str(SERVER_PATH)],
            "transport": "stdio",
        }
    }
)

tools = asyncio.run(client.get_tools(server_name="prototipo"))

TOOLS_BY_NAME = {tool.name: tool for tool in tools}

websearch_agent = create_agent(
    llm=llm,
    tools=[TOOLS_BY_NAME['web_search']]
)
async def web_search_node_async(state: MessagesState, config: RunnableConfig) -> Command[Literal["supervisor"]]:
    result = await websearch_agent.ainvoke(state, config=config)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="web_researcher")
            ]
        },
        goto="supervisor",
    )

def web_search_node(state: MessagesState, config: RunnableConfig) -> Command[Literal["supervisor"]]:
    return asyncio.run(web_search_node_async(state, config))


colheita_agent = create_agent(
    llm=llm,
    tools=[TOOLS_BY_NAME['listar_cultivares_por_regiao'], TOOLS_BY_NAME['validar_agrotoxicos_permitidos']]
)
async def colheita_node_async(state: MessagesState, config: RunnableConfig) -> Command[Literal["supervisor"]]:
    result = await colheita_agent.ainvoke(state, config=config)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="colheita")
            ]
        },
        goto="supervisor",
    )

def colheita_node(state: MessagesState, config: RunnableConfig) -> Command[Literal["supervisor"]]:
    return asyncio.run(colheita_node_async(state, config))

