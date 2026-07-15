from sqlalchemy.orm import Session
from backend import services
from db_scripts.db_connect import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.api.schemas.endpoints import (CustomerProfileResponse,
                                           CustomerTicketsResponse,
                                           CustomerSummaryResponse,
                                           SemanticRetrieverResponse,
                                           FuzzyResponse)
from typing import List


router = APIRouter()

@router.get(
    "/customers/{customer_id}/profile",
    response_model=CustomerProfileResponse
)
def get_profile(customer_id: str, db: Session = Depends(get_db)):
    return services.get_profile(customer_id, db)


@router.get(
    "/customers/{customer_id}/tickets",
    response_model=CustomerTicketsResponse
)
def get_tickets(customer_id: str, db: Session = Depends(get_db)):
    return services.get_tickets(customer_id, db)

    
    
    
@router.get(
    "/customers/{customer_id}/summary",
    response_model=CustomerSummaryResponse
)
def get_summary(customer_id: str, db: Session = Depends(get_db)):
    return services.get_summary(customer_id, db)
    
    

@router.get(
    "/retriever/{query}/semantic",
    response_model=List[SemanticRetrieverResponse]
)
def semantic_retriever(request: Request, query: str, db: Session = Depends(get_db)):
    
    embedding_manager = request.app.state.embedding_manager
    try:
        response = services.semantic_retriever(embedding_manager, query, db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate embedding: {e}"
        )
    return response



@router.get(
    "/fuzzy_match/{query}",
    response_model=FuzzyResponse
)
def fuzzy_match(query: str, db: Session = Depends(get_db)):
    result = services.fuzzy_match(query, db)
    if result:
        return result
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No account named {query}"
            )
    
    
    