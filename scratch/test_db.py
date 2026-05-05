
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(os.path.join('backend', '.env'))
uri = os.getenv('SQLALCHEMY_DATABASE_URI')
print(f"Connecting to: {uri}")
try:
    engine = create_engine(uri)
    connection = engine.connect()
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")
