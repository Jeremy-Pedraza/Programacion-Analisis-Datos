"""Fase 3 — listado de competencia.

La lógica de extracción de cada tarjeta vive aquí, independiente del motor de descarga:
la araña de Scrapy (``spiders/competencia_spider.py``) y el pipeline offline la reutilizan,
y las pruebas automatizadas la validan sin arrancar el reactor de Twisted.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from .utils import a_entero, texto_de

SELECTOR_TARJETA = "li.ui-search-layout__item"


def extraer_tarjeta(tarjeta, posicion: int) -> dict:
    """Convierte una tarjeta del listado en un registro de 11 campos."""
    precio = a_entero(texto_de(tarjeta, ".poly-price__current .andes-money-amount__fraction"))
    anterior = a_entero(
        texto_de(tarjeta, "s.andes-money-amount--previous .andes-money-amount__fraction")
    )
    envio = texto_de(tarjeta, ".poly-component__shipping") or ""
    enlace = tarjeta.select_one("a.poly-component__title")
    try:
        calificacion = float(texto_de(tarjeta, ".poly-reviews__rating") or 0)
    except ValueError:
        calificacion = 0.0
    return {
        "posicion": posicion,
        "titulo": texto_de(tarjeta, "a.poly-component__title") or "",
        "marca": texto_de(tarjeta, ".poly-component__brand") or "",
        "precio": precio,
        "precio_anterior": anterior,
        "descuento_pct": round((anterior - precio) / anterior * 100)
        if anterior and precio else None,
        "calificacion": calificacion,
        "n_opiniones": a_entero(texto_de(tarjeta, ".poly-reviews__total")),
        "envio_gratis": "gratis" in envio.lower(),
        "full": tarjeta.select_one(".poly-component__shipped-icon") is not None,
        "enlace": enlace.get("href") if enlace else None,
    }


def extraer_listado(html: str) -> list[dict]:
    """Extrae todas las tarjetas de una página de resultados."""
    sopa = BeautifulSoup(html, "lxml")
    return [
        extraer_tarjeta(tarjeta, posicion)
        for posicion, tarjeta in enumerate(sopa.select(SELECTOR_TARJETA), start=1)
    ]


def siguiente_pagina(html: str) -> str | None:
    """Devuelve el enlace de la siguiente página del listado, si existe."""
    sopa = BeautifulSoup(html, "lxml")
    enlace = sopa.select_one("a.andes-pagination__link[title='Siguiente']")
    return enlace.get("href") if enlace else None
