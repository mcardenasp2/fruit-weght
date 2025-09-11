from app.clients.svp_client import SvpClient
from app.mappers.box_mapper import BoxMapper

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
    
    def replicate_cut_off_weights(self, weights):
        location = self.svp_client.localidad_id
        print(f"Antes de Base")
        weights = [BoxMapper.serialize_weight(r) for r in weights]
        print({
                "pesos": weights,
                "localidad_id": location,
            })
        data = self.svp_client.request(
            "POST",
            "http://127.0.0.1:8001/api/produccion/pesaje/carta-corte-replicar-pesos",
            json={
                "pesos": weights,
                "localidad_id": location,
            },
            verify=False
        )
        print("Respuesta completa del servidor:", data)

        # Verificar que la request fue exitosa y que trae los ids
        if data and data.get("success") and "ids" in data:
            print("IDs recibidos:", data["ids"])
            return data["ids"]

        # Si algo falla, retornar lista vacía
        print("No se recibieron ids o la request falló")
        return []