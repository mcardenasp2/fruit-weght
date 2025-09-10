from datetime import datetime

class PesajeController:
    def __init__(self, scale_service, carta_service, cloud_service):
        self.scale_service = scale_service
        self.carta_service = carta_service
        self.cloud_service = cloud_service
        self.esperando_vacio = False

        # Intento de sincronización cloud
        try:
            self.cloud_service.sync_all()
        except Exception as e:
            print(f"[INFO] Sincronización cloud fallida: {e}")

        # Obtener cajas disponibles
        self.cajas = self.carta_service.get_cut_off_letter_details()
        self.index_caja = 0

    # ==== Manejo de cajas ====
    def caja_actual(self):
        if not self.cajas:
            return None
        return self.cajas[self.index_caja]

    def cambiar_caja(self, step=1):
        if not self.cajas:
            return None
        self.index_caja = (self.index_caja + step) % len(self.cajas)
        return self.caja_actual()

    # ==== Pesaje ====
    def pesar(self):
        peso = self.scale_service.get_weight()
        if peso is None:
            return None, "⚠ Error al obtener el peso"

        if self.esperando_vacio:
            return None, "⚠ Cambie de caja"

        caja = self.caja_actual()
        if caja and peso < caja["peso_minimo"]:
            return None, "⚠ Peso insuficiente"

        return peso, "OK"



    def guardar_peso(self):
        """Valida, guarda en DB y retorna info lista para UI"""
        peso, mensaje = self.pesar()
        if not peso:
            return None, mensaje

        # Guardar en DB (usamos carta_service)
        caja = self.caja_actual()

        registro = self.carta_service.save_weight(
            {
                "corte_detalle_id":  caja["corte_detalle_id"],
                "cantidad": peso,
                "fecha" :datetime.now().strftime("%Y-%m-%d"),
                "hora": datetime.now().strftime("%H:%M:%S")
            }
        )

        self.esperando_vacio = True

        return registro, "✅ Peso guardado"
            

        # Podrías sincronizar con la nube aquí
        # self.cloud.sync(registro)

        # Bloquear hasta que quede vacío
        


    def resetear_espera(self, peso_actual, peso_vacio=1.0):
        if self.esperando_vacio and peso_actual < peso_vacio:
            self.esperando_vacio = False
