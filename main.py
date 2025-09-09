from app.services.scale_service import ScaleService
from app.services.carta_corte_service import CartaCorteService
from app.services.cloud_sync_carta_corte_service import CloudSyncCartaCorteService
from app.controllers.pesaje_controller import PesajeController
from app.screens.pesaje_principal_screen import PantallaPesaje

def main():
    scale = ScaleService()
    scale.start() 
    carta = CartaCorteService()
    cloud = CloudSyncCartaCorteService()
    controller = PesajeController(scale, carta, cloud)
    app = PantallaPesaje(controller=controller)
    app.run()
    scale.stop()


if __name__ == "__main__":
    main()
