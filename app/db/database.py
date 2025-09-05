import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.core.config import config


class Database:
    def __init__(self):
        # Crear un pool de conexiones (mínimo 1, máximo 10)
        self.pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=config.get("db", "host"),
            port=config.get("db", "port"),
            dbname=config.get("db", "name"),
            user=config.get("db", "user"),
            password=config.get("db", "password")
        )

    def execute(self, query, params=None, fetch=False):
        conn = self.pool.getconn()  # tomar conexión del pool
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchall() if fetch else None
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            print(f"[DB ERROR] {e}")
            raise
        finally:
            self.pool.putconn(conn)  # devolver conexión al pool

    def closeall(self):
        """Cerrar todas las conexiones al terminar la aplicación"""
        self.pool.closeall()
