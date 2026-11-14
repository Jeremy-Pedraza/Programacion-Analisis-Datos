"""Utilidades compartidas: cabeceras HTTP, normalización y obtención de HTML."""

from __future__ import annotations

import re
import time
from pathlib import Path

import requests

# Cabeceras de un navegador real: Mercado Libre responde 403 ante el User-Agent de requests.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9",
}

URL_PRODUCTO = (
    "https://articulo.mercadolibre.com.co/"
    "MCO-1459028321-samsung-galaxy-a55-5g-256-gb-azul-oscuro-8-gb-ram-_JM"
)
URL_BUSQUEDA = "https://listado.mercadolibre.com.co/samsung-galaxy-a55"

RETARDO_SEGUNDOS = 2  # scraping responsable: una petición cada 2 s


def a_entero(texto: str | None) -> int | None:
    """Convierte un texto monetario o numérico en entero.

    >>> a_entero("$ 1.499.900")
    1499900
    >>> a_entero("(1.248)")
    1248
    >>> a_entero(None) is None
    True
    """
    if not texto:
        return None
    digitos = re.sub(r"[^0-9]", "", texto)
    return int(digitos) if digitos else None


def texto_de(raiz, selector: str) -> str | None:
    """Extracción defensiva: devuelve el texto del nodo o ``None`` si no existe."""
    if raiz is None:
        return None
    nodo = raiz.select_one(selector)
    return nodo.get_text(strip=True) if nodo else None


def obtener_html(url: str, snapshot: Path, offline: bool = True, sesion=None) -> str:
    """Devuelve el HTML desde el snapshot local (offline) o desde la web (en vivo)."""
    if offline:
        return Path(snapshot).read_text(encoding="utf-8")
    cliente = sesion or requests
    respuesta = cliente.get(url, headers=HEADERS, timeout=20)
    respuesta.raise_for_status()
    time.sleep(RETARDO_SEGUNDOS)
    return respuesta.text
