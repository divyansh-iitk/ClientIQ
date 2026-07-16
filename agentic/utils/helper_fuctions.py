from langchain_core.messages import ToolMessage
import json
from agentic.agents_state import AgentState


async def collect_tool_results_node(state: AgentState)->AgentState:
    print("collect_tool_results_node Executed")
    tool_results = {}

    for msg in state["tool_calls"]:
        if isinstance(msg, ToolMessage):
            try:
                # If your tools return JSON strings
                tool_results[msg.name] = json.loads(msg.content)
            except Exception:
                # Otherwise keep the raw string
                tool_results[msg.name] = msg.content
    return {"retrieved_data": tool_results,}



def route_after_critic(state: AgentState) -> str:
    print("Routing")
    if state["critic_report"]["approved"]:
        return "ready_for_final_report"
    if state["retry_count"] >= 2:
        return "ready_for_final_report"
    # state["retry_count"] += 1
    return "needs_more_info"