"""
Test script to verify PostgreSQL connection.
Run this once to confirm your .env and database setup are correct.
"""

import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def test_connection():
    """Attempt to connect to PostgreSQL and print server version."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        print("=" * 50)
        print("CONNECTION SUCCESSFUL!")
        print("=" * 50)
        print(f"PostgreSQL version:\n{version[0]}")
        print("=" * 50)

        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        print("=" * 50)
        print("CONNECTION FAILED!")
        print("=" * 50)
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is PostgreSQL running?")
        print("2. Is the password in .env correct?")
        print("3. Is the database 'researchhub' created?")
        print("4. Is the port 5432 correct?")
        print("=" * 50)

if __name__ == "__main__":
    test_connection()

