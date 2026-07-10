from typing import Literal
from langchain.chat_models import BaseChatModel
from pydantic import BaseModel, Field
from agentic.agents_state import AgentState
import json


class Evidence(BaseModel):
    source: Literal[
        "customer_profile",
        "tickets",
        "usage_events",
        "billing",
        "subscription",
        "semantic_documents",
        "other",
    ]
    reference: str = Field(
        description="Unique identifier of the source (ticket id, document id, invoice id, etc.)"
    )
    summary: str = Field(
        description="Relevant fact extracted from the source."
    )


class Finding(BaseModel):
    title: str
    severity: Literal[
        "info",
        "low",
        "medium",
        "high",
        "critical",
    ]
    explanation: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence]


class Risk(BaseModel):
    title: str
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]
    explanation: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence]


class Opportunity(BaseModel):
    title: str
    explanation: str
    expected_benefit: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence]


class MissingInformation(BaseModel):
    description: str
    reason: str
    importance: Literal[
        "low",
        "medium",
        "high",
    ]


class AnalystReport(BaseModel):
    executive_summary: str = Field(
        description="3-5 sentence summary of the customer's current situation."
    )
    customer_health: Literal[
        "excellent",
        "good",
        "fair",
        "poor",
        "critical",
    ]
    findings: list[Finding]
    risks: list[Risk]
    opportunities: list[Opportunity]
    missing_information: list[MissingInformation]
    overall_confidence: float = Field(
        ge=0,
        le=1
    )
    
    

ANALYST_PROMPT = """
You are the Analyst Agent in a customer support intelligence system.

Your role is to analyze the retrieved information and produce objective, evidence-based insights that directly address the Planner Agent's task.

You will receive:
- The user's original request.
- The task assigned by the Planner Agent.
- Retrieved information from one or more Retriever Agents.

User Query:
{user_query}

Task:
{task}

Retrieved Data:
{retrieved_data}

Your responsibilities:
- Understand the objective defined by the Planner Agent.
- Analyze all retrieved information collectively rather than evaluating each source independently.
- Identify the most important facts, patterns, trends, risks, opportunities, and inconsistencies relevant to the task.
- Distinguish observations from conclusions.
- Prioritize insights by their importance and relevance to the user's request.
- Generate practical recommendations only when they are supported by the available evidence.
- Clearly identify any missing information that prevents a complete analysis.

Rules:
- Base every conclusion solely on the retrieved information.
- Never fabricate facts, statistics, events, or customer details.
- Do not assume information that is not present in the retrieved data.
- If evidence is insufficient to answer the task confidently, explicitly indicate what information is missing instead of guessing.
- If different sources provide conflicting information, identify the conflict rather than attempting to resolve it yourself.
- Do not simply summarize the retrieved data. Synthesize it into meaningful insights.
- Avoid repeating the same evidence across multiple findings unless it genuinely supports multiple conclusions.
- Keep findings concise, specific, and actionable.
- Recommendations should be logical consequences of your findings, not generic best practices.
- Confidence should reflect the quality, consistency, and completeness of the available evidence.
- For every evidence item, the source field must be one of:
    - customer_profile
    - tickets
    - usage_events
    - billing
    - subscription
    - semantic_documents
    - other

    Do not use tool names such as get_ticket_data or semantic_retriever.

Think like an experienced business analyst: interpret the evidence, explain why it matters, and provide reliable insights that downstream agents can confidently use.
"""



async def analyst_node(state: AgentState, llm: BaseChatModel) -> AgentState:
    # state = prune_state(state)  # Week 5 Day 4's guard, applied before every LLM call
    step = next(
        (s for s in state["task_plan"]["steps"]
        if s["target"] == "Analyst Agent"),
        None,
    )
    if step:
        if state["retry_count"]>0:
            print(f"Retry Count: {state["retry_count"]} Analyst Node Executed")
        else:
            print("Analyst Node Executed")
        # llm = ChatGroq(model="Llama-3.3-70B-versatile", temperature=0)
        report = await llm.with_structured_output(AnalystReport).ainvoke(
            ANALYST_PROMPT.format(retrieved_data=json.dumps(state["retrieved_data"]),
                                  task=step["query"],
                                  user_query=state["messages"][0].content)
        )
        return {"analysis": report.model_dump(),}