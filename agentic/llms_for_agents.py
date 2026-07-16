from dataclasses import dataclass, field
from langchain.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

@dataclass
class LLMsForAgents:
    planner_llm: BaseChatModel = field(default_factory=lambda: ChatGroq(model="llama-3.3-70b-versatile", temperature=0))
    retriever_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))
    analyst_llm: BaseChatModel = field(default_factory=lambda: ChatGroq(model="llama-3.3-70b-versatile", temperature=0))
    action_plan_llm: BaseChatModel = field(default_factory=lambda: ChatGroq(model="llama-3.3-70b-versatile", temperature=0))
    critic_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))
    report_gen_llm: BaseChatModel = field(default_factory=lambda: ChatGroq(model="llama-3.3-70b-versatile", temperature=0))

# @dataclass
# class LLMsForAgents:
#     planner_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))
#     retriever_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))
#     analyst_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))
#     action_plan_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))
#     critic_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))
#     report_gen_llm: BaseChatModel = field(default_factory=lambda: ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0))