from langchain.chat_models import BaseChatModel
from agentic.agents_state import AgentState
from agentic.tools import get_customer_profile, get_ticket_data


tools=[get_customer_profile, get_ticket_data]


RETRIEVER_PROMPT="""
You are the Retriever Agent for a customer support intelligence system.
Your job is to perform the task given by the Planner Agent and call specific tools to give structured output.
You can also use context from the user's query.
Task:
{task}

Account ID: 
{account_id}

User Query:
{user_query}
"""



async def retrieval_node(state: AgentState, llm: BaseChatModel) -> AgentState:
    # llm = ChatGroq(model="Llama-3.3-70B-versatile", temperature=0)
    step = next(
        (s for s in state["task_plan"]["steps"]
        if s["target"] == "Customer Data Agent"),
        None,
    )
    if step:
        if state["retry_count"]>0:
            print(f"Retry Count: {state["retry_count"]} Data retriver node Executed")
        else:
            print("Data retriver node Executed")
        plan = await llm.bind_tools(tools).ainvoke(RETRIEVER_PROMPT.format(
                        task=step["query"],
                        account_id=step["account_id"],
                        user_query=state["messages"][0].content
                    ))
        return {"tool_calls": [plan],}