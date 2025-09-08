
from app.repositories.carta_corte_repository import CartaCorteRepository
from datetime import datetime

class CartaCorteService:
    def __init__(self):
        self.carta_corte_repository = CartaCorteRepository()


    def get_cut_off_letter_details(self):
        ahora = datetime.now()
        fecha_str = ahora.strftime("%Y-%m-%d")
        detalles = self.carta_corte_repository.get_cut_off_letter_details(fecha_str)
        return detalles
    
    
    def save_weight(self, corte_detalle_id, cantidad):
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")
        # llamar al repositorio pasando corte_detalle_id, cantidad, fecha y hora
        self.carta_corte_repository.save_weight(corte_detalle_id, cantidad, fecha, hora)



