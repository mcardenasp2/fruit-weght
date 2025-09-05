from app.clients.svp_client import SvpClient
from app.repositories.cloud_carta_corte_repository import CloudCartaCorteRepository
from app.repositories.carta_corte_repository import CartaCorteRepository
from app.repositories.calidad_caja_repository import CalidadCajaRepository
from app.repositories.caja_repository import CajaRepository
from psycopg2.extras import RealDictCursor
from psycopg2.extras import RealDictRow

from datetime import date

class CloudSyncCartaCorteService:
    def __init__(self):
        try:
            client = SvpClient()
            # Intenta cargar desde cache
            if not client.load_token_from_cache():
                client.login()  # si no hay cache o está expirado, hace login
        except Exception:
            client = None
        self.cloud_carta_corte_repo = CloudCartaCorteRepository(client)
        self.carta_corte_repo = CartaCorteRepository()
        self.calidad_cajas_repo = CalidadCajaRepository()
        self.caja_repo = CajaRepository()



    def sync_quality_boxes(self):
        quality_boxes_cloud = self.cloud_carta_corte_repo.get_all_quality_boxes()
        quality_boxes_local = self.calidad_cajas_repo.get_all_quality_boxes()


        if quality_boxes_cloud:
            # actualizar el estado de todos a 0
            self.calidad_cajas_repo.update_quality_boxes_all()

        quality_boxes_local = [
            {
                "id": row["id"],
                "descripcion": row["descripcion"],
                "observacion": row["observacion"] or "",
                "estado": row["estado"]
            }
            for row in quality_boxes_local
        ]

        quality_boxes_cloud = [
            {**row, "observacion": row.get("observacion") or ""}
            for row in quality_boxes_cloud
        ]

        for cloud in quality_boxes_cloud:
            match = next(
                (
                    local for local in quality_boxes_local
                    if local["descripcion"] == cloud["descripcion"]
                ),
                None
            )

            if match:
                self.calidad_cajas_repo.update_status_quality_box(match["id"])

            else:
                self.calidad_cajas_repo.create_quality_box(
                    descripcion=cloud["descripcion"],
                    observacion=cloud["observacion"]
                )

        print("Termina sincronizacion calidad Cajas")




    def sync_boxes(self):
        cajas_cloud = self.cloud_carta_corte_repo.boxes_by_location()

        calidad_cajas_local = self.calidad_cajas_repo.get_all_quality_boxes()
        cajas_local = self.caja_repo.get_all_boxes()

        cajas_cloud = [
            {**row}
            for row in cajas_cloud
        ]

        calidad_cajas_local = [
            {
                "id": row["id"],
                "descripcion": row["descripcion"]
            }
            for row in calidad_cajas_local
        ]

        cajas_local = [
            {
                "id": row["id"],
                "descripcion": row["descripcion"],
                "calidad_caja": row["calidad_caja"],
                "calidad_caja_id": row["calidad_caja_id"]
            }
            for row in cajas_local
        ]

        if cajas_cloud:
            self.caja_repo.update_status_boxes_all()

        for cloud in cajas_cloud:
            # Buscar registro local que coincida en todos los campos clave
            match = next(
                (
                    local for local in cajas_local
                    if local["descripcion"] == cloud["caja"]
                    and local["calidad_caja"] == cloud["calidad_caja"]
                ),
                None
            )

            if match:
                self.caja_repo.update_status_box(match["id"])
            else:

                match_calidad = next(
                    (
                        local for local in calidad_cajas_local
                        if local["descripcion"] == cloud["calidad_caja"]
                    ),
                    None
                )

                if match_calidad:

                    self.caja_repo.create_box(
                        caja=cloud["caja"],
                        calidad_id=match_calidad["id"]
                    )



        

                    

    def sync_indicated_weight(self):
        peso_indicados_cloud = self.cloud_carta_corte_repo.get_indicated_weight()
        peso_indicados_local = self.carta_corte_repo.get_indicated_weight()

        # print(f"peso_indicados_local: {peso_indicados_local}")

        # return
        cajas_local = self.caja_repo.get_all_boxes()

        cajas_local = [
            {
                "id": row["id"],
                "descripcion": row["descripcion"],
                "calidad_caja": row["calidad_caja"],
            }
            for row in cajas_local
        ]


        if peso_indicados_cloud:
            self.carta_corte_repo.update_status_indicated_weights_all()

        peso_indicados_cloud = [
            {
                "caja": row["caja"]["descripcion"],
                "peso_minimo": row["peso_minimo"],
                "peso_ideal": row["peso_ideal"],
                "peso_maximo": row["peso_maximo"],
                "calidad_caja": row["caja"]["calidad"]["descripcion"],
                "tara": row["tara"]
            }
            for row in peso_indicados_cloud
        ]

        

        peso_indicados_local = [
            {
                "peso_indicado_id": row["peso_indicado_id"],
                "caja": row["caja"],
                "peso_minimo": row["peso_minimo"],
                "peso_ideal": row["peso_ideal"],
                "peso_maximo": row["peso_maximo"],
                "tara": row["tara"]
            }
            for row in peso_indicados_local
        ]

     

        # ver si se cambia el estado a todos a cero 
        for cloud in peso_indicados_cloud:
            # Buscar registro local que coincida en todos los campos clave
            match = next(
                (
                    local for local in peso_indicados_local
                    if local["caja"] == cloud["caja"]
                    and local["peso_minimo"] == cloud["peso_minimo"]
                    and local["peso_ideal"] == cloud["peso_ideal"]
                    and local["peso_maximo"] == cloud["peso_maximo"]
                    and local["tara"] == cloud["tara"]
                ),
                None
            )

            if match:
                # Existe registro idéntico → no hacer nada

                self.carta_corte_repo.update_status_indicated_weight(match["peso_indicado_id"])

            else:
                match_caja = next(
                    (
                        local for local in cajas_local
                        if local["descripcion"] == cloud["caja"]
                        and local["calidad_caja"] == cloud["calidad_caja"]
                    ),
                    None
                )

                if match_caja:
                    # Actualizar o insertar según convenga
                    self.carta_corte_repo.create_indicated_weight(
                        caja_id=match_caja["id"],
                        peso_minimo=cloud["peso_minimo"],
                        peso_maximo=cloud["peso_maximo"],
                        peso_ideal=cloud["peso_ideal"],
                        tara=cloud["tara"]
                    )


        
    
    def sync_carta_corte(self):
        hoy = date.today()
        date = hoy.strftime("%Y-%m-%d")
        carta_corte = self.cloud_carta_corte_repo.get_cutting_letter_header(date)
        if carta_corte:
            details = self.cloud_carta_corte_repo.get_cutting_chart_detail(carta_corte["id"])
            for detail in details:
                data_details = {
                    "nombre_peso_indicado" : detail["nombre_peso_indicado"],
                    "cantidad": detail["cantidad"],
                    "estado": detail["estado"],
                }
        
            header_data = {
                "fecha": carta_corte["fecha"],
                "localidad_id": carta_corte["localidad_id"],
                "hora": carta_corte["hora"],
                "detalles": data_details
            }

            self.carta_corte_repo.save_cut_off_chart(header_data)
    


    def sync_all(self):
        # self.sync_quality_boxes()
        # self.sync_boxes()
        self.sync_indicated_weight()
        # self.sync_carta_corte()
        
