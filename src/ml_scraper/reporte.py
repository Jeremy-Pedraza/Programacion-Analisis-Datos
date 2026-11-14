"""Fase 5 — visualización y generación del sitio estático que se despliega en GitHub Pages."""

from __future__ import annotations

import html
import os
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROJO, AZUL, GRIS = "#b31b35", "#1b3a5c", "#6b7280"


def graficar(df: pd.DataFrame, destino: Path) -> Path:
    """Genera la figura de precio vs. competencia y precio vs. calificación."""
    orden = df.sort_values("precio")
    colores = [ROJO if f else AZUL for f in orden["es_articulo_analizado"]]
    etiquetas = [
        f"{i}. " + (t[:36] + ("…" if len(t) > 36 else ""))
        for i, t in enumerate(orden["titulo"], 1)
    ]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.6, 1]})
    ax1.barh(etiquetas, orden["precio"] / 1000, color=colores)
    ax1.axvline(df["precio"].mean() / 1000, color=GRIS, linestyle="--", linewidth=1.2,
                label=f"Promedio: ${df['precio'].mean() / 1000:,.0f}k")
    ax1.set_xlabel("Precio (miles de COP)")
    ax1.set_title("Precio del artículo analizado (rojo) frente a la competencia", fontsize=11)
    ax1.legend(fontsize=9)
    ax1.invert_yaxis()
    ax1.tick_params(labelsize=8)

    ax2.scatter(df["precio"] / 1000, df["calificacion"],
                s=df["n_opiniones"].fillna(0) / 6 + 40,
                c=[ROJO if f else AZUL for f in df["es_articulo_analizado"]],
                alpha=0.75, edgecolors="white")
    ax2.set_xlabel("Precio (miles de COP)")
    ax2.set_ylabel("Calificación (1-5)")
    ax2.set_title("Precio vs. calificación\n(tamaño = número de opiniones)", fontsize=11)
    ax2.grid(alpha=0.25)

    fig.suptitle("Mercado Libre Colombia — Samsung Galaxy A55 5G 256 GB", fontsize=13, y=0.99)
    fig.tight_layout()
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return destino


def _fmt(valor) -> str:
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, int):
        return f"{valor:,}".replace(",", ".")
    if isinstance(valor, float):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return html.escape(str(valor)) if valor is not None else "—"


