import socket
import re
import time

class ScaleService:
    def __init__(self):
        self.ip = '127.0.0.1'
        self.puerto = 4001
        self.socket = None


    def connect(self):
        """Establece conexión con la báscula"""
        self.close()
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1)
            self.socket.connect((self.ip, self.puerto))
            print('Conectado')
            return True


        except Exception as e:
            print("Error al conectar: {e}")
            self.socket = None
            return False


    def close(self):
        """Cierra conexión activa"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None


    def _esperar_conexion(self):
        while not self.socket:
            self.conectar()
            if not self.socket:
                print("No se pudo conectar a la báscula, reintentando en 1 segundo...")
                time.sleep(1)

    def run(self):
        self._esperar_conexion()

        try:
            while True:
                if not self.socket_activo():
                    print("Socket caído, reconectando...")
                    # logger.warning("Socket caído, reconectando...")
                    self.cerrar()
                    time.sleep(0.5)
                    self._esperar_conexion()
                    continue


                peso = self.leer_peso()
                print(f"Peso leído: {peso}")
                if peso is not None and isinstance(peso, (int, float)) and peso >= 0:
                    self.procesar_peso(peso)
                else:
                    # logger.warning("No se recibió peso, intentando reconectar...")
                    print("No se recibió peso, intentando reconectar...")
                    self.cerrar()
                    time.sleep(1)
                    self._esperar_conexion()       
                time.sleep(0.1)  # ajustar frecuencia de lectura
        except KeyboardInterrupt:
            print("Interrupción manual recibida, cerrando conexión.")
            # logger.info("Interrupción manual recibida, cerrando conexión.")
        finally:
            self.close()




    def socket_activo(self):
        if not self.socket:
            return False
        try:
            # send 0 bytes como ping, no envía datos pero valida el socket
            self.socket.send(b'')
            return True
        except:
            return False


    def get_wight(self):
        if not self.socket:  # Si no hay conexión, intenta conectar
            if not self.connect():
                return None
            
        try:
            data = self.socket.recv(1024)
            if not data:
                return None
            
            texto = data.decode("utf-8", errors="ignore").strip()
            lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
            if not lineas:
                return None
            for linea in reversed(lineas):
                match = re.search(r"[-+]?\d*\.\d+|\d+", linea)
                if match:
                    peso = float(match.group())
                    return peso
            return None
        except socket.timeout:
            self.close()
            return None
        except Exception as e:
            self.close()
            return None


