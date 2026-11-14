"""Fase 2 — Selenium: opiniones de compradores renderizadas por JavaScript."""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from .utils import HEADERS, a_entero, texto_de

SELECTOR_RESENAS = "section.ui-review-capability"
SELECTOR_COMENTARIO = ".ui-review-capability-comments__comment"


def html_con_selenium(
    url: str, snapshot: Path, offline: bool = True, espera: int = 15
) -> tuple[str, str]:
    """Devuelve ``(html, motor)``. Usa Chrome headless; si no hay navegador, usa el snapshot.

    El import de Selenium es diferido para que el paquete funcione (y se pruebe en CI)
    aunque Selenium o Chrome no estén instalados.
    """
    navegador = None
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        opciones = Options()
        for argumento in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                          "--window-size=1920,1080", f"user-agent={HEADERS['User-Agent']}"):
            opciones.add_argument(argumento)
        navegador = webdriver.Chrome(options=opciones)
        navegador.get(Path(snapshot).resolve().as_uri() if offline else url)
        WebDriverWait(navegador, espera).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_RESENAS))
        )
        navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return navegador.page_source, "Selenium + Chrome headless"
    except Exception:  # noqa: BLE001 - cualquier fallo del navegador activa el respaldo
        return Path(snapshot).read_text(encoding="utf-8"), "snapshot (fallback)"
    finally:
        if navegador is not None:
            navegador.quit()


def extraer_resenas(html: str) -> list[dict]:
    """Extrae comentario y estrellas de cada opinión presente en el DOM."""
    sopa = BeautifulSoup(html, "lxml")
    resenas = []
    for nodo in sopa.select(SELECTOR_COMENTARIO):
        resenas.append({
            "comentario": texto_de(nodo, ".ui-review-capability-comments__comment__content"),
            "estrellas": a_entero(
                texto_de(nodo, ".ui-review-capability-comments__comment__rating")
            ) or 0,
        })
    return resenas
