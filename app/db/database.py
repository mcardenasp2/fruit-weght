import psycopg2
import os
from psycopg2.extras import RealDictCursor

from dotenv import load_dotenv

# Cargar .env
load_dotenv()

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                dbname=os.getenv("DB_PORT"),
                user=os.getenv("DB_PORT"),
                password=os.getenv("DB_PORT")
            )
        return self.conn
    

    def execute(self, query, params=None, fetch=False):
        conn = self.connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            result = cur.fetchall() if fetch else None
            conn.commit()
            return result

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None