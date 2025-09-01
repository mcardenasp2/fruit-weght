import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    def __init__(self):
        # Cargar JSON de configuración de negocio
        # config_path = Path(__file__).parent / "config.json"
        # with open(config_path, "r") as f:
        #     self.business = json.load(f)

        # Variables de entorno (infraestructura)
        self.env = {
            "db": {
                "host": os.getenv("DB_HOST"),
                "port": int(os.getenv("DB_PORT", 5432)),
                "name": os.getenv("DB_NAME"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
            },
            "bascula": {
                "ip": os.getenv("BASCULA_IP"),
                "port": int(os.getenv("BASCULA_PORT", 4001)),
            },
            "api": {
                "url": os.getenv("API_URL"),
                "username": os.getenv("USER_NAME"),
                "password": os.getenv("USER_PASSWORD"),
                "empresa": os.getenv("COMPANY_NAME"),
                "localidad": os.getenv("FARM_NAME"),
            }
        }

    def get(self, section, key=None):
        if key:
            return self.env.get(section, {}).get(key)
        return self.env.get(section)

# Instancia global
config = Config()
