from app.clients.svp_client import SvpClient
from app.repositories.cloud_carta_corte_repository import CloudCartaCorteRepository

class CloudSyncCartaCorteService:
    def __init__(self):
        try:
            client = SvpClient()
            client.login()
        except Exception:
            client = None
        self.cloud_users_repo = CloudCartaCorteRepository(client)


    def sync_carta_corte(self):
        users = self.cloud_users_repo.get_all_clients()
        print(users)
