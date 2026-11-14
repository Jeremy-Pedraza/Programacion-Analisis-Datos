from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="session")
def html_producto() -> str:
    return (DATA / "ml_producto.html").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def html_resultados() -> str:
    return (DATA / "ml_resultados.html").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def ficha(html_producto) -> dict:
    from ml_scraper.producto import extraer_ficha

    return extraer_ficha(html_producto)


@pytest.fixture(scope="session")
def df_competencia(html_resultados):
    import pandas as pd

    from ml_scraper.analisis import marcar_articulo
    from ml_scraper.competencia import extraer_listado

    return marcar_articulo(pd.DataFrame(extraer_listado(html_resultados)))
