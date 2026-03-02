from __future__ import annotations

import json
import operator
from typing import Annotated, Literal

from langgraph.graph import add_messages
from pydantic import BaseModel, Field

class WorkerTask(BaseModel):
	topic: str
	task_type: Literal["cultivar", "agrotoxico", "web"]
	task: str
	search_query: str | None = None
	regiao: str | None = None
	cultura: str | None = None
	produtos: list[str] = Field(default_factory=list)


class ResearchTasks(BaseModel):
	tasks: list[WorkerTask] = Field(default_factory=list)


class CompletedTask(BaseModel):
	task: WorkerTask
	report: str


class WorkflowState(BaseModel):
	messages: Annotated[list, add_messages] = Field(default_factory=list)
	tasks: list[WorkerTask] = Field(default_factory=list)
	completed_tasks: Annotated[list[CompletedTask], operator.add] = Field(default_factory=list)
	final_report: str | None = None


class WorkerState(BaseModel):
	task: WorkerTask
	completed_tasks: Annotated[list[CompletedTask], operator.add] = Field(default_factory=list)


def normalizar(texto: str) -> str:
	return (texto or "").strip().lower()


def to_json(data: dict) -> str:
	return json.dumps(data, ensure_ascii=False, indent=2)
