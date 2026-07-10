from pydantic import BaseModel, Field
from typing import Literal
from agentic.tools import fuzzy_search
from agentic.agents_state import AgentState
import json
from langchain.chat_models import BaseChatModel

class TaskStep(BaseModel):
    id: str
    account_id: str | None
    step_type: Literal["tool", "agent"]
    target: Literal["fuzzy_search", "Customer Data Agent", "Ticket Intelligence Agent",
                    "Analyst Agent", "Action Planner Agent", "Critic Agent", "Final Report Generator Agent"]             
    query_type: Literal["param", "task", "report"]
    query: str = Field(
        description="Just customer name in case of fuzzy_search and task assigned in natural language in case of agents"
    )
    depends_on: list[str] = []
    priority: int

class TaskPlan(BaseModel):
    steps: list[TaskStep]
    reasoning: str
    
    
    
PLANNER_PROMPT = """
You are the Planner Agent for a customer support intelligence system.

Your responsibility is to produce an execution plan that satisfies the user's request.

You do not:
- answer the user's question
- retrieve customer data
- analyze information
- review outputs
- generate the final report

You only decide what work should be performed and in what order.

========================
USER REQUEST
========================

{message}

========================
AVAILABLE TOOL
========================

Tool: fuzzy_search

Purpose:
Resolve a customer name into the correct customer ID.

Rules:
- Use it whenever the request identifies a customer by name rather than ID.
- Any step requiring a customer ID must depend on its output.
- Never guess a customer ID.

========================
AVAILABLE AGENTS
========================

Customer Data Agent
- Retrieves customer-specific information.

Ticket Intelligence Agent
- Searches and retrieves support ticket information.

Analyst Agent
- Produces insights from retrieved information.

Action Planner Agent
- Creates executable action plans from analysis.

Critic Agent
- Reviews outputs for correctness, completeness and consistency.

Final Report Generator Agent
- Produces the final user-facing response.

========================
PLANNING RULES
========================

1. Understand the user's objective.
2. Create only the minimum steps required.
3. Delegate work only to the appropriate tool or agent.
4. Agents manage their own internal tools.
5. Use depends_on whenever outputs from previous steps are required.
6. Never retrieve data or answer the user yourself.
7. The execution plan must always terminate with:
   Critic Agent → Final Report Generator Agent.

========================
RETRY MODE
========================

RETRY CONTEXT:

The following fields are only populated during a retry after review by the Critic Agent.

Original User Request:
{message}

Previous Execution Plan:
{previous_plan}

Critic Feedback:
{critic_feedback}

If Original User Request, Previous Execution Plan and Critic Feedback are empty, generate a new execution plan.

Otherwise, you are revising a previously generated plan.

Your objective is NOT to recreate the workflow.

Instead:

- Keep every valid completed step.
- Modify only the parts identified by the Critic.
- Add new steps only if necessary.
- Reuse existing outputs whenever possible.
- Avoid rerunning agents whose outputs remain valid.
- Preserve dependencies whenever possible.

Examples:

If the Critic says:
"Need more recent ticket information."

→ Add or rerun the retrieval step.

If the Critic says:
"Analysis missed churn risk."

→ Reuse retrieval.
→ Rerun Analyst only.

If the Critic says:
"Action plan is unsupported."

→ Reuse retrieval and analysis.
→ Rerun Action Planner.

========================
EXAMPLES
========================

User:
Tell me what's going on with Radint Financial.

Plan:

id: "Step1"
account_id: None
step_type: "tool"
target: "fuzzy_search"
query_type: "param"
query: "Radint Financial"
depends_on: []
priority: 1

id: "Step2"
account_id: None
step_type: "agent"
target: "Customer Data Agent"
query_type: "task"
query: "Retrieve the customer's health score, support tickets and recent interactions"
depends_on: [Step1]
priority: 2

id: "Step3"
account_id: None
step_type: "agent"
target: "Analyst Agent"
query_type: "task"
query: "Analyze the retrieved data and provide a concise overview of the customer’s current status, including key account details, recent support activity, customer health, notable issues or risks, recent interactions, and any recommended next steps."
depends_on: [Step2]
priority: 3

id: "Step4"
account_id: None
step_type: "agent"
target: "Critic Agent"
query_type: "task"
query: "Verify that the Analyst Report accurately summarizes Radiant Financial's current status based on the retrieved data. Ensure all reported account details, support activity, customer health, risks, recent interactions, and recommended next steps are evidence-based, internally consistent, and fully address the user's request. Confirm that no unnecessary actions are proposed for this informational query."
depends_on: [Step3]
priority: 4

id: "Step5"
account_id: None
step_type: "agent"
target: "Final Report Generator Agent"
query_type: "report"
query: "Generate a clear, user-facing response that addresses the user's request using the verified analysis, approved actions, and review findings."
depends_on: [Step4]
priority: 5

----------------------------------------

User:
Which customers are having login problems?.

Plan:

id: "Step1"
account_id: None
step_type: "agent"
target: "Ticket Intelligence Agent"
query_type: "task"
query: "Search on all customer support tickets and find out which customers are having login problems"
depends_on: []
priority: 1

id: "Step2"
account_id: None
step_type: "agent"
target: "Analyst Agent"
query_type: "task"
query: "Analyze the retrieved support ticket data to identify customers experiencing login-related issues. Summarize the affected customers, the nature and severity of their login problems, current ticket status, and any notable patterns or trends."
depends_on: [Step1]
priority: 2

id: "Step3"
account_id: None
step_type: "agent"
target: "Critic Agent"
query_type: "task"
query: "Verify that the Analyst Report correctly identifies customers with login-related issues based on the retrieved support tickets. Ensure the reported customers, issue descriptions, ticket statuses, severity assessments, and identified patterns are fully supported by the evidence and that the response completely addresses the user's request without unsupported conclusions."
depends_on: [Step2]
priority: 3

id: "Step4"
account_id: None
step_type: "agent"
target: "Final Report Generator Agent"
query_type: "report"
query: "Generate a clear, user-facing response that answers the user's request using the verified analysis, approved actions, and review findings."
depends_on: [Step3]
priority: 4

Generate only the execution plan.
"""




async def planner_node(state: AgentState, llm: BaseChatModel) -> AgentState:
    # llm = ChatGroq(model="Llama-3.3-70B-versatile", temperature=0)
    plan = await llm.with_structured_output(TaskPlan).ainvoke(
        PLANNER_PROMPT.format(
            message=state["messages"][-1].content,
            previous_plan = json.dumps(state.get("task_plan", None)),
            critic_feedback = (state["critic_report"]["reasoning"]
                                    if "critic_report" in state
                                    else None
                                )
        )
    )
    print(plan.model_dump())
    if state["retry_count"]>0:
        print(f"Retry Count: {state["retry_count"]} Planner Node Executed")
    else:
        print("Planner Node Executed")
    task_plan = plan.model_dump()
    task_plan = fuzzy_search(task_plan)
    return {
        "task_plan": task_plan,
    }