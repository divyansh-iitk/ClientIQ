from typing import List
from fastapi import HTTPException
from rapidfuzz import process
from requests import Session
from backend.api.schemas.endpoints import CustomerProfileResponse, CustomerSummaryResponse, CustomerTicketsResponse, FuzzyResponse, SemanticRetrieverResponse, SemanticRetrieverResult
from logger import logging
from db_scripts.tables import Account, Contact, Ticket
from rag.retrievers.semantic import dense_retriever
from rag.vector_store.embeddings import EmbeddingManager

def get_profile(customer_id: str, db: Session) -> CustomerProfileResponse:
    account = (
        db.query(Account)
        .filter(Account.account_id == customer_id)
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    contacts = (
        db.query(Contact)
        .filter(Contact.account_id == customer_id)
        .all()
    )

    return CustomerProfileResponse(
        account_id = account.account_id,
        account_name = account.account_name,
        industry = account.industry,
        company_size = account.company_size,
        plan = account.plan,
        contract_value = account.contract_value,
        renewal_date = account.renewal_date,
        account_status = account.account_status,
        contacts = contacts
    )
    
    
def get_tickets(customer_id: str, db: Session) -> CustomerTicketsResponse:
    tickets = (
        db.query(Ticket)
        .filter(Ticket.account_id == customer_id)
        .all()
    )

    return CustomerTicketsResponse(
        customer_id = customer_id,
        ticket_count = len(tickets),
        tickets = tickets
    )

def get_summary(customer_id: str, db: Session) -> CustomerSummaryResponse:
    open_tickets = (
        db.query(Ticket)
        .filter(
            Ticket.account_id == customer_id,
            Ticket.status.ilike("open")
        )
        .count()
    )
    closed_tickets = (
        db.query(Ticket)
        .filter(
            Ticket.account_id == customer_id,
            Ticket.status.ilike("closed")
        )
        .count()
    )
    
    in_progress_tickets = (
        db.query(Ticket)
        .filter(
            Ticket.account_id == customer_id,
            Ticket.status.ilike("in_progress")
        )
        .count()
    )

    health_score = 100

    if open_tickets > 5:
        health_score -= 20

    risk_tier = (
        "high"
        if health_score < 50
        else "medium"
        if health_score < 80
        else "low"
    )

    return CustomerSummaryResponse(
        customer_id = customer_id,
        open_tickets = open_tickets,
        closed_tickets = closed_tickets,
        in_progress_tickets = in_progress_tickets,
        usage_last_30_days = 0,
        monthly_revenue = None,
        renewal_in_days = None,
        health_score = health_score,
        risk_tier = risk_tier
    )


def semantic_retriever(embedding_manager: EmbeddingManager, query: str, db: Session) -> SemanticRetrieverResult:
    try:
        retrieved_docs = dense_retriever(query, embedding_manager, db)
    except Exception as e:
        logging.error(f"Could not generate embedding: {e}")
        raise
        
    docs = []
    
    for row in retrieved_docs:
        docs.append(SemanticRetrieverResponse(
            customer_id = row.account_id,
            ticket_id = row.ticket_id,
            subject = row.subject,
            description = row.description,
            relevance_score = 1 - row.distance
            ))
    
    return SemanticRetrieverResult(results = docs)


def fuzzy_match(query: str, db: Session) -> FuzzyResponse:
    
    accounts_data = db.query(Account).with_entities(Account.account_name, Account.account_id).all()
    company_db = dict(accounts_data)
    
    company_names = list(company_db.keys())
    
    result = process.extractOne(query, company_names)

    if result and result[1] > 80:

        return FuzzyResponse(
            account_name = result[0],
            account_id = company_db[result[0]],
            similarity_score = result[1]
        )
    else:
        logging.error(f"No account named {query}")
        raise