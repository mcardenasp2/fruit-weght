import requests
import time
import random
import json, os
from app.core.config import config

TOKEN_CACHE_FILE = "token.json"

class SvpClient:
    """
    Cliente profesional para consumir API de Laravel protegida por JWT.
    - Maneja login automático.
    - Renueva token antes de expirar.
    - Cachea token en disco.
    - Reintenta requests con backoff exponencial.
    """

    def __init__(self, username=None, password=None, empresa=None, localidad=None):
        self.token = None
        self.token_expiration = None
        self.username = username or config.get("api", "username")
        self.password = password or config.get("api", "password")
        self.empresa = empresa or config.get("api", "empresa")
        self.localidad = localidad or config.get("api", "localidad")
        self.empresa_id = None
        self.localidad_id = None
        self.api_url = config.get("api", "url")

        # intenta cargar token guardado
        self.load_token_from_cache()

    # ------------------------
    # MÉTODOS DE LOGIN / CACHE
    # ------------------------
    def companies(self):
        resp = requests.get(f"{self.api_url}/api/security/companies", verify=False)
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
            self.save_token_to_cache()

        except Exception as e:
            print(f"[WARN] No se pudo conectar a la API: {e}")
            self.token = None
            self.token_expiration = None

    def ensure_token_valid(self):
        if not self.token or time.time() >= self.token_expiration:
            print("[INFO] Token expired or missing. Logging in again...")
            self.login()

    def load_token_from_cache(self):
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, "r") as f:
                data = json.load(f)
                if data["expires_at"] > time.time():
                    self.token = data["token"]
                    self.token_expiration = data["expires_at"]
                    self.localidad_id = data["localidad_id"]
                    print("[INFO] Token cargado desde cache.")
                    return True
        return False

    def save_token_to_cache(self):
        with open(TOKEN_CACHE_FILE, "w") as f:
            json.dump({
                "token": self.token,
                "expires_at": self.token_expiration,
                "localidad_id": self.localidad_id
            }, f)

    # ------------------------
    # REQUESTS
    # ------------------------
    def request(self, method, endpoint, **kwargs):
        try:
            self.ensure_token_valid()
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self.token}" if self.token else ""
            # Si endpoint ya es una URL completa, úsala tal cual
            if endpoint.startswith("http://") or endpoint.startswith("https://"):
                url = endpoint
            else:
                url = f"{self.api_url}{endpoint}"
                
            resp = requests.request(method, url, headers=headers, **kwargs)

            if resp.status_code == 401:
                print("[WARN] Received 401, re-login...")
                self.login()
                headers["Authorization"] = f"Bearer {self.token}" if self.token else ""
                resp = requests.request(method, f"{self.api_url}{endpoint}", headers=headers, **kwargs)

            resp.raise_for_status()
            return resp.json()

        except Exception as e:
            print(f"[WARN] Request fallido: {e}")
            return None

    def retry_request(self, method, endpoint, retries=3, **kwargs):
        """Hace un request con reintentos y backoff exponencial."""
        for intento in range(retries):
            resp = self.request(method, endpoint, **kwargs)
            if resp:
                return resp
            wait = 2 ** intento + random.random()
            print(f"[INFO] Reintentando en {wait:.1f}s...")
            time.sleep(wait)
        print("[ERROR] No se pudo completar la petición tras varios intentos.")
        return None

    # ------------------------
    # LOCALIDAD
    # ------------------------
    def set_location(self):
        try:
            print(f"{self.api_url}/api/security/locations?per_page=all")
            locations = self.request('GET',f"{self.api_url}/api/security/locations?per_page=all", verify=False)
            
            if locations:
                location = next((c for c in locations if c["descripcion"] == self.localidad), None)
                if not location:
                    raise ValueError(f"No se encontró la localidad '{self.localidad}' en la API.")

                self.localidad_id = location["id"]

            print(f"[INFO] Localidad seleccionada: {self.localidad} (ID={self.localidad_id})")

        except Exception as e:
            print(f"[WARN] No se pudo conectar a la API Localidad: {e}")
