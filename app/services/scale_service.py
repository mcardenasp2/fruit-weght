import threading
import socket
import re
import time

class ScaleService:
    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 4001
        self.socket = None
        self.current_weight = None
        self.running = False
        self.lock = threading.Lock()


    def connect(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.ip, self.port))
            self.socket = s
            print("[SCALE] Conectado a báscula")
            return True
        except Exception as e:
            print(f"[SCALE] Error al conectar: {e}")
            self.socket = None
            self.current_weight = None
            return False

    def listen(self):
        """Escucha datos de la báscula en un hilo"""
        while self.running:
            if not self.socket:
                # reintentar conexión cada 2 seg
                if self.connect():
                    continue
                time.sleep(2)
                continue

            try:
                data = self.socket.recv(1024)
                # print("gssggs")
                if not data:
                    continue
                texto = data.decode("utf-8", errors="ignore").strip()
                for linea in texto.splitlines():
                    match = re.search(r"[-+]?\d*\.\d+|\d+", linea)
                    if match:
                        with self.lock:
                            self.current_weight = float(match.group())
            except (socket.timeout, OSError):
                # en caso de error, forzar reconexión
                self.socket = None
                self.current_weight = None
                continue
            finally:
                time.sleep(0.01)  # evita CPU al 100%

    def start(self):
        """Inicia conexión persistente"""
        self.running = True
        hilo = threading.Thread(target=self.listen, daemon=True)
        hilo.start()

    def stop(self):
        """Detiene servicio"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None


    def get_weight(self):
        """Devuelve último peso leído (para el botón)"""
        with self.lock:
            return self.current_weight

