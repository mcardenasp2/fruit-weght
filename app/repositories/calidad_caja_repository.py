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
        
        resultado = self.db.execute(query)
        return resultado[0] if resultado else []
    
    
    def create_quality_box(self, descripcion, observacion):

        observacion = observacion or None
        observacion = 'Prueba'
        print(f"Descripcion: {descripcion}, Observacion: {observacion}")
        query = """
            INSERT INTO calidad_cajas (descripcion, observacion, estado)
            VALUES (%s, %s, %s)
        """
        self.db.execute(query, (descripcion, observacion, 1), fetch=True)


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
            WHERE id = ?
        """
        self.db.execute(query, (id))