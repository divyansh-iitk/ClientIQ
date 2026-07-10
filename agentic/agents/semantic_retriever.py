from agentic.agents_state import AgentState
from agentic.tools import semantic_retriever

async def semantic_retriever_node(state: AgentState) -> AgentState:
    step = next(
        (s for s in state["task_plan"]["steps"]
        if s["target"] == "Ticket Intelligence Agent"),
        None,
    )
    
    if step:
        if state["retry_count"]>0:
            print(f"Retry Count: {state["retry_count"]} Semantic Retriever Node Executed")
        else:
            print("Semantic Retriever Node Executed")
        query = step["query"]
        tool_result = await semantic_retriever.ainvoke(query)
        retrieved_data = dict(state.get("retrieved_data", {}))
        retrieved_data["semantic_retriever"] = tool_result
        return {"retrieved_data": retrieved_data,}