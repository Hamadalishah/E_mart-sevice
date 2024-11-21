import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
