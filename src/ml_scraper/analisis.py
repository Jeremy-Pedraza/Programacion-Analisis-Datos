"""Fase 4 — consolidación con pandas e indicadores de posicionamiento."""

from __future__ import annotations

import pandas as pd

PATRON_ARTICULO = "A55 5G 256 GB"


def marcar_articulo(df: pd.DataFrame, patron: str = PATRON_ARTICULO) -> pd.DataFrame:
    """Añade la columna ``es_articulo_analizado`` excluyendo equipos reacondicionados."""
    df = df.copy()
    titulos = df["titulo"].fillna("")
    df["es_articulo_analizado"] = (
        titulos.str.contains(patron, case=False, regex=False)
        & ~titulos.str.contains("reacondicionado", case=False)
    )
    return df


def calcular_indicadores(df: pd.DataFrame, ficha: dict) -> dict:
    """Calcula los indicadores de posicionamiento del artículo frente a su mercado."""
    if df.empty:
        raise ValueError("El listado de competencia está vacío")
    if "es_articulo_analizado" not in df:
        df = marcar_articulo(df)
    precio_objetivo = ficha["precio_actual"]
    promedio = df["precio"].mean()
    ranking = df["precio"].rank(method="min").loc[df["es_articulo_analizado"]]
    return {
        "Artículos rastreados": int(len(df)),
        "Precio del artículo analizado (COP)": int(precio_objetivo),
        "Precio mínimo del mercado (COP)": int(df["precio"].min()),
        "Precio máximo del mercado (COP)": int(df["precio"].max()),
        "Precio promedio del mercado (COP)": int(promedio),
        "Mediana del mercado (COP)": int(df["precio"].median()),
        "Desviación vs. promedio (%)": round((precio_objetivo / promedio - 1) * 100, 2),
        "Ranking de precio (1 = más barato)": int(ranking.iloc[0]) if len(ranking) else None,
        "Descuento promedio del mercado (%)": round(float(df["descuento_pct"].mean()), 1),
        "Ofertas con envío gratis (%)": round(float(df["envio_gratis"].mean()) * 100, 1),
        "Calificación promedio del mercado": round(float(df["calificacion"].mean()), 2),
        "Calificación del artículo analizado": ficha["calificacion"],
    }


def evaluar_metricas_exito(
    ficha: dict, especificaciones: dict, resenas: list, df: pd.DataFrame
) -> pd.DataFrame:
    """Contrasta los resultados con los criterios de aceptación definidos en la EA1."""
    campos = len(ficha) + len(especificaciones)
    filas = [
        ("Cobertura de campos de la ficha", "≥ 10 campos", campos, campos >= 10),
        ("Especificaciones técnicas", "≥ 5 atributos", len(especificaciones),
         len(especificaciones) >= 5),
        ("Contenido dinámico", "≥ 3 opiniones", len(resenas), len(resenas) >= 3),
        ("Cobertura del mercado", "≥ 10 competidores", len(df), len(df) >= 10),
    ]
    return pd.DataFrame(filas, columns=["Métrica", "Criterio", "Resultado", "Cumple"])
