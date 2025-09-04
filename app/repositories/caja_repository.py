from app.db.database import Database

class CajaRepository:
    def __init__(self):
        self.db = Database()

    def get_all_boxes(self):
        query = """
            SELECT 
                cajas.id, 
                cajas.descripcion, 
                cajas.peso, 
                calidad_cajas.descripcion AS calidad_caja,
                calidad_cajas.id As calidad_caja_id
            FROM cajas 
            join calidad_cajas on calidad_cajas.id = cajas.calidad_caja_id
            WHERE cajas.estado = 1"""
        
        return self.db.execute(query)
    

    def create_box(self, *args):
        descripcion, calidad_id = args
        query = """
            INSERT INTO cajas (descripcion, calidad_caja_id, estado)
            VALUES (?, ?, 1)
        """
        self.db.execute(query, (descripcion, calidad_id))


    def update_status_box(self, id):
        query = """
            UPDATE cajas
            SET estado = 1
            WHERE id = ?
        """
        self.db.execute(query, (id))


    def update_status_boxes_all(self):
        query = """
            UPDATE cajas
            SET estado = 0
        """
        self.db.execute(query)