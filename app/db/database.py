import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import config

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = psycopg2.connect(
                host=config.get("db", "host"),
                port=config.get("db", "port"),
                dbname=config.get("db", "name"),
                user=config.get("db", "user"),
                password=config.get("db", "password")
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