from app.clients.svp_client import SvpClient
from app.repositories.cloud_carta_corte_repository import CloudCartaCorteRepository
from app.repositories.carta_corte_repository import CartaCorteRepository
from app.repositories.calidad_caja_repository import CalidadCajaRepository
from app.repositories.caja_repository import CajaRepository

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
        print(f"Cajas {quality_boxes_cloud}")

        if quality_boxes_cloud:
            # actualizar el estado de todos a 0
            self.calidad_cajas_repo.update_quality_boxes_all()


        for cloud in quality_boxes_cloud:
            # Buscar registro local que coincida en todos los campos clave
            match = next(
                (
                    local for local in quality_boxes_local
                    if local["descripcion"] == cloud["descripcion"]
                    and local["observacion"] == cloud["observacion"]
                ),
                None
            )

            if match:
                self.calidad_cajas_repo.update_status_quality_box(match["id"])
               
            else:
                # Insertar o actualizar según convenga
                self.calidad_cajas_repo.create_quality_box(
                    descripcion=cloud["descripcion"],
                    observacion=cloud["observacion"]
                )


    def sync_boxes(self):
        cajas_cloud = self.cloud_carta_corte_repo.boxes_by_location()
        cajas_local = self.caja_repo.get_all_boxes()
        calidad_cajas_local = self.calidad_cajas_repo.get_all_quality_boxes()

        if cajas_cloud:
            self.caja_repo.update_status_boxes_all()

        for cloud in cajas_cloud:
            # Buscar registro local que coincida en todos los campos clave
            match = next(
                (
                    local for local in cajas_local
                    if local["nombre"] == cloud["nombre"]
                    and local["descripcion"] == cloud["descripcion"]
                    and local["calidad_caja_id"] == cloud["calidad_caja_id"]
                    and local["estado"] == cloud["estado"]
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
                        descripcion=cloud["descripcion"],
                        calidad_id=match_calidad["id"]
                    )

                    

    def sync_indicated_weight(self):
        peso_indicados_cloud = self.cloud_carta_corte_repo.get_indicated_weight()
        peso_indicados_local = self.carta_corte_repo.get_indicated_weight()
        cajas_local = self.caja_repo.get_all_boxes()


        # ver si se cambia el estado a todos a cero 
        for cloud in peso_indicados_cloud:
            # Buscar registro local que coincida en todos los campos clave
            match = next(
                (
                    local for local in peso_indicados_local
                    if local["nombre_caja"] == cloud["nombre_caja"]
                    and local["peso_minimo"] == cloud["peso_minimo"]
                    and local["peso_ideal"] == cloud["peso_ideal"]
                    and local["peso_maximo"] == cloud["peso_maximo"]
                    and local["tara"] == cloud["tara"]
                ),
                None
            )

            if match:
                # Existe registro idéntico → no hacer nada

                continue
            else:
                match_caja = next(
                    (
                        local for local in cajas_local
                        if local["descripcion"] == cloud["nombre_caja"]
                    ),
                    None
                )

                if match_caja:
                    # Actualizar o insertar según convenga
                    self.carta_corte_repo.update_indicated_weight(
                        peso_id=match["peso_indicado_id"] if match else None,
                        caja_id=match_caja["id"],
                        peso_minimo=cloud["peso_minimo"],
                        peso_maximo=cloud["peso_maximo"]
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
        self.sync_quality_boxes()
        # self.sync_boxes()
        # self.sync_indicated_weight()
        # self.sync_carta_corte()
        
