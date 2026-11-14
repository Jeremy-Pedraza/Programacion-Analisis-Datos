from ml_scraper.producto import extraer_especificaciones, extraer_ficha


def test_ficha_campos_principales(ficha):
    assert "Galaxy A55" in ficha["titulo"]
    assert ficha["precio_actual"] == 1_499_900
    assert ficha["precio_anterior"] == 1_899_900
    assert ficha["ahorro_cop"] == 400_000
    assert 0 < ficha["calificacion"] <= 5
    assert ficha["n_opiniones"] > 0
    assert ficha["vendedor"]


def test_ficha_cobertura_minima(ficha, html_producto):
    especificaciones = extraer_especificaciones(html_producto)
    campos = len(ficha) + len(especificaciones)
    assert campos >= 10
    assert len(especificaciones) >= 5


def test_extraccion_defensiva_html_vacio():
    ficha = extraer_ficha("<html><body></body></html>")
    assert ficha["titulo"] is None
    assert ficha["precio_actual"] is None
    assert ficha["calificacion"] == 0.0
    assert ficha["ahorro_cop"] == 0
    assert extraer_especificaciones("<html></html>") == {}


def test_calificacion_no_numerica_no_rompe():
    html = '<span class="ui-pdp-review__rating">N/A</span>'
    assert extraer_ficha(html)["calificacion"] == 0.0
