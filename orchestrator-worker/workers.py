from __future__ import annotations


from states import (
    CompletedTask,
    WorkerState,
    WorkerTask,
)

import json
import sys
from pathlib import Path
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


# Configuração do MCP Client
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

async def chamar_tool(tool_name, **kwargs):
    tool = TOOLS_BY_NAME[tool_name]
    return await tool.ainvoke(kwargs)


def researcher(state: WorkerState | dict):
    raw_task = state["task"] if isinstance(state, dict) else state.task
    task = raw_task if isinstance(raw_task, WorkerTask) else WorkerTask.model_validate(raw_task)

    async def run():
        if task.task_type == "cultivar":
            # Chama tool do MCP Server
            result = await chamar_tool("listar_cultivares_por_regiao", regiao=task.regiao or "")
        elif task.task_type == "agrotoxico":
            result = await chamar_tool(
                "validar_agrotoxicos_permitidos",
                cultura=task.cultura or "",
                produtos=", ".join(task.produtos or [])
            )
        else:
            result = await chamar_tool(
                "web_search",
                query=task.search_query or task.task
            )
        return result

    result = asyncio.run(run())
    # Garante que report seja sempre string
    if isinstance(result, str):
        report = result
    else:
        try:
            report = json.dumps(result, ensure_ascii=False, indent=2)
        except Exception:
            report = str(result)
    completed_task = CompletedTask(task=task, report=report)
    return {"completed_tasks": [completed_task]}
