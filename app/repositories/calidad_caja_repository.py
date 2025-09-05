from app.db.database import Database


class CalidadCajaRepository:
    def __init__(self):
        self.db = Database()

    def get_all_quality_boxes(self):
        query = """
            SELECT 
                id, 
                descripcion, 
                observacion,
                estado
            FROM calidad_cajas 
            WHERE estado = 1"""
        
        resultado = self.db.execute(query, fetch = True)
        return resultado if resultado else []
    
    
    def create_quality_box(self, descripcion, observacion):
        observacion = observacion or None
        query = """
            INSERT INTO calidad_cajas (descripcion, observacion, estado)
            VALUES (%s, %s, %s)
        """
        self.db.execute(query, (descripcion, observacion, 1), fetch=False)


    def update_quality_boxes_all(self):
        query = """
            UPDATE calidad_cajas
            SET estado = 0
        """
        self.db.execute(query)
    

    def update_status_quality_box(self, id):
        query = """
            UPDATE calidad_cajas
            SET estado = 1
            WHERE id = %s
        """
        self.db.execute(query, (id, ), fetch=False)