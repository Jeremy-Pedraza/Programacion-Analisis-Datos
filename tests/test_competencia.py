from bs4 import BeautifulSoup

from ml_scraper.competencia import extraer_listado, extraer_tarjeta, siguiente_pagina

CAMPOS = {"posicion", "titulo", "marca", "precio", "precio_anterior", "descuento_pct",
          "calificacion", "n_opiniones", "envio_gratis", "full", "enlace"}


def test_listado_cobertura_y_esquema(html_resultados):
    registros = extraer_listado(html_resultados)
    assert len(registros) >= 10
    assert all(set(r) == CAMPOS for r in registros)
    assert [r["posicion"] for r in registros] == list(range(1, len(registros) + 1))
    assert all(isinstance(r["precio"], int) and r["precio"] > 0 for r in registros)


def test_descuento_calculado_correctamente(html_resultados):
    for r in extraer_listado(html_resultados):
        if r["precio_anterior"]:
            esperado = round((r["precio_anterior"] - r["precio"]) / r["precio_anterior"] * 100)
            assert r["descuento_pct"] == esperado


def test_tarjeta_incompleta_no_rompe():
    tarjeta = BeautifulSoup("<li class='ui-search-layout__item'></li>", "lxml").li
    r = extraer_tarjeta(tarjeta, 1)
    assert r["precio"] is None and r["descuento_pct"] is None
    assert r["envio_gratis"] is False and r["full"] is False and r["enlace"] is None


def test_paginacion():
    html = '<a class="andes-pagination__link" title="Siguiente" href="/p2">›</a>'
    assert siguiente_pagina(html) == "/p2"
    assert siguiente_pagina("<html></html>") is None
