from backend import services
from db_scripts.db_connect import SessionLocal
from agentic.tools import get_customer_profile
# db=SessionLocal()
# response = services.get_profile(customer_id="ACC-02065070f173", db=db)
response = get_customer_profile.invoke({"account_id": "ACC-02065070f173"})
print(response)