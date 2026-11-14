"""Fase 1 — BeautifulSoup: extracción de la ficha de producto (contenido estático)."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .utils import URL_PRODUCTO, a_entero, texto_de

SELECTORES_FICHA = {
    "titulo": "h1.ui-pdp-title",
    "condicion_ventas": "span.ui-pdp-subtitle",
    "precio_actual": ".ui-pdp-price__second-line .andes-money-amount__fraction",
    "precio_anterior": ".ui-pdp-price__second-line s .andes-money-amount__fraction",
    "descuento": ".ui-pdp-price__second-line .andes-money-amount__discount",
    "calificacion": ".ui-pdp-review__rating",
    "n_opiniones": ".ui-pdp-review__amount",
    "vendedor": ".ui-pdp-seller__link-trigger",
    "reputacion_vendedor": ".ui-pdp-seller__status-title",
    "stock": ".ui-pdp-buybox__quantity__available",
}


def _a_flotante(texto: str | None) -> float:
    try:
        return float((texto or "0").replace(",", "."))
    except ValueError:
        return 0.0


def extraer_ficha(html: str, url: str = URL_PRODUCTO) -> dict:
    """Extrae los campos de la ficha de producto con selectores CSS defensivos."""
    sopa = BeautifulSoup(html, "lxml")
    s = SELECTORES_FICHA
    ficha = {
        "titulo": texto_de(sopa, s["titulo"]),
        "condicion_ventas": texto_de(sopa, s["condicion_ventas"]),
        "precio_actual": a_entero(texto_de(sopa, s["precio_actual"])),
        "precio_anterior": a_entero(texto_de(sopa, s["precio_anterior"])),
        "descuento": texto_de(sopa, s["descuento"]),
        "calificacion": _a_flotante(texto_de(sopa, s["calificacion"])),
        "n_opiniones": a_entero(texto_de(sopa, s["n_opiniones"])),
        "vendedor": texto_de(sopa, s["vendedor"]),
        "reputacion_vendedor": texto_de(sopa, s["reputacion_vendedor"]),
        "stock": texto_de(sopa, s["stock"]),
        "categoria": " > ".join(
            a.get_text(strip=True) for a in sopa.select(".andes-breadcrumb__item a")
        ),
        "url": url,
    }
    ficha["ahorro_cop"] = (ficha["precio_anterior"] or 0) - (ficha["precio_actual"] or 0)
    return ficha


def extraer_especificaciones(html: str) -> dict[str, str]:
    """Recorre la tabla ``andes-table`` y devuelve un diccionario atributo -> valor."""
    sopa = BeautifulSoup(html, "lxml")
    especificaciones: dict[str, str] = {}
    for fila in sopa.select("table.ui-pdp-specs__table tr.andes-table__row"):
        atributo, valor = fila.select_one("th"), fila.select_one("td")
        if atributo and valor:
            especificaciones[atributo.get_text(strip=True)] = valor.get_text(strip=True)
    return especificaciones
