"""Aplicación web (FastAPI) que publica el análisis competitivo como un servicio.

A diferencia del reporte estático de la EA2 (GitHub Pages), esta evidencia expone el
resultado del *pipeline* como una **aplicación web con API REST** desplegable en un servicio
de alojamiento en la nube (Render). El contenido se calcula una sola vez al arrancar,
reutilizando ``ml_scraper.pipeline.ejecutar`` sobre el *snapshot* versionado, de modo que
el contenedor no depende de la red ni del estado del sitio.

Ejecución local::

    uvicorn ml_scraper.web:app --reload
    python -m ml_scraper.web            # equivalente, leyendo el puerto de $PORT

Variables de entorno (configurables en el servicio en la nube):

===================  ========================================================  ===============
Variable             Propósito                                                 Valor por defecto
===================  ========================================================  ===============
``APP_TITLE``        Título mostrado en el encabezado del tablero              Análisis Galaxy A55
``APP_ENV``          Entorno lógico (``local`` / ``production``)               ``local``
``APP_DATA_MODE``    ``snapshot`` (offline) o ``en-vivo`` (peticiones reales)  ``snapshot``
``PORT``             Puerto de escucha (lo inyecta la plataforma)              ``8000``
``APP_WORK_DIR``     Carpeta de trabajo para artefactos generados              carpeta temporal
===================  ========================================================  ===============
"""

from __future__ import annotations

import os
import tempfile
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from . import __version__
from .pipeline import ejecutar
from .reporte import _fmt

# --------------------------------------------------------------------- configuración
APP_TITLE = os.environ.get("APP_TITLE", "Análisis competitivo — Samsung Galaxy A55 5G 256 GB")
APP_ENV = os.environ.get("APP_ENV", "local")
APP_DATA_MODE = os.environ.get("APP_DATA_MODE", "snapshot").lower()
COMMIT = os.environ.get("RENDER_GIT_COMMIT", os.environ.get("GITHUB_SHA", "local"))[:7]
WORK_DIR = Path(os.environ.get("APP_WORK_DIR", tempfile.gettempdir())) / "ml_scraper_web"


