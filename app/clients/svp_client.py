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
        self.localidad = empresa or config.get("api", "localidad")
        self.empresa_id = None
        self.localidad_id = None
        self.api_url = config.get("api", "url")


    def companies(self):
        resp = requests.get(
            f"{self.api_url}/api/security/companies",
            verify=False
        )
        resp.raise_for_status()
        companies = resp.json()
        company = next((c for c in companies if c["nombre"] == self.empresa), None)
        if not company:
            raise ValueError(f"No se encontró la empresa '{self.empresa}' en la API.")
        
        self.empresa_id = company["id"]
        print(f"[INFO] Empresa seleccionada: {self.empresa} (ID={self.empresa_id})")


    def login(self):
        try:
            if not self.empresa_id:
                self.companies()
                self.set_location()
            resp = requests.post(
                f"{self.api_url}/api/security/login",
                data={"username": self.username, "password": self.password, "empresa_id": self.empresa_id},
                headers={"Accept": "application/json"},
                verify=False
            )
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success"):
                raise Exception(f"Error de login: {data}")

            token_data = data["data"]
            self.token = token_data["token"]
            login_time_days = token_data.get("login_time", 15)
            self.token_expiration = time.time() + login_time_days * 86400
            print(f"[OK] Logged in as {self.username}. Token valid for {login_time_days} days.")

        except Exception as e:
            print(f"[WARN] No se pudo conectar a la API: {e}")
            self.token = None
            self.token_expiration = None


    def ensure_token_valid(self):
        # print(f"token: {self.token}")
        """Si el token expira, vuelve a logear automáticamente."""
        if not self.token or time.time() >= self.token_expiration:
            print("[INFO] Token expired or missing. Logging in again...")
            self.login()

    def request(self, method, endpoint, **kwargs):
        try:
            self.ensure_token_valid()
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self.token}" if self.token else ""
            resp = requests.request(method, f"{self.api_url}{endpoint}", headers=headers, **kwargs)

            if resp.status_code == 401:
                print("[WARN] Received 401, re-login...")
                self.login()
                headers["Authorization"] = f"Bearer {self.token}" if self.token else ""
                resp = requests.request(method, f"{self.api_url}{endpoint}", headers=headers, **kwargs)

            resp.raise_for_status()
            return resp.json()

        except Exception as e:
            print(f"[WARN] Request fallido, se ignorará temporalmente: {e}")
            return None
        

    def set_location(self):
        try:
            resp = requests.get(
                f"{self.api_url}/api/security/locations?per_page=all",
                verify=False
            )  

            resp.raise_for_status()
            locations = resp.json()

            print(f"Locations: {locations}")

            if not locations.get("success"):
                raise Exception(f"Error de login: {locations}")
            
            location = next((c for c in locations if c["nombre"] == self.localidad), None)
            if not location:
                raise ValueError(f"No se encontró la empresa '{self.localidad}' en la API.")
            self.localidad_id = location["id"]

            print(f"LOCALIDAD ID: {self.localidad_id}")

        except Exception as e:
            print(f"[WARN] No se pudo conectar a la API: {e}")
        
            
            