def _tabla(filas: list[tuple], encabezados: tuple) -> str:
    cab = "".join(f"<th>{html.escape(h)}</th>" for h in encabezados)
    cuerpo = "".join(
        "<tr>" + "".join(f"<td>{_fmt(c)}</td>" for c in fila) + "</tr>" for fila in filas
    )
    return f"<table><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table>"


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1f2937;--muted:#6b7280;--accent:#1b3a5c;--hl:#b31b35;
--line:#e5e7eb}
@media (prefers-color-scheme:dark){:root{--bg:#0f1419;--card:#18202a;--ink:#e5e7eb;
--muted:#9ca3af;--accent:#7fb0e0;--hl:#f2697f;--line:#2a3441}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:var(--accent);color:#fff;padding:28px 16px}
header h1{margin:0 0 4px;font-size:1.5rem}header p{margin:0;opacity:.85}
main{max-width:1100px;margin:0 auto;padding:20px 16px 48px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:8px 0 20px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.kpi b{display:block;font-size:1.35rem}.kpi span{color:var(--muted);font-size:.85rem}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px;
margin-bottom:18px;overflow-x:auto}h2{margin-top:0;font-size:1.1rem}
table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{text-align:left;padding:6px 8px;
border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}
tr.hl td{color:var(--hl);font-weight:600}img{max-width:100%;height:auto;border-radius:6px;
background:#fff}footer{color:var(--muted);font-size:.8rem;text-align:center;padding:16px}
code{font-size:.85em}
"""


def generar_sitio(
    ficha: dict,
    especificaciones: dict,
    resenas: list[dict],
    df: pd.DataFrame,
    indicadores: dict,
    metricas: pd.DataFrame,
    destino: Path,
) -> Path:
    """Escribe ``index.html`` y los datos descargables en ``destino``."""
    destino = Path(destino)
    (destino / "data").mkdir(parents=True, exist_ok=True)
    graficar(df, destino / "analisis_precios.png")
    df.to_csv(destino / "data" / "competencia.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(indicadores.items(), columns=["Métrica", "Valor"]).to_csv(
        destino / "data" / "resumen_analisis.csv", index=False, encoding="utf-8-sig")

    commit = os.environ.get("GITHUB_SHA", "local")[:7]
    run = os.environ.get("GITHUB_RUN_NUMBER", "—")
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    kpis = [
        ("Precio del artículo", f"$ {_fmt(indicadores['Precio del artículo analizado (COP)'])}"),
        ("Promedio del mercado", f"$ {_fmt(indicadores['Precio promedio del mercado (COP)'])}"),
        ("Desviación vs. promedio", f"{_fmt(indicadores['Desviación vs. promedio (%)'])} %"),
        ("Ranking de precio",
         f"{indicadores['Ranking de precio (1 = más barato)']} de {indicadores['Artículos rastreados']}"),
    ]
    kpi_html = "".join(f'<div class="kpi"><span>{k}</span><b>{v}</b></div>' for k, v in kpis)

    filas_comp = ""
    for _, r in df.sort_values("precio").iterrows():
        clase = ' class="hl"' if r["es_articulo_analizado"] else ""
        filas_comp += (
            f"<tr{clase}><td>{html.escape(str(r['titulo']))}</td><td>$ {_fmt(int(r['precio']))}</td>"
            f"<td>{_fmt(r['descuento_pct']) if pd.notna(r['descuento_pct']) else '—'} %</td>"
            f"<td>{_fmt(float(r['calificacion']))}</td><td>{_fmt(r['envio_gratis'])}</td></tr>"
        )
    tabla_comp = (
        "<table><thead><tr><th>Artículo</th><th>Precio</th><th>Descuento</th>"
        f"<th>Calificación</th><th>Envío gratis</th></tr></thead><tbody>{filas_comp}</tbody></table>"
    )

    pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Análisis Galaxy A55</title><style>{CSS}</style></head><body>
<header><h1>Análisis competitivo — Samsung Galaxy A55 5G 256 GB</h1>
<p>Mercado Libre Colombia · Web scraping con BeautifulSoup, Selenium y Scrapy ·
desplegado automáticamente con GitHub Actions</p></header>
<main>
<div class="kpis">{kpi_html}</div>
<section><h2>Visualización</h2>
<img src="analisis_precios.png" alt="Precio del artículo frente a la competencia y relación precio-calificación"></section>
<section><h2>Indicadores de posicionamiento</h2>
{_tabla(list(indicadores.items()), ("Métrica", "Valor"))}</section>
<section><h2>Competencia rastreada ({len(df)} artículos)</h2>{tabla_comp}</section>
<section><h2>Ficha del producto</h2>
{_tabla([(k, v) for k, v in ficha.items() if k != "url"], ("Campo", "Valor"))}</section>
<section><h2>Especificaciones técnicas</h2>
{_tabla(list(especificaciones.items()), ("Atributo", "Valor"))}</section>
<section><h2>Opiniones recuperadas</h2>
{_tabla([(r["estrellas"], r["comentario"]) for r in resenas], ("Estrellas", "Comentario"))}</section>
<section><h2>Métricas de éxito</h2>
{_tabla(list(metricas.itertuples(index=False, name=None)), tuple(metricas.columns))}</section>
<section><h2>Datos descargables</h2><p><a href="data/competencia.csv">competencia.csv</a> ·
<a href="data/resumen_analisis.csv">resumen_analisis.csv</a></p></section>
</main>
<footer>Build #{run} · commit <code>{commit}</code> · generado {fecha} ·
Evidencia de Aprendizaje 2 — Programación para Análisis de Datos, IU Digital</footer>
</body></html>"""
    salida = destino / "index.html"
    salida.write_text(pagina, encoding="utf-8")
    (destino / ".nojekyll").write_text("", encoding="utf-8")
    return salida
