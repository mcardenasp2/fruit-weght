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

        self.index_caja = 0

        self.root = tk.Tk()

        self.root.title("Pantalla de Pesaje")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)

        # ====== Frame superior (40% altura) ======
        self.frame_superior = tk.Frame(self.root, bg="black")
        self.frame_superior.place(relx=0, rely=0, relwidth=1, relheight=0.3)

        # ====== Texto de la caja ======
        texto_caja = "SELVATICA SUPREME COMPAGNIE FRUITIERE (40.79) SIN ETIQUETA"
        texto_caja = self.truncar_texto(texto_caja, 40)  # aumenté el límite

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

        self.label_minimo_valor = tk.Label(
            frame_izquierda,
            text='0.00',
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


    def truncar_texto(self, texto, max_chars=60):
        if len(texto) > max_chars:
            return texto[:max_chars - 3] + "..."
        return texto


    def save_weight(self):
        registro, mensaje = self.controller.guardar_peso()
        if registro:
            self.label_peso.config(text=f"{registro['cantidad']:.2f}")
            self.label_hora.config(text="Hora: " + registro["hora"].strftime("%H:%M:%S"))
            self.label_alerta.config(text=mensaje, fg="green")
        else:
            self.label_alerta.config(text=mensaje, fg="red")


    def actualizar_peso(self):
        peso_actual = self.controller.scale_service.get_weight()
        self.controller.resetear_espera(peso_actual)
        self.root.after(100, self.actualizar_peso)


    def update_box(self, step):
        caja = self.controller.cambiar_caja(step)
        if caja:
            name = self.truncar_texto(caja["caja"], 40)
            self.label_caja.config(text=name)
            self.label_minimo_valor.config(text=caja["peso_minimo"])
        else:
            self.label_caja.config(text="SIN CAJAS DISPONIBLES")
            self.label_minimo_valor.config(text="0.0")



    def run(self):
        self.root.mainloop()