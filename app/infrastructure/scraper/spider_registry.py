"""Registry centrale degli spider disponibili. Supporto multi-spider senza modifiche all'engine."""


class SpiderRegistry:
    """Registro centralizzato degli spider: registrazione e lookup per nome."""

    def __init__(self) -> None:
        self._spiders: dict = {}

    def register(self, name: str, spider) -> None:
        """Salva lo spider nel dizionario."""
        self._spiders[name] = spider

    def get(self, name: str):
        """Restituisce lo spider oppure None."""
        return self._spiders.get(name)

    def list(self) -> list:
        """Restituisce la lista dei nomi degli spider registrati."""
        return list(self._spiders.keys())
