"""Parser HTML: BeautifulSoup con html.parser. Nessuna richiesta HTTP né DB."""

from bs4 import BeautifulSoup
from bs4.element import Tag


class HtmlParser:
    """Parsing HTML da stringa: trova elementi per tag/classe, estrae testo. Indipendente e riutilizzabile."""

    def __init__(self, html: str) -> None:
        self._soup = BeautifulSoup(html, "html.parser")

    def find_by_tag(self, tag: str) -> list[Tag]:
        """Restituisce tutti gli elementi con il tag indicato."""
        return self._soup.find_all(tag)

    def find_all_by_tag(self, tag_name: str) -> list:
        """Restituisce tutti i tag trovati con find_all(tag_name); lista vuota se non trovati."""
        return self._soup.find_all(tag_name)

    def find_all_by_attribute(self, tag: str, attribute: str, value: str) -> list:
        """Restituisce tutti gli elementi con tag e attributo=valore; lista vuota se non trovati."""
        return self._soup.find_all(tag, attrs={attribute: value})

    def find_by_class(self, class_name: str, tag: str | None = None) -> list[Tag]:
        """Restituisce tutti gli elementi con la classe indicata; opzionale filtro per tag."""
        if tag is None:
            return self._soup.find_all(class_=class_name)
        return self._soup.find_all(tag, class_=class_name)

    def get_title(self) -> str | None:
        """Restituisce il contenuto del tag <title> se presente, None altrimenti."""
        title = self._soup.find("title")
        return title.get_text(strip=True) if title else None

    @staticmethod
    def extract_text(element: Tag) -> str:
        """Estrae il testo da un elemento (es. risultato di find_by_tag / find_by_class)."""
        return element.get_text(strip=True)
