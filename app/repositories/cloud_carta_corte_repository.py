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
    

    def get_cutting_letter_header(self, fecha_str):
        data = self.svp_client.request("GET", f"http://127.0.0.1:8001/api/produccion/pesaje/carta-corte-localidad/{fecha_str}/{self.svp_client.localidad_id}",  verify=False)
        return data or []


    def get_indicated_weight(self):
        data = self.svp_client.request("GET", f"http://127.0.0.1:8001/api/produccion/pesaje/peso-indicado/{self.svp_client.localidad_id}",  verify=False)
        return data or []
    
    def replicate_cut_off_weights(self, weights, location):
        data = self.svp_client.request("POST", f"http://127.0.0.1:8001/api/produccion/pesaje/carta-corte-replicar-pesos",
                                       {
                                          'pesos': weights,
                                          'localidad_id': location
                                       }, verify=False)
        return data