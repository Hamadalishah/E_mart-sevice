import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

SUPER_ADMIN_USERNAME = os.getenv('SUPER_ADMIN_USERNAME')
print(f"Super Admin Username: {SUPER_ADMIN_USERNAME}")

SUPER_ADMIN_PASSWORD= os.getenv('SUPER_ADMIN_PASSWORD')
print(f"Super Admin Password: {SUPER_ADMIN_PASSWORD}")

SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL')
print(f"Super Admin Email: {SUPER_ADMIN_EMAIL}")

