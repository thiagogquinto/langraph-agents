"""Orquestrador de tarefas para planejamento de plantio."""

from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from states import ResearchTasks, WorkflowState
from config import llm
from workers import researcher


orchestrator_llm = llm.with_structured_output(schema=ResearchTasks)


def orchestrator(state: WorkflowState, config: RunnableConfig):
    """Decompõe solicitação de plantio em tarefas paralelas."""
    system_prompt = SystemMessage(
        content=(
            "Você é um orquestrador agrícola. Quebre a solicitação do usuário em 2 a 4 tarefas "
            "autocontidas para workers paralelos no contexto de planejamento de plantio no Paraná. "
            "Use os tipos de tarefa: cultivar, agrotoxico e web.\n\n"
            "IMPORTANTE: Informações sobre janela de plantio, cultivares, culturas e regiões do Paraná JÁ ESTÃO DISPONÍVEIS LOCALMENTE e NÃO DEVEM ser buscadas na web.\n"
            "Só crie tarefa do tipo web para assuntos realmente externos, como clima futuro, preços de mercado, notícias, riscos, pragas ou manejo que não estejam na base local.\n\n"
            "Regras:\n"
            "- Se o usuário citar região ou janelas de plantio, inclua 1 tarefa do tipo cultivar preenchendo campo regiao.\n"
            "- Se citar cultura e produtos, inclua 1 tarefa do tipo agrotoxico preenchendo cultura e produtos.\n"
            "- Inclua tarefa web apenas quando faltar contexto EXTERNO, nunca para dados já presentes na base local.\n"
            "- Cada tarefa deve ser independente e clara.\n"
            "- Retorne estritamente no schema solicitado."
        )
    )
    response = orchestrator_llm.invoke([system_prompt] + state.messages, config=config)
    return {"tasks": response.tasks}


def researcher_router(state: WorkflowState):
    return [Send("researcher", {"task": task}) for task in state.tasks]


def synthesizer(state: WorkflowState, config: RunnableConfig):
    """Consolida os outputs dos workers em resposta final."""
    reports = [
        {
            "topic": item.task.topic,
            "task_type": item.task.task_type,
            "report": item.report,
        }
        for item in state.completed_tasks
    ]

    system_prompt = SystemMessage(
        content=(
            "Você é um analista agrícola sênior. Combine os resultados em um relatório único, objetivo e acionável com base na solicitação inicial do usuário.\n"
        )
    )

    response = llm.invoke(
        [
            system_prompt,
            HumanMessage(content=f"Solicitação original: {state.messages}\n\nResultados dos workers: {json.dumps(reports, ensure_ascii=False)}"),
        ],
        config=config,
    )
    return {"final_report": response.content}


def build_graph():
    builder = StateGraph(WorkflowState)
    builder.add_node("orchestrator", orchestrator)
    builder.add_node("researcher", researcher)
    builder.add_node("synthesizer", synthesizer)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges("orchestrator", researcher_router, ["researcher"])
    builder.add_edge("researcher", "synthesizer")
    builder.add_edge("synthesizer", END)
    return builder.compile()


graph = build_graph()
