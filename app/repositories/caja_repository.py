from app.db.database import Database

class CajaRepository:
    def __init__(self):
        self.db = Database()

    def get_all_boxes(self):
        query = """
            SELECT 
                cajas.id, 
                cajas.descripcion, 
                calidad_cajas.descripcion AS calidad_caja,
                calidad_cajas.id As calidad_caja_id
            FROM cajas 
            join calidad_cajas on calidad_cajas.id = cajas.calidad_id
            WHERE cajas.estado = 1"""
        data = self.db.execute(query, fetch=True)
        return data or []
    

    def create_box(self, caja, calidad_id):
        print(f"caja: {caja}, calidad: {calidad_id}")
        query = """
            INSERT INTO cajas (descripcion, calidad_id, estado)
            VALUES (%s, %s, 1)
        """
        print(query)
        self.db.execute(query, (caja, calidad_id))


    def update_status_box(self, id):
        query = """
            UPDATE cajas
            SET estado = 1
            WHERE id = %s
        """
        self.db.execute(query, (id,))


    def update_status_boxes_all(self):
        query = """
            UPDATE cajas
            SET estado = 0
        """
        self.db.execute(query)