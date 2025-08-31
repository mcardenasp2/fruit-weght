import tkinter as tk
from datetime import datetime
import random
from app.services.scale_service import ScaleService

# Detección de simulación
try:
    from gpiozero import Button
    SIMULACION = platform.system() != "Linux"  # Solo real en Linux (Raspberry)
except ImportError:
    SIMULACION = True


class MockButton:
    def __init__(self):
        self.when_pressed = None
        self.when_released = None

    def press(self):
        if self.when_pressed:
            self.when_pressed()

    def release(self):
        if self.when_released:
            self.when_released()


class PantallaPesaje:
    def __init__(self):

        self.esperando_vacio = False

        self.service = ScaleService()
        self.service.start()

        if SIMULACION:
            print("Simulación de botón activada")
            self.boton = MockButton()
        else:
            self.boton = Button(17)

        self.boton.when_pressed = self.save_weight

        


        self.root = tk.Tk()
        # Tecla espacio -> simula botón
        self.root.bind("<space>", lambda e: self.boton.press())

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
            text=texto_caja,
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
            text="40.00",
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



        self.actualizar_peso()

        # Simulación de pesos
        # self.simular_peso()

        # self.save_weight()

        # Salida con ESC
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def truncar_texto(self, texto, max_chars=60):
        if len(texto) > max_chars:
            return texto[:max_chars - 3] + "..."
        return texto



    def simular_peso(self):
        # Simula lectura de peso
        peso = round(random.uniform(35, 45), 2)

        print(peso)
        peso_minimo = 40.00

        # Actualiza pantalla
        self.label_peso.config(text=f"{peso}")
        self.label_hora.config(text="Hora: " + datetime.now().strftime("%H:%M:%S"))

        # Validar alerta
        if peso < peso_minimo:
            self.label_alerta.config(text="⚠ Peso insuficiente")
        else:
            self.label_alerta.config(text="")

        # Repite cada 2 segundos
        self.root.after(2000, self.simular_peso)


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

        # if peso_actual > peso_minimo:
        # print(f"Ok Peso registrado: {peso_actual}")
        # self.guardar_en_db(peso_actual)
        # Actualiza UI
        self.label_peso.config(text=f"{peso_actual:.2f}")
        self.label_hora.config(text="Hora: " + datetime.now().strftime("%H:%M:%S"))
        self.label_alerta.config(text="Peso Guardado", fg="green")
        self.esperando_vacio = True
        # else :
        #     self.label_alerta.config(text="⚠ Peso insuficiente", fg="red")
        # else:
        #     self.label_alerta.config(text="⚠ Error al Obtener el Peso")
        #     print("No se pudo leer peso (reintentando)")
        # print(value)

        # self.root.after(2000, self.save_weight)


    def actualizar_peso(self):
        peso_minimo = 20.0
        peso_vacio = 1.0  # tolerancia para considerar cero
        peso_actual = self.service.get_weight()

        if peso_actual is not None and self.esperando_vacio:
            if peso_actual < peso_vacio:
                self.esperando_vacio = False
                # Aquí opcionalmente podrías mostrar un mensaje temporal en UI
                # self.label_alerta.config(text="Báscula lista", fg="lime")

        # Repite cada 100 ms
        self.root.after(100, self.actualizar_peso)


    def run(self):
        self.root.mainloop()