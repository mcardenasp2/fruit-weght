from app.services.scale_service import ScaleService
from app.services.carta_corte_service import CartaCorteService
from app.services.cloud_sync_carta_corte_service import CloudSyncCartaCorteService
from app.controllers.pesaje_controller import PesajeController
from app.screens.pesaje_principal_screen import PantallaPesaje
from app.services.replicator_service import ReplicatorService

def main():
    scale = ScaleService()
    # scale.start() 
    carta = CartaCorteService()
    cloud = CloudSyncCartaCorteService()

    # Replicador: hoy cada 5s, histórico cada 10 minutos
    replicator = ReplicatorService(cloud, interval_today=5, interval_history=600)
    replicator.start()

    controller = PesajeController(scale, carta, cloud)
    app = PantallaPesaje(controller=controller)
    app.run()
    scale.stop()


if __name__ == "__main__":
    main()
