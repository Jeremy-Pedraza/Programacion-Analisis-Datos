"""Orquestador: ejecuta las cinco fases y deja los artefactos en ``out/`` y ``site/``.

Uso::

    python -m ml_scraper                 # modo offline (snapshot versionado)
    python -m ml_scraper --en-vivo       # peticiones reales al sitio
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .analisis import calcular_indicadores, evaluar_metricas_exito, marcar_articulo
from .competencia import extraer_listado
from .producto import extraer_especificaciones, extraer_ficha
from .reporte import generar_sitio
from .resenas import extraer_resenas, html_con_selenium
from .utils import URL_BUSQUEDA, URL_PRODUCTO, obtener_html

RAIZ = Path(__file__).resolve().parents[2]


def ejecutar(
    offline: bool = True,
    data_dir: Path = RAIZ / "data",
    out_dir: Path = RAIZ / "out",
    site_dir: Path = RAIZ / "site",
    usar_selenium: bool = False,
) -> dict:
    data_dir, out_dir = Path(data_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    snap_producto = data_dir / "ml_producto.html"
    snap_busqueda = data_dir / "ml_resultados.html"

    # Fase 1 — BeautifulSoup
    html_producto = obtener_html(URL_PRODUCTO, snap_producto, offline)
    ficha = extraer_ficha(html_producto)
    especificaciones = extraer_especificaciones(html_producto)
    pd.DataFrame([{**ficha, **especificaciones}]).to_csv(
        out_dir / "producto_beautifulsoup.csv", index=False, encoding="utf-8-sig")

    # Fase 2 — Selenium (o snapshot)
    if usar_selenium:
        html_dinamico, motor = html_con_selenium(URL_PRODUCTO, snap_producto, offline)
    else:
        html_dinamico, motor = html_producto, "snapshot"
    resenas = extraer_resenas(html_dinamico)
    pd.DataFrame(resenas).to_csv(out_dir / "resenas_selenium.csv", index=False,
                                 encoding="utf-8-sig")

    # Fase 3 — listado de competencia
    registros = extraer_listado(obtener_html(URL_BUSQUEDA, snap_busqueda, offline))
    (out_dir / "competencia.json").write_text(
        json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")

    # Fase 4 — análisis
    df = marcar_articulo(pd.DataFrame(registros))
    indicadores = calcular_indicadores(df, ficha)
    metricas = evaluar_metricas_exito(ficha, especificaciones, resenas, df)
    pd.DataFrame(indicadores.items(), columns=["Métrica", "Valor"]).to_csv(
        out_dir / "resumen_analisis.csv", index=False, encoding="utf-8-sig")

    # Fase 5 — sitio estático para despliegue continuo
    index = generar_sitio(ficha, especificaciones, resenas, df, indicadores, metricas, site_dir)

    return {"ficha": ficha, "especificaciones": especificaciones, "resenas": resenas,
            "competencia": df, "indicadores": indicadores, "metricas": metricas,
            "motor_resenas": motor, "index": index}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline de scraping Mercado Libre — EA2")
    parser.add_argument("--en-vivo", action="store_true", help="scraping contra el sitio real")
    parser.add_argument("--selenium", action="store_true", help="usar Chrome headless")
    parser.add_argument("--site", default=str(RAIZ / "site"), help="carpeta del sitio")
    args = parser.parse_args(argv)

    r = ejecutar(offline=not args.en_vivo, site_dir=Path(args.site), usar_selenium=args.selenium)
    print(f"Ficha: {len(r['ficha']) + len(r['especificaciones'])} campos | "
          f"Reseñas: {len(r['resenas'])} ({r['motor_resenas']}) | "
          f"Competidores: {len(r['competencia'])}")
    for k, v in r["indicadores"].items():
        print(f"  {k:40} {v}")
    print("Sitio generado en", r["index"])
    return 0 if r["metricas"]["Cumple"].all() else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
