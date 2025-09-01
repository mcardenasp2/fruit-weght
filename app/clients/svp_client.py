import requests
import time
from app.core.config import config


class SvpClient:
    """
    Cliente profesional para consumir API de Laravel protegida por JWT.
    - Maneja login automático.
    - Renueva token antes de expirar.
    - Puede escalar a múltiples básculas usando distintos usuarios.
    """

    def __init__(self, username=None, password=None, empresa=None):
        self.token = None
        self.token_expiration = None
        # Si no se pasan credenciales, toma las del config
        self.username = username or config.get("api", "username")
        self.password = password or config.get("api", "password")
        self.empresa = empresa or config.get("api", "empresa")
        self.empresa_id = None
        self.api_url = config.get("api", "url")


    def companies(self):
        resp = requests.get(
            f"{self.api_url}/api/security/companies"
        )
        resp.raise_for_status()
        companies = resp.json()
        company = next((c for c in companies if c["nombre"] == self.empresa), None)
        if not company:
            raise ValueError(f"No se encontró la empresa '{self.empresa}' en la API.")
        
        self.empresa_id = company["id"]
        print(f"[INFO] Empresa seleccionada: {self.empresa} (ID={self.empresa_id})")


    def login(self):
        if not self.empresa_id:
            self.companies()
        """Hace login y obtiene JWT del backend."""
        resp = requests.post(
            f"{self.api_url}/api/security/login",
            data={"username": self.username, "password": self.password, "empresa_id": self.empresa_id},
            headers={"Accept": "application/json"}
        )

        try:
            resp.raise_for_status()  # lanza error si no es 2xx
            data = resp.json()
        except requests.HTTPError as e:
            print(f"[ERROR] Login fallido. Status: {resp.status_code}")
            print(resp.text)
            raise Exception("Login fallido: usuario o contraseña incorrectos") from e
        except ValueError:
            print("[ERROR] El servidor no devolvió JSON válido")
            print(resp.text)
            raise

        if not data.get("success"):
            raise Exception(f"Error de login: {data}")

        token_data = data["data"]

        self.token = token_data["token"]
        
        # login_time viene en días, convertimos a timestamp
        login_time_days = token_data.get("login_time", 15)
        # login_time_days = 60
        # print(f"TOK {self.token}")
        print(f"login_time_days {login_time_days}")
        print("----------------------------------------------------------------------------")
        self.token_expiration = time.time() + login_time_days * 86400
        # self.token_expiration = time.time() + login_time_days
        print(f"[OK] Logged in as {self.username}. Token valid for {login_time_days} days.")

    def ensure_token_valid(self):
        # print(f"token: {self.token}")
        """Si el token expira, vuelve a logear automáticamente."""
        if not self.token or time.time() >= self.token_expiration:
            print("[INFO] Token expired or missing. Logging in again...")
            self.login()

    def request(self, method, endpoint, **kwargs):
        """Hace request seguro, renueva token si es necesario."""
        self.ensure_token_valid()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        resp = requests.request(method, f"{self.api_url}{endpoint}", headers=headers, **kwargs)

        # Si Laravel devuelve 401, relogear y reintentar
        if resp.status_code == 401:
            print("[WARN] Received 401, re-login...")
            self.login()
            headers["Authorization"] = f"Bearer {self.token}"
            resp = requests.request(method, f"{self.api_url}{endpoint}", headers=headers, **kwargs)

        resp.raise_for_status()
        return resp.json()