from functools import partial
from langgraph.graph import StateGraph
from agentic.agents_state import AgentState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from agentic.tools import get_customer_profile, get_ticket_data
from agentic.agents import (planner, retriever, semantic_retriever,
                            analyst, action_planner, critic, report_gen)
from agentic.utils.helper_fuctions import collect_tool_results_node, route_after_critic
from agentic.llms_for_agents import LLMsForAgents

tools=[get_customer_profile, get_ticket_data]
llms = LLMsForAgents()

builder = StateGraph(AgentState)
builder.add_node("planner", partial(planner.planner_node, llm=llms.planner_llm))
builder.add_node("customer_data_retriever", partial(retriever.retrieval_node, llm=llms.retriever_llm))
builder.add_node("semantic_retriever", semantic_retriever.semantic_retriever_node)
builder.add_node("tools",ToolNode(tools, messages_key="tool_calls"))
builder.add_node("collect_tool_result", collect_tool_results_node)
builder.add_node("analyst", partial(analyst.analyst_node, llm=llms.analyst_llm))
builder.add_node("action_planner", partial(action_planner.action_plan_node, llm=llms.action_plan_llm))
builder.add_node("critic", partial(critic.critic_node, llm=llms.critic_llm))
builder.add_node("final_report_node", partial(report_gen.final_report_node, llm=llms.report_gen_llm))

builder.set_entry_point("planner")
builder.add_edge("planner", "customer_data_retriever")
builder.add_edge("planner", "semantic_retriever")
builder.add_conditional_edges(
    "customer_data_retriever",
    lambda state: tools_condition(state, messages_key="tool_calls"),
    {
        "tools": "tools",
    },
)
builder.add_edge("tools", "collect_tool_result")
builder.add_edge(["semantic_retriever", "collect_tool_result"], "analyst")
builder.add_edge("analyst", "action_planner")
builder.add_edge("action_planner", "critic")
builder.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "ready_for_final_report": "final_report_node",
        "needs_more_info": "planner",
    },
)

## compile the graph
graph=builder.compile()

if __name__ == "__main__":
    png = graph.get_graph().draw_mermaid_png()

    with open("graph.png", "wb") as f:
        f.write(png)

    print("Graph saved to graph.png")