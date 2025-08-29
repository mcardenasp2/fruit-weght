import tkinter as tk
from datetime import datetime
import random

class PantallaPesaje:
    def __init__(self, root):
        self.root = root
        self.root.title("Pantalla de Pesaje")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)

        # ====== Frame superior (40% altura) ======
        self.frame_superior = tk.Frame(root, bg="black")
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
        frame_inferior = tk.Frame(root, bg="black")
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
            root,
            text="",
            font=("Arial", 45, "bold"),
            fg="red",
            bg="black"
        )
        self.label_alerta.place(relx=0.5, rely=0.80, anchor="center")

        # Simulación de pesos
        self.simular_peso()

        # Salida con ESC
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def truncar_texto(self, texto, max_chars=60):
        if len(texto) > max_chars:
            return texto[:max_chars - 3] + "..."
        return texto

    def scroll_marquee(self, ancho_texto):
        # mueve las dos etiquetas
        self.x1 -= 2  # velocidad
        if self.x1 <= -(ancho_texto + self.espacio_extra):
            self.x1 = 0
        self.marquee_label1.place(x=self.x1, y=50)
        self.marquee_label2.place(x=self.x1 + ancho_texto + self.espacio_extra, y=50)
        self.root.after(20, lambda: self.scroll_marquee(ancho_texto))

    def simular_peso(self):
        # Simula lectura de peso
        peso = round(random.uniform(35, 45), 2)
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

if __name__ == "__main__":
    root = tk.Tk()
    app = PantallaPesaje(root)
    root.mainloop()
