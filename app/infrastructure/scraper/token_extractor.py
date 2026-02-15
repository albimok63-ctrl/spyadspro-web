"""Estrae input nascosti da HTML (CSRF, lsd, __VIEWSTATE, ecc.) per POST e session-based scraping."""

from bs4 import BeautifulSoup


def extract_hidden_inputs(html_content: str) -> dict[str, str]:
    """Estrae tutti i campi input type=\"hidden\" (name -> value) dall'HTML.

    Restituisce un dizionario riutilizzabile per richieste POST e session-based scraping.
    I campi senza name o senza value vengono ignorati.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    result: dict[str, str] = {}
    for tag in soup.find_all("input", type="hidden"):
        name = tag.get("name")
        value = tag.get("value")
        if name is not None and value is not None:
            result[name] = value
    return result
