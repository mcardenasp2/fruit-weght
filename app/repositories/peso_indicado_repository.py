from app.db.database import Database


class PesoIndicadoRepository:
    def __init__(self):
        self.db = Database()


    def update_status_indicated_weights_all(self):
        query = """
            UPDATE pe_pesos_indicados
            SET estado = 0
        """
        self.db.execute(query)

    
    def update_status_indicated_weight(self, peso_id):
        query = """
            UPDATE pe_pesos_indicados
            SET estado = 1
            WHERE id = %s
        """
        self.db.execute(query, (peso_id,))
        


    def create_indicated_weight(self, caja_id, peso_minimo, peso_maximo, peso_ideal, tara, localidad_id):
        query = """
            INSERT INTO pe_pesos_indicados (caja_id, peso_minimo, peso_maximo, peso_ideal, tara, localidad_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db.execute(query, (caja_id, peso_minimo, peso_maximo, peso_ideal, tara, localidad_id))



    def get_indicated_weight(self):
        query = """
            SELECT
                pi.id AS peso_indicado_id,
                c.id AS caja_id,
                c.descripcion AS caja,
                pi.peso_minimo,
                pi.peso_maximo,
                pi.peso_ideal,
                pi.tara,
                cc.descripcion AS calidad_caja
            FROM pe_pesos_indicados pi
            JOIN cajas c ON c.id = pi.caja_id
            join calidad_cajas cc ON cc.id = c.calidad_id
            where pi.estado = 1
        """
        data = self.db.execute(query, fetch=True)
        return data or []