import tkinter as tk
from datetime import datetime
import random
from app.services.scale_service import ScaleService
from app.clients.svp_client import SvpClient
from app.services.cloud_sync_carta_corte_service import CloudSyncCartaCorteService
from app.services.carta_corte_service import CartaCorteService
from app.mappers.cut_off_letter_local_mapper import CutOffLetterLocalMapper

# Detección de simulación
try:
    from gpiozero import Button
    SIMULACION = platform.system() != "Linux"  # Solo real en Linux (Raspberry)
except ImportError:
    SIMULACION = True


class MockButton:
    def __init__(self):
        self.when_pressed = None
        self.when_press_the_left_button = None
        self.when_press_the_right_button = None
        self.when_released = None

    def press(self):
        if self.when_pressed:
            self.when_pressed()
    

    def press_the_left_button(self):
        if self.when_pressed:
            self.when_pressed()


    def press_the_right_button(self):
        if self.when_pressed:
            self.when_pressed()


    def press_the_save_button(self):
        if self.when_pressed:
            self.when_pressed()


    def release(self):
        if self.when_released:
            self.when_released()


class PantallaPesaje:
    def __init__(self, controller):

        self.controller = controller

        self.esperando_vacio = False

        self.service = ScaleService()
        self.service.start()

        # self.cloud_service = CloudSyncCartaCorteService()

        # self.carta_corte_service = CartaCorteService()

        # # intento sincronizar cloud -> local
        # try:
        #     print("[INFO] Iniciando sincronización cloud...")
        #     self.cloud_service.sync_all()
        # except Exception as e:
        #     print(f"[INFO] Sincronización cloud no disponible {e}")

        # Obtener datos de corte Detalle
        # self.cajas = self.carta_corte_service.get_cut_off_letter_details()

        # self.cajas = [CutOffLetterLocalMapper.from_cut_off_letter_detail_local(r) for r in self.cajas]



        self.cajas = []
        print(f"cajas: {self.cajas}")


        self.index_caja = 0

        


        if SIMULACION:
            print("Simulación de botón activada")
            self.boton = MockButton()
        else:
            self.boton = Button(17)

        self.boton.when_pressed = self.save_weight
        # self.boton.when_press_the_left_button = self.change_box
        # self.boton.when_press_the_right_button = self.change_box

        


        self.root = tk.Tk()
        # Tecla espacio -> simula botón
        # self.root.bind("<space>", lambda e: self.boton.press())

                # Flecha izquierda -> hacer algo
        # self.root.bind("<Left>", lambda e: self.update_box(-1))
        # self.root.bind("<Right>", lambda e: self.update_box(1))
        # self.root.bind("<Escape>", lambda e: self.root.destroy())


        self.root.title("Pantalla de Pesaje")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)

        # ====== Frame superior (40% altura) ======
        self.frame_superior = tk.Frame(self.root, bg="black")
        self.frame_superior.place(relx=0, rely=0, relwidth=1, relheight=0.3)

        # ====== Texto de la caja ======
        texto_caja = "SELVATICA SUPREME COMPAGNIE FRUITIERE (40.79) SIN ETIQUETA"
        texto_caja = self.truncar_texto(texto_caja, 40)  # aumenté el límite

         # Mostrar primera caja
        # texto_caja = self.obtener_nombre_caja()

        font_size = 70
        self.label_caja = tk.Label(
            self.frame_superior,
            text="",
            font=("Arial", font_size, "bold"),
            fg="white",
            bg="black",
            wraplength=self.frame_superior.winfo_screenwidth() - 100,  # permite varias líneas
            justify="center",   # centrado si hay varias líneas
        )
        # expand=True + fill="both" hace que el Label se ajuste al frame y no se corte
        self.label_caja.pack(expand=True, fill="both", pady=20)


        # ====== Frame inferior (60% altura) ======
        frame_inferior = tk.Frame(self.root, bg="black")
        frame_inferior.place(relx=0, rely=0.3, relwidth=1, relheight=0.7)

        # ====== Columna izquierda -> Peso mínimo ======
        frame_izquierda = tk.Frame(frame_inferior, bg="black")
        frame_izquierda.pack(side="left", expand=True, fill="both", padx=50, pady=5)

        self.label_minimo_text = tk.Label(
            frame_izquierda,
            text="Peso mínimo",
            font=("Arial", 40, "bold"),
            fg="yellow",
            bg="black"
        )
        self.label_minimo_text.pack()

        # peso_minimo_valor =  self.obtener_peso_minimo()

        self.label_minimo_valor = tk.Label(
            frame_izquierda,
            text='',
            font=("Arial", 170, "bold"),
            fg="yellow",
            bg="black"
        )
        self.label_minimo_valor.pack()

        # ====== Columna derecha -> Último peso + hora ======
        frame_derecha = tk.Frame(frame_inferior, bg="black")
        frame_derecha.pack(side="right", expand=True, fill="both", padx=50, pady=5)

        self.label_peso = tk.Label(
            frame_derecha,
            text="0.00",
            font=("Arial", 100, "bold"),
            fg="lime",
            bg="black"
        )
        self.label_peso.pack(pady=20)

        self.label_hora = tk.Label(
            frame_derecha,
            text="Hora: --:--:--",
            font=("Arial", 35),
            fg="white",
            bg="black"
        )
        self.label_hora.pack(pady=10)

        # ====== Mensaje de alerta (abajo centrado) ======
        self.label_alerta = tk.Label(
            self.root,
            text="",
            font=("Arial", 45, "bold"),
            fg="red",
            bg="black"
        )
        self.label_alerta.place(relx=0.5, rely=0.80, anchor="center")

         # ==== Teclas ====
        self.root.bind("<space>", lambda e: self.save_weight())
        self.root.bind("<Left>", lambda e: self.update_box(-1))
        self.root.bind("<Right>", lambda e: self.update_box(1))
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Mostrar la primera caja
        self.update_box(0)


        self.actualizar_peso()


        # Salida con ESC
        # self.root.bind("<Escape>", lambda e: self.root.destroy())

    def truncar_texto(self, texto, max_chars=60):
        if len(texto) > max_chars:
            return texto[:max_chars - 3] + "..."
        return texto



    def save_weight(self):
        peso_minimo = 20.00
        # peso = self.service.get_weight()
        peso_actual = self.service.get_weight()
        if peso_actual is None:
            self.label_alerta.config(text="⚠ Error al Obtener el Peso", fg="red")
            return
        # if peso_actual is not None:
        if self.esperando_vacio:
            self.label_alerta.config(text="⚠ Cambie de Caja", fg="red")
            print(" Esperando que la báscula vuelva a cero")
            return

        if peso_actual < peso_minimo:
            self.label_alerta.config(text="⚠ Peso insuficiente", fg="red")
            return


        self.label_peso.config(text=f"{peso_actual:.2f}")
        self.label_hora.config(text="Hora: " + datetime.now().strftime("%H:%M:%S"))
        self.label_alerta.config(text="Peso Guardado", fg="green")
        self.esperando_vacio = True


    def actualizar_peso(self):
        peso_actual = self.controller.scale_service.get_weight()
        self.controller.resetear_espera(peso_actual)
        self.root.after(100, self.actualizar_peso)

    # def actualizar_peso(self):
    #     peso_minimo = 20.0
    #     peso_vacio = 1.0  # tolerancia para considerar cero
    #     peso_actual = self.service.get_weight()

    #     if peso_actual is not None and self.esperando_vacio:
    #         if peso_actual < peso_vacio:
    #             self.esperando_vacio = False
    #             # Aquí opcionalmente podrías mostrar un mensaje temporal en UI
    #             # self.label_alerta.config(text="Báscula lista", fg="lime")

    #     # Repite cada 100 ms
    #     self.root.after(100, self.actualizar_peso)


    # def caja_actual(self):
    #     """Devuelve la caja actual o None si no hay cajas."""
    #     if not self.cajas:
    #         return None
    #     return self.cajas[self.index_caja]
    

    # def obtener_nombre_caja(self):
    #     caja = self.caja_actual()
    #     if not caja:
    #         return "SIN CAJAS DISPONIBLES"
    #     return self.truncar_texto(caja["caja"], 40)

    # def obtener_peso_minimo(self):
    #     caja = self.caja_actual()
    #     return caja["peso_minimo"] if caja else "0.0"
    

    def update_box(self, step):
        caja = self.controller.cambiar_caja(step)
        if caja:
            name = self.truncar_texto(caja["caja"], 40)
            self.label_caja.config(text=name)
            self.label_minimo_valor.config(text=caja["peso_minimo"])
        else:
            self.label_caja.config(text="SIN CAJAS DISPONIBLES")
            self.label_minimo_valor.config(text="0.0")


    # def change_box(self, type=None):
    #     if not self.cajas:  # Lista vacía
    #         self.label_caja.config(text="SIN CAJAS DISPONIBLES")
    #         self.label_minimo_valor.config(text="0.0")
    #         return

    #     # Determinar dirección según el tipo (default avanzar)
    #     step = 1 if type == "sumar" else -1

    #     # Actualizar índice de forma cíclica
    #     self.index_caja = (self.index_caja + step) % len(self.cajas)

    #     # Refrescar labels
    #     self.label_caja.config(text=self.obtener_nombre_caja())
    #     self.label_minimo_valor.config(text=self.obtener_peso_minimo())


    def run(self):
        self.root.mainloop()