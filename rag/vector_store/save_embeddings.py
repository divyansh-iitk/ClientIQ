from db_scripts.db_connect import SessionLocal
from sqlalchemy.orm import Session
from db_scripts.tables import Ticket
from logger import logging


def save_embeddings(ticket_data: list, vectors: list, db: Session = None) -> None:
    if db is None:
        db = SessionLocal()
    
    try:
        for item, vector in zip(ticket_data, vectors):

            db.query(Ticket).filter(

                Ticket.ticket_id == item["ticket_id"]

            ).update({

                "embedding": vector

            })
            db.commit()
        logging.info(f"Saved {len(vector)} embeddings in database")
    except Exception as e:
        logging.error(f"Error while saving embeddings: {e}")
        raise
    finally:
        db.close()