from fastapi import APIRouter, Depends, HTTPException
from langchain.messages import HumanMessage
from agentic.agents_state import AgentState
from backend.api.schemas.endpoints import AgentResponse
from agentic.graph import graph

router = APIRouter()

@router.get(
    "/chat/{user_query}/query",
    response_model=AgentResponse
)
async def agent_response(user_query: str):
    state = AgentState(
    {"messages": [
        HumanMessage(content=user_query)
    ],
     "retry_count": 0})
    try:
        response = await graph.ainvoke(state)
        ai_response = response["messages"][-1]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate response: {e}"
        )
    return {
        "response": ai_response
        }