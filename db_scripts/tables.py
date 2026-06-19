from db_scripts.db_connect import engine
from logger import logging
from datetime import date, datetime
from pgvector.sqlalchemy import Vector

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_name: Mapped[str]
    industry: Mapped[str]
    company_size: Mapped[int]

    plan: Mapped[str]
    contract_value: Mapped[float]

    renewal_date: Mapped[date]

    account_status: Mapped[str]
    archetype: Mapped[str]


class Contact(Base):
    __tablename__ = "contacts"

    contact_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    name: Mapped[str]
    job_title: Mapped[str]
    email: Mapped[str]

    decision_maker_flag: Mapped[bool]
    is_primary_contact: Mapped[bool]


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    created_at: Mapped[datetime]
    resolved_at: Mapped[datetime | None]

    status: Mapped[str]
    priority: Mapped[str]

    subject: Mapped[str]

    description: Mapped[str] = mapped_column(Text)
    
    embedding: Mapped[list[float] | None] = mapped_column(

        Vector(1536),

        nullable=True

    )


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    message_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.ticket_id"),
        nullable=False,
    )

    sender_type: Mapped[str]

    timestamp: Mapped[datetime]

    message_body: Mapped[str] = mapped_column(Text)


class UsageEvent(Base):
    __tablename__ = "usage_events"

    event_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    timestamp: Mapped[datetime]

    event_name: Mapped[str]


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    plan: Mapped[str]

    contract_value: Mapped[float]

    renewal_date: Mapped[date]

    status: Mapped[str]


class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    amount: Mapped[float]

    due_date: Mapped[date]

    status: Mapped[str]


class BillingEvent(Base):
    __tablename__ = "billing_events"

    event_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    invoice_id: Mapped[str] = mapped_column(
        ForeignKey("invoices.invoice_id"),
        nullable=False,
    )

    event_type: Mapped[str]

    event_description: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime]


class Email(Base):
    __tablename__ = "emails"

    email_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    timestamp: Mapped[datetime]

    subject: Mapped[str]

    body: Mapped[str] = mapped_column(Text)


class Meeting(Base):
    __tablename__ = "meetings"

    meeting_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    date: Mapped[date]

    notes: Mapped[str] = mapped_column(Text)


class CallTranscript(Base):
    __tablename__ = "call_transcripts"

    call_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    date: Mapped[date]

    transcript: Mapped[str] = mapped_column(Text)


class CSMNote(Base):
    __tablename__ = "csm_notes"

    note_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    created_at: Mapped[datetime]

    note: Mapped[str] = mapped_column(Text)


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    query: Mapped[str]

    recommended_action: Mapped[str]

    feedback: Mapped[str]

    timestamp: Mapped[datetime]


class Outcome(Base):
    __tablename__ = "outcomes"

    outcome_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False,
    )

    action_taken: Mapped[str]

    outcome_type: Mapped[str]

    outcome_date: Mapped[date]


if __name__=="__main__":
    
    try:
        Base.metadata.create_all(bind=engine)
        logging.info(f"Tables created in DB")
        print(f"Tables created in DB")
    
    except Exception as e:
        logging.error(f"Error while creating tables in DB:{e}")