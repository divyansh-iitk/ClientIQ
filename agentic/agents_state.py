from typing import TypedDict, Annotated, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


def merge_retrieved_data(old: dict[str, Any], new: dict[str, Any],) -> dict[str, Any]:
    return {**old, **new}


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    tool_calls: Annotated[list[AnyMessage], add_messages]
    task_plan: dict
    retrieved_data: Annotated[dict[str, Any], merge_retrieved_data]
    analysis: dict | None
    proposed_actions: list[dict] | None
    critic_report: list[dict] | None
    hitl_decisions: list[dict]
    retry_count: int