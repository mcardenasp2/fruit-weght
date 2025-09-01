from app.db.database import Database

class CajaRepository:
    def __init__(self, conn=None):
        self.conn = conn or db_connection
        

def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM cajas ORDER BY fecha_creacion DESC")
        return cursor.fetchall()