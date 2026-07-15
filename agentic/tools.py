from langchain.tools import tool
from typing import Any
from backend import services
from db_scripts.db_connect import SessionLocal
from rag.vector_store.embeddings import EmbeddingManager

@tool
def get_customer_profile(account_id: str)->dict[str, Any]:
    """This tool returns customer data

    Args:
        account_id (str): Unique ID for each customer

    Returns:
        Dict: Details of customers
    """
    db = SessionLocal()
    result = services.get_profile(customer_id=account_id, db=db)
    return result.model_dump(mode="json")

@tool
def get_ticket_data(account_id: str)->dict[str, Any]:
    """This tool returns data of tickets raised by customer

    Args:
        account_id (str): Unique ID for each customer

    Returns:
        Dict: Details of tickets raised
    """
    db = SessionLocal()
    result = services.get_tickets(customer_id=account_id, db=db)
    return result.model_dump(mode="json")


@tool
def semantic_retriever(query: str)->dict[str, Any]:
    """Returns semantic ticket data with respect to query

    Args:
        query (str): Query to retrieve semantic ticket data

    Returns:
        Dict: Retrived tickets data
    """
    db = SessionLocal()
    embedding_manager = EmbeddingManager()
    result = services.semantic_retriever(embedding_manager=embedding_manager, query=query, db=db)
    return result.model_dump(mode="json")

def fuzzy_search(task_plan: dict)->dict[str, Any]:
    """Returns exact company name using fuzzy search

    Args:
        query (str): Company name from query

    Returns:
        Dict: task_plan updated with account_id
    """
    db = SessionLocal()
    if task_plan["steps"][0]["step_type"]=="tool":
        result = services.fuzzy_match(query=task_plan["steps"][0]["query"], db=db)
        for step in task_plan["steps"]:
            # step["account_id"] = result["account_id"]
            step["account_id"] = result.account_id
    return task_plan
    