from app.clients.svp_client import SvpClient

class CloudCartaCorteRepository:
    def __init__(self, client : SvpClient):
        self.svp_client = client


    def get_all_quality_boxes(self):
        data = self.svp_client.request("GET", "http://127.0.0.1:8001/api/produccion/banprod/crud/cajas-calidad?per_page=all",  verify=False)
        return data or []
    

    def boxes_by_location(self):
        data = self.svp_client.request("GET", f"http://127.0.0.1:8001/api/produccion/banprod/crud/caja-localidad/{self.svp_client.localidad_id}",  verify=False)
        return data or []
    

    def get_cutting_letter_header(self, date):
        data = self.svp_client.request("GET", f"/api/cutting-chart/header/{self.svp_client.localidad_id}/{date}",  verify=False)
        return data or None



    def get_cutting_chart_detail(self, header_id):
        data = self.svp_client.request("GET", f"/api/cutting-chart/detail/{header_id}",  verify=False)
        return data or []
    

    def get_indicated_weight(self):
        data = self.svp_client.request("GET", f"http://127.0.0.1:8001/api/produccion/pesaje/peso-indicado/{self.svp_client.localidad_id}",  verify=False)
        return data or []
    