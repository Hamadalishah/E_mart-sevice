import os
from dotenv import load_dotenv

load_dotenv()

DATABASEURL = os.getenv("DATABASEURL")
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
