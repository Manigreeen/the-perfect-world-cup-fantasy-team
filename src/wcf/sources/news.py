"""Noticias de fútbol vía RSS — fuentes confiables, GRATIS y sin API key (P1: señal cualitativa
de lesiones/rotación de último momento). Reemplaza al agregador de pago de RapidAPI.

Validado 2026-06-13: BBC, Guardian y Sky Sports sirven RSS 2.0 con decenas de ítems. Reddit
r/soccer quedó fuera (su JSON exige auth → 403). Para robustez se usan 3 fuentes; si una se cae,
las demás siguen.
"""

import unicodedata
import xml.etree.ElementTree as ET
from datetime import timezone
from email.utils import parsedate_to_datetime

import requests

FEEDS = {
    "BBC Sport": "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "The Guardian": "https://www.theguardian.com/football/rss",
    "Sky Sports": "https://www.skysports.com/rss/12040",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (wcf-news)"}


def _published_ts(text) -> float:
    """Timestamp POSIX para ordenar, robusto a fechas naive vs aware. 0.0 si no parsea."""
    try:
        dt = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return 0.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def fetch_feed(name: str, url: str) -> list[dict]:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = []
    for it in root.iter("item"):
        items.append({
            "source": name,
            "title": (it.findtext("title") or "").strip(),
            "link": (it.findtext("link") or "").strip(),
            "published": it.findtext("pubDate"),
            "summary": (it.findtext("description") or "").strip(),
        })
    return items


def fetch_all() -> list[dict]:
    """Todos los feeds combinados. Una fuente caída no tumba el resto."""
    out = []
    for name, url in FEEDS.items():
        try:
            out.extend(fetch_feed(name, url))
        except (requests.RequestException, ET.ParseError):
            continue
    return out


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def filter_by_entities(items: list[dict], entities: list[str]) -> list[dict]:
    """Ítems cuyo título o resumen menciona alguna entidad (nombres de jugadores, naciones).

    Las entidades de <4 letras se ignoran para no generar ruido ('Kim', 'Diaz' cortos). Cada hit
    queda anotado con qué entidades matcheó. Ordenado por fecha de publicación (reciente primero).
    """
    pairs = [(_norm(e), e) for e in entities if len(e) >= 4]
    hits = []
    for it in items:
        haystack = _norm(f"{it['title']} {it['summary']}")
        matched = sorted({orig for ne, orig in pairs if ne in haystack})
        if matched:
            hits.append({**it, "matched": matched})
    hits.sort(key=lambda x: _published_ts(x["published"]), reverse=True)
    return hits
