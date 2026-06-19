from db_scripts.db_connect import SessionLocal
from sqlalchemy.orm import Session
from db_scripts.tables import Ticket
from typing import List, Dict
        
        
def get_tickets(db: Session = None) -> List[Dict]:
    ticket_data = []
    if db is None:
        db = SessionLocal()
    try:
        tickets = db.query(Ticket).all()
        if(tickets):
            for ticket in tickets:

                ticket_data.append({

                    "ticket_id": ticket.ticket_id,

                    "text": f"Subject: {ticket.subject}\nDescription: {ticket.description}"

                })
    finally:
        db.close()
    return ticket_data