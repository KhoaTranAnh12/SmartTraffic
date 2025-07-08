import os
from dotenv import load_dotenv

load_dotenv()

environment = os.getenv('KHOA')
print(environment)