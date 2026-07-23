import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Creates and returns a new connection to the Postgres database.
    Reads credentials from .env file (never hardcode passwords).
    """
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn