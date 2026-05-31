from dataclasses import asdict, dataclass
import os
from dotenv import load_dotenv
load_dotenv()



@dataclass
class PgSqlConfig:
    pguser: str = "divyanshyadav"
    pgpassword: str = os.getenv("PG_USER_PASSWORD")
    pghost: str = "localhost"
    pgport: int = 5432
    pgdb: str = "customer_db"
    
    
if __name__=="__main__":
    print(asdict(PgSqlConfig()))