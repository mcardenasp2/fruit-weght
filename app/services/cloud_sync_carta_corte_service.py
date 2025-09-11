from app.clients.svp_client import SvpClient
from app.repositories.cloud_carta_corte_repository import CloudCartaCorteRepository
from app.repositories.carta_corte_repository import CartaCorteRepository
from app.repositories.calidad_caja_repository import CalidadCajaRepository
from app.repositories.caja_repository import CajaRepository
from app.repositories.peso_indicado_repository import PesoIndicadoRepository
from app.mappers.cut_off_letter_mapper import CutOffLetterMapper
from app.mappers.box_mapper import BoxMapper
from app.mappers.indicated_weight_mapper import IndicatedWeight

from datetime import datetime

class CloudSyncCartaCorteService:
    def __init__(self):
        try:
            self.client = SvpClient()
            # Intenta cargar desde cache
            if not self.client.load_token_from_cache():
                self.client.login()  # si no hay cache o está expirado, hace login
        except Exception:
            self.client = None

        self.cloud_carta_corte_repo = CloudCartaCorteRepository(self.client)
        self.carta_corte_repo = CartaCorteRepository()
        self.calidad_cajas_repo = CalidadCajaRepository()
        self.caja_repo = CajaRepository()
        self.peso_indicado_repo = PesoIndicadoRepository()



    def sync_quality_boxes(self):
        quality_boxes_cloud = self.cloud_carta_corte_repo.get_all_quality_boxes()
        quality_boxes_cloud = [BoxMapper.from_quality_boxes_cloud(r) for r in quality_boxes_cloud]

        quality_boxes_local = self.calidad_cajas_repo.get_all_quality_boxes()
        quality_boxes_local = [BoxMapper.from_quality_boxes_local(r) for r in quality_boxes_local]


        if quality_boxes_cloud:
            # actualizar el estado de todos a 0
            self.calidad_cajas_repo.update_quality_boxes_all()

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

        print("Termina sincronizacion calidad Cajas d")




    def sync_boxes(self):
        cajas_cloud = self.cloud_carta_corte_repo.boxes_by_location()
        cajas_cloud = [BoxMapper.from_box_cloud(r) for r in cajas_cloud]

        calidad_cajas_local = self.calidad_cajas_repo.get_all_quality_boxes()
        calidad_cajas_local = [BoxMapper.from_quality_boxes_local(r) for r in calidad_cajas_local]
        

        cajas_local = self.caja_repo.get_all_boxes()
        cajas_local = [BoxMapper.from_box_local(r) for r in cajas_local]

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
        peso_indicados_cloud = [IndicatedWeight.from_indicated_weight_cloud(r) for r in peso_indicados_cloud]

        peso_indicados_local = self.peso_indicado_repo.get_indicated_weight()
        peso_indicados_local = [IndicatedWeight.from_indicated_weight_local(r) for r in peso_indicados_local]

        
        cajas_local = self.caja_repo.get_all_boxes()
        cajas_local = [BoxMapper.from_box_local(r) for r in cajas_local]


        if peso_indicados_cloud:
            self.peso_indicado_repo.update_status_indicated_weights_all()

        # ver si se cambia el estado a todos a cero 
        for cloud in peso_indicados_cloud:
            # Buscar registro local que coincida en todos los campos clave
            match = next(
            (
                local for local in peso_indicados_local
                if local["caja"] == cloud["caja"]
                and float(local["peso_minimo"]) == float(cloud["peso_minimo"])
                and float(local["peso_ideal"]) == float(cloud["peso_ideal"])
                and float(local["peso_maximo"]) == float(cloud["peso_maximo"])
                and local["calidad_caja"] == cloud["calidad_caja"]
                and float(local["tara"]) == float(cloud["tara"])
            ),
            None
        )


            if match:
                # Existe registro idéntico → no hacer nada

                self.peso_indicado_repo.update_status_indicated_weight(match["peso_indicado_id"])

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
                    self.peso_indicado_repo.create_indicated_weight(
                        caja_id=match_caja["id"],
                        peso_minimo=cloud["peso_minimo"],
                        peso_maximo=cloud["peso_maximo"],
                        peso_ideal=cloud["peso_ideal"],
                        tara=cloud["tara"],
                        localidad_id = self.client.localidad_id
                    )


        
    
    def sync_carta_corte(self):
        print("Sincronizando carta de corte...")
        ahora = datetime.now()
        fecha_str = ahora.strftime("%Y-%m-%d")

        cutting_chart_detail_cloud = self.cloud_carta_corte_repo.get_cutting_letter_header(fecha_str)
        cutting_chart_detail_cloud = [CutOffLetterMapper.from_get_cutting_letter_header_cloud(r) for r in cutting_chart_detail_cloud]
 
        cutting_chart_detail_local = self.carta_corte_repo.get_cut_off_letter_details(fecha_str)
        cutting_chart_detail_local = [CutOffLetterMapper.from_cut_off_letter_detail_local(r) for r in cutting_chart_detail_local]

        peso_indicados_local = self.peso_indicado_repo.get_indicated_weight()
        peso_indicados_local = [IndicatedWeight.from_indicated_weight_local(r) for r in peso_indicados_local]

        cut_off_letter = self.carta_corte_repo.get_cut_off_letter(fecha_str)

        

        if cutting_chart_detail_cloud:
            self.carta_corte_repo.update_cut_off_chart_by_date(fecha_str)

            if cut_off_letter is None:
                cut_off_letter = self.carta_corte_repo.save_cut_off_chart(
                    localidad_id = self.client.localidad_id,
                    fecha = fecha_str,
                    hora = cutting_chart_detail_cloud[0]["hora"]
                )
           
        for cloud in cutting_chart_detail_cloud:
            match = next(
                (
                    local for local in cutting_chart_detail_local
                    if local["caja"] == cloud["caja"]
                    and local["calidad_caja"] == cloud["calidad_caja"]
                    and float(local["cantidad"]) == float(cloud["cantidad"])
                    and float(local["peso_minimo"]) == float(cloud["peso_minimo"])
                    and float(local["peso_ideal"]) == float(cloud["peso_ideal"])
                    and float(local["peso_maximo"]) == float(cloud["peso_maximo"])
                    # and int(local["cantidad"]) == int(cloud["cantidad"])
                    and float(local["tara"]) == float(cloud["tara"])
                ),
                None
            )


            if match:
                self.carta_corte_repo.updateStatusCutDeatil(match["corte_detalle_id"], match["cantidad"])

            else:
                match_peso_indicado = next(
                    (
                        local for local in peso_indicados_local
                        if local["caja"] == cloud["caja"]
                        and float(local["peso_minimo"]) == float(cloud["peso_minimo"])
                        and float(local["peso_ideal"]) == float(cloud["peso_ideal"])
                        and float(local["peso_maximo"]) == float(cloud["peso_maximo"])
                        and local["calidad_caja"] == cloud["calidad_caja"]
                        and float(local["tara"]) == float(cloud["tara"])
                    ),
                    None
                )

                print(f"match_peso_indicado: {match_peso_indicado}")
                if match_peso_indicado:
                    self.carta_corte_repo.save_cutting_detail(
                        corte_encabezado_id = cut_off_letter["id"],
                        peso_indicado_id = match_peso_indicado["peso_indicado_id"],
                        cantidad = cloud["cantidad"]
                    )
                else:
                    print("No se encontró peso indicado correspondiente, no se puede crear detalle de")


    

    def replicate_cut_off_weights(self, type = None):
        ahora = datetime.now()
        fecha_str = ahora.strftime("%Y-%m-%d")
        data = self.carta_corte_repo.get_data_to_replicate(tipo = type, fecha_str=fecha_str)

        if data:
            ids = self.cloud_carta_corte_repo.replicate_cut_off_weights(data)
            if ids:
                self.carta_corte_repo.update_replicated_weight_status(ids)
        


    def sync_all(self):
        self.sync_quality_boxes()
        self.sync_boxes()
        self.sync_indicated_weight()
        self.sync_carta_corte()
        