@lru_cache(maxsize=1)
def _datos() -> dict:
    """Ejecuta el pipeline una sola vez y memoiza el resultado para toda la vida del proceso."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    return ejecutar(
        offline=(APP_DATA_MODE != "en-vivo"),
        out_dir=WORK_DIR / "out",
        site_dir=WORK_DIR / "site",
        usar_selenium=False,
    )


# --------------------------------------------------------------------- aplicación
app = FastAPI(
    title=APP_TITLE,
    version=__version__,
    description="API REST y tablero del análisis competitivo del Galaxy A55 en Mercado Libre "
    "Colombia. Evidencia de Aprendizaje 3 — despliegue continuo de un servicio en la nube.",
    contact={"name": "Jeremy Pedraza", "url": "https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos"},
)


@app.get("/health", tags=["servicio"], summary="Estado del servicio")
def health() -> dict:
    """Comprobación de salud usada por el *health check* de Render y por la prueba de humo del CD."""
    return {
        "status": "ok",
        "version": __version__,
        "entorno": APP_ENV,
        "modo_datos": APP_DATA_MODE,
        "commit": COMMIT,
    }


@app.get("/api/indicadores", tags=["datos"], summary="Indicadores de posicionamiento")
def api_indicadores() -> JSONResponse:
    return JSONResponse(_datos()["indicadores"])


@app.get("/api/producto", tags=["datos"], summary="Ficha y especificaciones del artículo")
def api_producto() -> JSONResponse:
    d = _datos()
    return JSONResponse({"ficha": d["ficha"], "especificaciones": d["especificaciones"]})


@app.get("/api/competencia", tags=["datos"], summary="Listado de competencia rastreado")
def api_competencia() -> JSONResponse:
    df: pd.DataFrame = _datos()["competencia"]
    return JSONResponse(df.to_dict(orient="records"))


@app.get("/api/metricas", tags=["datos"], summary="Métricas de éxito de la solución")
def api_metricas() -> JSONResponse:
    df: pd.DataFrame = _datos()["metricas"]
    return JSONResponse(df.to_dict(orient="records"))


@app.get("/grafica.png", tags=["datos"], summary="Figura del análisis de precios", include_in_schema=False)
def grafica() -> FileResponse:
    _datos()  # garantiza que el sitio (y la figura) estén generados
    return FileResponse(WORK_DIR / "site" / "analisis_precios.png", media_type="image/png")


@app.get("/", response_class=HTMLResponse, tags=["servicio"], summary="Tablero web")
def tablero() -> HTMLResponse:
    """Página HTML con los KPI, la visualización y la tabla de competencia (modo claro/oscuro)."""
    d = _datos()
    ind = d["indicadores"]
    df: pd.DataFrame = d["competencia"]

    kpis = [
        ("Precio del artículo", f"$ {_fmt(ind['Precio del artículo analizado (COP)'])}"),
        ("Promedio del mercado", f"$ {_fmt(ind['Precio promedio del mercado (COP)'])}"),
        ("Desviación vs. promedio", f"{_fmt(ind['Desviación vs. promedio (%)'])} %"),
        ("Ranking de precio",
         f"{ind['Ranking de precio (1 = más barato)']} de {ind['Artículos rastreados']}"),
    ]
    kpi_html = "".join(f'<div class="kpi"><span>{k}</span><b>{v}</b></div>' for k, v in kpis)

    filas = ""
    for _, r in df.sort_values("precio").iterrows():
        clase = ' class="hl"' if r["es_articulo_analizado"] else ""
        filas += (
            f"<tr{clase}><td>{r['titulo']}</td><td>$ {_fmt(int(r['precio']))}</td>"
            f"<td>{_fmt(float(r['calificacion']))}</td></tr>"
        )

    return HTMLResponse(f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{APP_TITLE}</title><style>{_CSS}</style></head><body>
<header><h1>{APP_TITLE}</h1>
<p>Aplicación web desplegada en la nube con integración y despliegue continuos (GitHub Actions + Render) ·
entorno <code>{APP_ENV}</code> · commit <code>{COMMIT}</code> · datos <code>{APP_DATA_MODE}</code></p></header>
<main>
<div class="kpis">{kpi_html}</div>
<section><h2>Visualización</h2><img src="grafica.png" alt="Precio frente a la competencia"></section>
<section><h2>Competencia rastreada ({len(df)} artículos)</h2>
<table><thead><tr><th>Artículo</th><th>Precio</th><th>Calificación</th></tr></thead>
<tbody>{filas}</tbody></table></section>
<section><h2>API REST</h2><p>El mismo análisis está disponible como servicio:</p>
<ul>
<li><a href="/health">/health</a> — estado del servicio (JSON)</li>
<li><a href="/api/indicadores">/api/indicadores</a> — indicadores de posicionamiento</li>
<li><a href="/api/producto">/api/producto</a> — ficha y especificaciones</li>
<li><a href="/api/competencia">/api/competencia</a> — listado de competencia</li>
<li><a href="/api/metricas">/api/metricas</a> — métricas de éxito</li>
<li><a href="/docs">/docs</a> — documentación interactiva (OpenAPI/Swagger)</li>
</ul></section>
</main>
<footer>Evidencia de Aprendizaje 3 — Programación para Análisis de Datos · IU Digital de Antioquia</footer>
</body></html>""")


_CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1f2937;--muted:#6b7280;--accent:#1b3a5c;--hl:#b31b35;--line:#e5e7eb}
@media (prefers-color-scheme:dark){:root{--bg:#0f1419;--card:#18202a;--ink:#e5e7eb;--muted:#9ca3af;
--accent:#7fb0e0;--hl:#f2697f;--line:#2a3441}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:#1b3a5c;color:#fff;padding:28px 16px}header h1{margin:0 0 4px;font-size:1.5rem}
header p{margin:0;opacity:.9;font-size:.9rem}header code{background:rgba(255,255,255,.15);padding:1px 5px;border-radius:4px}
main{max-width:1000px;margin:0 auto;padding:20px 16px 48px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:8px 0 20px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.kpi b{display:block;font-size:1.35rem}.kpi span{color:var(--muted);font-size:.85rem}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px;margin-bottom:18px;overflow-x:auto}
h2{margin-top:0;font-size:1.1rem}table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}
tr.hl td{color:var(--hl);font-weight:600}img{max-width:100%;height:auto;border-radius:6px;background:#fff}
a{color:var(--accent)}footer{color:var(--muted);font-size:.8rem;text-align:center;padding:16px}
code{font-size:.85em}
"""


def main() -> None:  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":  # pragma: no cover
    main()
