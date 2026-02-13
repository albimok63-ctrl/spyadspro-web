"""ScraperEngine: esecuzione spider passato come parametro, normalizzazione e pipeline."""

from app.infrastructure.scraper.http_client import HttpClient
from app.infrastructure.scraper.normalizer import ScraperNormalizer
from app.infrastructure.scraper.pipeline import ScraperPipeline
from app.infrastructure.scraper.result_store import ResultStore


class ScraperEngine:
    """Esegue più spider registrati, aggrega risultati in pipeline e result_store."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
        self.normalizer = ScraperNormalizer()
        self.pipeline = ScraperPipeline()
        self.result_store = ResultStore()
        self.spiders: list = []

    def register_spider(self, spider) -> None:
        """Aggiunge lo spider alla lista degli spider registrati."""
        self.spiders.append(spider)

    def _to_dict(self, result) -> dict:
        """Converte il risultato dello spider in dict per pipeline/normalizer."""
        if isinstance(result, dict):
            return result
        if hasattr(result, "data") and hasattr(result, "url"):
            data = getattr(result, "data") or {}
            return {
                "source": getattr(result, "source", ""),
                "url": result.url,
                "title": data.get("title"),
                "description": data.get("meta_description") or data.get("description"),
            }
        return {}

    def run(self, url: str) -> list:
        """Esegue tutti gli spider registrati; output sempre con schema {source, data}. Duplicati (pipeline None) esclusi."""
        results_list: list = []
        for spider in self.spiders:
            result = spider.run(url)
            data = self._to_dict(result)
            processed = self.pipeline.process(data)
            if processed is None:
                continue
            if "data" not in processed:
                stable = {"source": spider.__class__.__name__, "data": processed}
            else:
                stable = processed
            normalized = self.normalizer.normalize(
                stable["data"],
                source=stable.get("source") or spider.__class__.__name__,
            )
            if normalized is not None:
                stable["data"] = normalized
            self.result_store.add(stable)
            results_list.append(stable)
        return results_list
