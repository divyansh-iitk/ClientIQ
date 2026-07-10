from langchain.tools import tool
import requests
from typing import Dict

BASE_URL = "http://localhost:8000/api"

@tool
def get_customer_profile(account_id: str)->Dict:
    """This api endpoint returns customer data

    Args:
        customer_id (str): Unique ID for each customer

    Returns:
        Dict: Details of customers
    """
    response = requests.get(f"{BASE_URL}/customers/{account_id}/profile")
    
    return response.json()


@tool
def get_ticket_data(account_id: str)->Dict:
    """This api endpoint returns data of tickets raised by customer

    Args:
        account_id (str): Unique ID for each customer

    Returns:
        Dict: Details of tickets raised
    """
    
    response = requests.get(f"{BASE_URL}/customers/{account_id}/tickets")
    
    return response.json()


@tool
def semantic_retriever(query: str)->Dict:
    """Returns semantic ticket data with respect to query

    Args:
        query (str): Query to retrieve semantic ticket data

    Returns:
        Dict: Retrived tickets data
    """
    
    response = requests.get(f"{BASE_URL}/retriever/{query}/semantic")
    
    return response.json()

# @tool
# def fuzzy_search(query: str)->Dict:
#     """Returns exact company name using fuzzy search

#     Args:
#         query (str): Company name from query

#     Returns:
#         Dict: Exact company name with ID
#     """
#     response = requests.get(f"{BASE_URL}/fuzzy_match/{query}")
    
#     return response.json()


def fuzzy_search(task_plan: dict)->dict:
    if task_plan["steps"][0]["step_type"]=="tool":
        response = requests.get(f"{BASE_URL}/fuzzy_match/{task_plan["steps"][0]["query"]}")
        for step in task_plan["steps"]:
            step["account_id"] = response.json()["account_id"]
    return task_plan
    