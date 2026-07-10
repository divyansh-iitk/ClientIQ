from enum import IntEnum
from typing import Literal, Annotated, Union
from langchain.chat_models import BaseChatModel
from pydantic import BaseModel, Field, EmailStr
from agentic.agents_state import AgentState
import json

class ReversibilityTier(IntEnum):
    FULLY_REVERSIBLE = 1   # drafts, internal notes — essentially free to undo
    SEMI_REVERSIBLE = 2    # status changes, deal stage updates — undoable but has side effects
    IRREVERSIBLE = 3       # sending an email, charging a card — cannot be undone

class ActionBase(BaseModel):
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str                              # why the agent thinks this is the right action
    reversibility_tier: ReversibilityTier
    requires_approval: bool = True               # default-safe; only set False deliberately, if ever

class DraftEmailAction(ActionBase):
    action_type: Literal["draft_email"] = "draft_email"
    reversibility_tier: ReversibilityTier = ReversibilityTier.FULLY_REVERSIBLE
    to_email: list[EmailStr]
    subject: str
    body: str

class UpdateTicketAction(ActionBase):
    action_type: Literal["update_ticket"] = "update_ticket"
    reversibility_tier: ReversibilityTier = ReversibilityTier.SEMI_REVERSIBLE
    ticket_id: str
    new_status: str
    internal_note: str | None = None

# the discriminated union: Pydantic uses "action_type" to know which class to validate against
AnyAction = Annotated[
    Union[DraftEmailAction, UpdateTicketAction],
    Field(discriminator="action_type"),
]

class ActionPlan(BaseModel):
    actions: list[AnyAction]
    
    
    
    
ACTION_PROMPT = """
You are the Action Planner Agent for a customer support intelligence system.

Your job is to determine what actions, if any, should be proposed based on:
1. The task assigned to you by the Planner.
2. The user's original request.
3. The Analyst Report.

Task:
{task}

User Request:
{user_query}

Analyst Report:
{analysis}

Responsibilities:
- Carefully follow the Planner's task.
- Review the Analyst Report and identify actions that are fully supported by the evidence.
- Only propose actions that help satisfy the user's request.
- If the Planner's task indicates that no actions are required, return an empty action list.
- If the available evidence is insufficient, do not guess or fabricate information. Return no actions.
- Never perform additional analysis beyond what is present in the Analyst Report.
- Never retrieve additional data.
- Never execute any action.
- Never communicate directly with the end user.

Action Planning Guidelines:
- Prefer the least disruptive action that satisfies the user's request.
- Do not propose redundant or conflicting actions.
- Do not propose actions that cannot be justified by the Analyst Report.

Output Requirements:
- Return ONLY valid structured output matching the provided Action schema.
- Do not include explanations outside the schema.
- If no action is appropriate, return an empty list.
"""



async def action_plan_node(state: AgentState, llm: BaseChatModel) -> AgentState:
    step = next(
        (s for s in state["task_plan"]["steps"]
        if s["target"] == "Action Planner Agent"),
        None,
    )
    if step:
        if state["retry_count"]>0:
            print(f"Retry Count: {state["retry_count"]} Action Plan Node Executed")
        else:
            print("Action Plan Node Executed")
        # llm = ChatGroq(model="Llama-3.3-70B-versatile", temperature=0)
        report = await llm.with_structured_output(ActionPlan).ainvoke(
            ACTION_PROMPT.format(analysis=json.dumps(state["analysis"]),
                                  task=step["query"],
                                  user_query=state["messages"][0].content)
        )
        return {"proposed_actions": report.model_dump(),}