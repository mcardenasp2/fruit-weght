import threading
import time
from datetime import date

class ReplicatorService:
    def __init__(self, cloud_service, interval_today=5, interval_history=60):
        """
        :param cloud_service: instancia de CloudSyncCartaCorteService
        :param interval_today: segundos entre replicaciones de hoy
        :param interval_history: segundos entre replicaciones históricas
        """
        self.cloud_service = cloud_service
        self.interval_today = interval_today
        self.interval_history = interval_history

        self._stop_event = threading.Event()

        # Hilos independientes
        self.today_thread = threading.Thread(target=self._run_today, daemon=True)
        self.history_thread = threading.Thread(target=self._run_history, daemon=True)

        self._is_running_today = False
        self._is_running_history = False

    def start(self):
        print("[INFO] Replicador iniciado")
        self.today_thread.start()
        self.history_thread.start()

    def _run_today(self):
        """Replicación en tiempo real (día actual)"""
        while not self._stop_event.is_set():
            if not self._is_running_today:
                self._is_running_today = True
                try:
                    print("[INFO] Replicando datos de HOY...")
                    self.cloud_service.replicate_cut_off_weights('actual')
                except Exception as e:
                    print(f"[ERROR] Replicación HOY fallida: {e}")
                finally:
                    self._is_running_today = False
            time.sleep(self.interval_today)

    def _run_history(self):
        """Replicación de fechas anteriores"""
        while not self._stop_event.is_set():
            if not self._is_running_history:
                self._is_running_history = True
                try:
                    print("[INFO] Replicando HISTÓRICO...")
                    self.cloud_service.replicate_cut_off_weights('historico')
                except Exception as e:
                    print(f"[ERROR] Replicación HISTÓRICA fallida: {e}")
                finally:
                    self._is_running_history = False
            time.sleep(self.interval_history)

    def stop(self):
        print("[INFO] Deteniendo replicador...")
        self._stop_event.set()
        self.today_thread.join()
        self.history_thread.join()
