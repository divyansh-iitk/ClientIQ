import json
from sqlalchemy.orm import Session
from logger import logging

from db_scripts.db_connect import engine
from db_scripts.tables import (
    Account, Contact, Ticket, TicketMessage, UsageEvent,
    Subscription, Invoice, BillingEvent, Email,
    Meeting, CallTranscript, CSMNote, Feedback, Outcome
)

with open("data/b2b_customer_dataset.json", "r") as f:
    data = json.load(f)

table_mapping = {
    "accounts": Account,
    "contacts": Contact,
    "tickets": Ticket,
    "ticket_messages": TicketMessage,
    "usage_events": UsageEvent,
    "subscriptions": Subscription,
    "invoices": Invoice,
    "billing_events": BillingEvent,
    "emails": Email,
    "meetings": Meeting,
    "call_transcripts": CallTranscript,
    "csm_notes": CSMNote,
    "feedback": Feedback,
    "outcomes": Outcome,
}

with Session(engine) as session:
    try:
        for json_key, model_class in table_mapping.items():

            records = data.get(json_key, [])

            if not records:
                logging.warning(f"No records found for {json_key}")
                continue

            session.bulk_insert_mappings(
                model_class,
                records
            )

            logging.info(f"Inserted {len(records)} rows into {model_class.__tablename__}")

        session.commit()
        logging.info("All data inserted successfully!")

    except Exception as e:
        session.rollback()
        logging.error(f"Error in data insertion: {e}")
        raise