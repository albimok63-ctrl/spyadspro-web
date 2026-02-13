"""Scheduler minimale per esecuzione periodica di un job (es. spider)."""

import threading
import time


class SimpleScheduler:
    """Esegue un job periodicamente in un thread separato."""

    def start(self, interval_seconds: int, job) -> None:
        """Avvia un thread separato che esegue job() ogni interval_seconds secondi."""

        def run_loop() -> None:
            while True:
                job()
                time.sleep(interval_seconds)

        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
