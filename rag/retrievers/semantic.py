from db_scripts.db_connect import SessionLocal
from sqlalchemy.orm import Session
from logger import logging
from rag.vector_store.embeddings import EmbeddingManager
from sqlalchemy import select
from db_scripts.tables import Ticket
from configs.config import SemanticRetrieverConfig

def dense_retriever(query: str, emb_mngr: EmbeddingManager, db: Session = None):
    if db is None:
        db = SessionLocal()
    
    embedding = emb_mngr.create_embeddings_query(query)
    
    try:
        stmt = (
            select(
                Ticket.account_id,
                Ticket.ticket_id,
                Ticket.subject,
                Ticket.description,
                Ticket.embedding.cosine_distance(embedding).label("distance")
            )
            .order_by("distance")
            .limit(SemanticRetrieverConfig.top_k)
        )
        results = db.execute(stmt).all()
    except Exception as e:
        logging.error(f"Error in semantic retrieval: {e}")
        raise
    finally:
        db.close()
    
    return results