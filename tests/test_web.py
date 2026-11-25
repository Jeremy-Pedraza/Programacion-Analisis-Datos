"""Pruebas de la aplicación web (FastAPI) que se despliega como servicio en la nube."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ml_scraper.web import app

cliente = TestClient(app)


def test_health_responde_ok():
    """El endpoint de salud debe responder 200 con estado 'ok' (lo usa el smoke test del CD)."""
    r = cliente.get("/health")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["status"] == "ok"
    assert cuerpo["version"]
    assert cuerpo["modo_datos"] in {"snapshot", "en-vivo"}


def test_tablero_contiene_el_articulo():
    """La página principal debe renderizar HTML con el artículo analizado."""
    r = cliente.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Galaxy A55" in r.text


def test_api_indicadores_expone_la_conclusion_de_negocio():
    """La API de indicadores debe conservar la conclusión de la EA1 (+17,05 % sobre el promedio)."""
    r = cliente.get("/api/indicadores")
    assert r.status_code == 200
    ind = r.json()
    assert ind["Desviación vs. promedio (%)"] == pytest.approx(17.05, abs=0.01)
    assert ind["Artículos rastreados"] >= 10


def test_api_producto_incluye_ficha_y_especificaciones():
    r = cliente.get("/api/producto")
    assert r.status_code == 200
    cuerpo = r.json()
    assert "ficha" in cuerpo and "especificaciones" in cuerpo
    assert cuerpo["ficha"]["titulo"]
    assert len(cuerpo["especificaciones"]) >= 5


def test_api_competencia_devuelve_el_listado():
    r = cliente.get("/api/competencia")
    assert r.status_code == 200
    registros = r.json()
    assert isinstance(registros, list) and len(registros) >= 10
    assert {"titulo", "precio"} <= set(registros[0])


def test_api_metricas_todas_cumplen():
    r = cliente.get("/api/metricas")
    assert r.status_code == 200
    filas = r.json()
    assert all(fila["Cumple"] for fila in filas)


def test_grafica_png_disponible():
    r = cliente.get("/grafica.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"
