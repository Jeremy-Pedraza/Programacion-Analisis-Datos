import pandas as pd
import pytest

from ml_scraper.analisis import calcular_indicadores, evaluar_metricas_exito, marcar_articulo


def test_marca_un_unico_articulo_analizado(df_competencia):
    assert df_competencia["es_articulo_analizado"].sum() == 1


def test_excluye_reacondicionados():
    df = pd.DataFrame({"titulo": ["Galaxy A55 5G 256 GB Reacondicionado", "Galaxy A55 5G 256 GB"]})
    assert marcar_articulo(df)["es_articulo_analizado"].tolist() == [False, True]


def test_indicadores_coherentes(df_competencia, ficha):
    ind = calcular_indicadores(df_competencia, ficha)
    assert ind["Artículos rastreados"] == len(df_competencia)
    assert ind["Precio mínimo del mercado (COP)"] <= ind["Precio promedio del mercado (COP)"]
    assert ind["Precio promedio del mercado (COP)"] <= ind["Precio máximo del mercado (COP)"]
    assert 1 <= ind["Ranking de precio (1 = más barato)"] <= len(df_competencia)
    esperado = round((ficha["precio_actual"] / df_competencia["precio"].mean() - 1) * 100, 2)
    assert ind["Desviación vs. promedio (%)"] == esperado


def test_resultado_de_negocio_ea1(df_competencia, ficha):
    """Regresión: la conclusión de la EA1 (≈ +17 % sobre el promedio) debe mantenerse."""
    ind = calcular_indicadores(df_competencia, ficha)
    assert ind["Desviación vs. promedio (%)"] == pytest.approx(17.05, abs=0.01)


def test_indicadores_marca_si_falta_columna(ficha):
    df = pd.DataFrame({"titulo": ["Galaxy A55 5G 256 GB", "Otro"], "precio": [100, 200],
                       "descuento_pct": [10, None], "envio_gratis": [True, False],
                       "calificacion": [4.5, 4.0]})
    ind = calcular_indicadores(df, {"precio_actual": 100, "calificacion": 4.5})
    assert ind["Ranking de precio (1 = más barato)"] == 1


def test_indicadores_listado_vacio(ficha):
    with pytest.raises(ValueError):
        calcular_indicadores(pd.DataFrame(), ficha)


def test_metricas_de_exito(df_competencia, ficha, html_producto):
    from ml_scraper.producto import extraer_especificaciones
    from ml_scraper.resenas import extraer_resenas

    m = evaluar_metricas_exito(ficha, extraer_especificaciones(html_producto),
                               extraer_resenas(html_producto), df_competencia)
    assert m["Cumple"].all()
