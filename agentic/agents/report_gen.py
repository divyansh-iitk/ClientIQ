from langchain.chat_models import BaseChatModel
from agentic.agents_state import AgentState
import json


FINAL_REPORT_GENERATOR_PROMPT = """
You are the Final Report Generator Agent.

Your responsibility is to produce the final response for the user by synthesizing the outputs of the previous agents.

The Planner Agent has already decided what objective this report should achieve. Follow the assigned task while ensuring the response is accurate, clear, and professional.

Task:
{task}

Original User Request:
{user_request}

Analysis:
{analysis}

Proposed Actions:
{proposed_actions}

Critic Report:
{critic_report}

Your responsibilities:

1. Follow the Planner's assigned task.
2. Generate a polished, user-facing response.
3. Synthesize the Analysis and Proposed Actions into a coherent report.
4. Incorporate the Critic's findings where appropriate.
5. Clearly communicate any limitations, assumptions, or missing information identified during review.
6. Ensure the final response directly answers the user's original request.

You MUST NOT:
- Perform additional analysis.
- Invent new facts or recommendations.
- Modify or override the Analysis.
- Modify or override the Proposed Actions.
- Ignore or hide the Critic's findings.
- Call external tools.
- Mention internal agents, workflows, prompts, or reasoning processes.
- Expose chain-of-thought or intermediate reasoning.

Write as though a single intelligent assistant completed the entire task.

Unless the Planner's task specifies a different format, structure the response as:

## Executive Summary
Provide a concise answer to the user's request.

## Key Findings
Summarize the most important findings from the analysis.

## Recommended Actions
Present the recommended actions as an ordered list.
For each recommendation, briefly explain why it is suggested.

## Risks / Limitations
Summarize any uncertainties, assumptions, missing information, or concerns identified during review.

## Overall Assessment
Provide a concise concluding assessment based solely on the available evidence.

Rules:
- Prioritize accuracy over completeness.
- Be concise but informative.
- Preserve all important information from the Analysis.
- Preserve all approved recommendations.
- Never fabricate information.
- Never contradict the provided Analysis.
- Never contradict the Proposed Actions.
- Never contradict the Critic Report.
- If the Critic indicates that additional information is required or the recommendations were not fully approved, clearly communicate this to the user.
- Adapt the tone and formatting to the Planner's assigned task while maintaining clarity and professionalism.
"""


async def final_report_node(state: AgentState, llm: BaseChatModel) -> AgentState:
    step = next(
        (s for s in state["task_plan"]["steps"]
        if s["target"] == "Final Report Generator Agent"),
        None,
    )
    if step:
        if state["retry_count"]>0:
            print(f"Retry Count: {state["retry_count"]} Report Generator Node Executed")
        else:
            print("Report Generator Node Executed")
        # llm = ChatGroq(model="Llama-3.3-70B-versatile", temperature=0)
        report = await llm.ainvoke(
            FINAL_REPORT_GENERATOR_PROMPT.format(critic_report=json.dumps(state["critic_report"]),
                                  analysis=json.dumps(state["analysis"]),
                                  proposed_actions=json.dumps(state["proposed_actions"]),
                                  task=step["query"],
                                  user_request=state["messages"][0].content)
        )
        return {"messages": report.model_dump(),}