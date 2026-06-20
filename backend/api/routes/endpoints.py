from sqlalchemy.orm import Session
from db_scripts.db_connect import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, Request
from db_scripts.tables import Account, Ticket, Contact
from backend.api.schemas.endpoints import (CustomerProfileResponse,
                                           CustomerTicketsResponse,
                                           CustomerSummaryResponse,
                                           SemanticRetrieverResponse)
from rag.retrievers.semantic import dense_retriever
from typing import List

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        
        
        

router = APIRouter()

@router.get(
    "/customers/{customer_id}/profile",
    response_model=CustomerProfileResponse
)
def get_profile(
    customer_id: str,
    db: Session = Depends(get_db)
):
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

    return {
        "account_id": account.account_id,
        "account_name": account.account_name,
        "industry": account.industry,
        "company_size": account.company_size,
        "plan": account.plan,
        "contract_value": account.contract_value,
        "renewal_date": account.renewal_date,
        "account_status": account.account_status,
        "archetype": account.archetype,
        "contacts": contacts
    }


@router.get(
    "/customers/{customer_id}/tickets",
    response_model=CustomerTicketsResponse
)
def get_tickets(
    customer_id: str,
    db: Session = Depends(get_db)
):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.account_id == customer_id)
        .all()
    )

    return {
        "customer_id": customer_id,
        "ticket_count": len(tickets),
        "tickets": tickets
    }

    
    
    
@router.get(
    "/customers/{customer_id}/summary",
    response_model=CustomerSummaryResponse
)
def get_summary(
    customer_id: str,
    db: Session = Depends(get_db)
):
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

    return {
        "customer_id": customer_id,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "in_progress_tickets": in_progress_tickets,
        "usage_last_30_days": 0,
        "monthly_revenue": None,
        "renewal_in_days": None,
        "health_score": health_score,
        "risk_tier": risk_tier
    }
    
    

@router.get(
    "/retriever/{query}/semantic",
    response_model=List[SemanticRetrieverResponse]
)
def semantic_retriever(request: Request, query: str, db: Session = Depends(get_db)):
    
    embedding_manager = request.app.state.embedding_manager
    try:
        retrieved_docs = dense_retriever(query, embedding_manager, db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate embedding: {e}"
        )
        
    
    docs = []
    
    for row in retrieved_docs:
        docs.append({
            "customer_id": row.account_id,
            "ticket_id": row.ticket_id,
            "subject": row.subject,
            "description": row.description,
            "relevance_score": 1 - row.distance
            })
    
    return docs
    
    