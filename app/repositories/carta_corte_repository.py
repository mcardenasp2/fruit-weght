
from app.db.database import Database

class CartaCorteRepository:
    def __init__(self):
        self.db = Database()


    def save_weight(self, *args):
        corte_detalle_id, cantidad, fecha, hora = args
        query = """
             insert into pe_cortes_detalles (corte_detalle_id, cantidad, fecha, hora)
                values (?, ?, ?, ?)
            """
        self.db.execute(query, (corte_detalle_id, cantidad, fecha, hora))
    
    