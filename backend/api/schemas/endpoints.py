from datetime import date, datetime
from langchain.messages import AIMessage
from pydantic import BaseModel, ConfigDict
from typing import List


class ContactResponse(BaseModel):
    contact_id: str
    name: str | None = None
    email: str | None = None
    job_title: str | None = None
    decision_maker_flag: bool | None = None
    is_primary_contact: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class CustomerProfileResponse(BaseModel):
    account_id: str
    account_name: str
    industry: str | None = None
    company_size: int | None = None
    plan: str | None = None
    contract_value: float | None = None
    renewal_date: date | None = None
    account_status: str | None = None

    contacts: List[ContactResponse] = []

    model_config = ConfigDict(from_attributes=True)
    
    



class TicketResponse(BaseModel):
    ticket_id: str
    account_id: str

    subject: str | None = None
    status: str | None = None
    priority: str | None = None

    created_at: datetime | None = None
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
    
    
class CustomerTicketsResponse(BaseModel):
    customer_id: str
    ticket_count: int
    tickets: list[TicketResponse]

    model_config = ConfigDict(from_attributes=True)
    
    
class CustomerSummaryResponse(BaseModel):
    customer_id: str

    open_tickets: int
    closed_tickets: int

    usage_last_30_days: int

    monthly_revenue: float | None = None

    renewal_in_days: int | None = None

    health_score: int

    risk_tier: str

    model_config = ConfigDict(from_attributes=True)


class SemanticRetrieverResponse(BaseModel):
    customer_id: str
    
    ticket_id: str
    subject: str
    description: str
    relevance_score: float


class FuzzyResponse(BaseModel):
    account_name: str
    account_id: str
    similarity_score: float
    
class AgentResponse(BaseModel):
    response: AIMessage
    
    