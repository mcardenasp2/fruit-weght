from app.clients.svp_client import SvpClient

class CloudCartaCorteRepository:
    def __init__(self, client : SvpClient):
        self.svp_client = client


    def get_all_clients(self):
        data = self.svp_client.request("GET", "/api/security/list-users",  verify=False)
        return data or []
    

    def boxes_by_location(self):
        data = self.svp_client.request("GET", f"/api/boxes/by-location/{self.svp_client.localidad_id}",  verify=False)
        return data or []
    

    def get_cutting_letter_header(self, date):
        data = self.svp_client.request("GET", f"/api/cutting-chart/header/{self.svp_client.localidad_id}/{date}",  verify=False)
        return data or []



    def get_cutting_chart_detail(self, header_id):
        data = self.svp_client.request("GET", f"/api/cutting-chart/detail/{header_id}",  verify=False)
        return data or []
    