import os
from dotenv import load_dotenv

load_dotenv()

database_name = os.getenv("DB_NAME")
host = os.getenv("DB_HOST")

print("Database:", database_name)
print("Host:", host)