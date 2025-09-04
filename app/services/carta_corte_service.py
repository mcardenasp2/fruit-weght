
from app.repositories.carta_corte_repository import CartaCorteRepository
from datetime import datetime

class CartaCorteService:
    def __init__(self, cloud_sync_carta_corte_service):
        self.carta_corte_repository = CartaCorteRepository()
        self.cloud_sync_carta_corte_service = cloud_sync_carta_corte_service


    def get_cut_off_chart_details(self):
        corte = self.carta_corte_repository.get_cut_off_letter()
        if corte is None:
            return []
        
        detalles = self.carta_corte_repository.get_cutting_details(corte["id"])
        return detalles
    
    
    def save_weight(self, corte_detalle_id, cantidad):
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")
        # llamar al repositorio pasando corte_detalle_id, cantidad, fecha y hora
        self.carta_corte_repository.save_weight(corte_detalle_id, cantidad, fecha, hora)



