"""Genera los diagramas del informe de la EA3: python generar_figuras_ea3.py figuras"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "figuras")
OUT.mkdir(parents=True, exist_ok=True)
AZUL, ROJO, VERDE, GRIS, NAR, MOR = "#1b3a5c", "#b31b35", "#2e7d32", "#6b7280", "#c77700", "#5b3a8c"


def box(ax, x, y, w, h, titulo, cuerpo, c, fs=7.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc="white", ec=c, lw=1.8))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.42), w, 0.42,
                                boxstyle="round,pad=0.04,rounding_size=0.12", fc=c, ec=c))
    ax.text(x + w / 2, y + h - 0.21, titulo, ha="center", va="center", color="white",
            fontsize=9, weight="bold")
    ax.text(x + w / 2, y + (h - 0.42) / 2, cuerpo, ha="center", va="center", fontsize=fs,
            color="#1f2937", linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, c=GRIS, txt=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                 color=c, lw=1.5))
    if txt:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, txt, ha="center", fontsize=7.5, color=c)


# ============================================================ Figura: modelo de ramas EA3
fig, ax = plt.subplots(figsize=(12, 4.4))
lanes = {"main": 4, "develop": 3, "feature/*": 2, "docs/*": 1}
colors = {"main": ROJO, "develop": AZUL, "feature/*": VERDE, "docs/*": MOR}
for name, y in lanes.items():
    ax.text(-0.3, y, name, ha="right", va="center", fontsize=10, color=colors[name], weight="bold")
ax.plot([0, 13.2], [4, 4], color=ROJO, lw=2.5)
ax.plot([0.6, 12.4], [3, 3], color=AZUL, lw=2.5)


def dot(x, y, c, s=70):
    ax.scatter([x], [y], s=s, color=c, zorder=3, edgecolors="white", linewidths=1.2)


dot(0, 4, ROJO)
ax.text(0, 4.32, "v1.0.0\n(EA2)", ha="center", fontsize=7.5, color=ROJO)
link = lambda x1, y1, x2, y2, c: arrow(ax, x1, y1, x2, y2, c)  # noqa: E731
link(0, 4, 0.6, 3, AZUL)
feats = [("feature/\nwebapp-fastapi", 2, 2.0), ("feature/\ndeploy-render", 3, 2.0)]
x = 1.2
for nombre, n, _ in feats:
    link(x, 3, x + 0.4, 2, VERDE)
    xs = [x + 0.4 + i * 0.6 for i in range(n)]
    ax.plot([xs[0], xs[-1]], [2, 2], color=VERDE, lw=2)
    for xi in xs:
        dot(xi, 2, VERDE, 45)
    ax.text((xs[0] + xs[-1]) / 2, 1.6, nombre, ha="center", va="top", fontsize=7)
    xm = xs[-1] + 0.5
    link(xs[-1], 2, xm, 3, VERDE)
    dot(xm, 3, AZUL)
    x = xm + 0.5
# docs branch
link(x - 0.3, 3, x, 1, MOR)
xs = [x + i * 0.6 for i in range(3)]
ax.plot([xs[0], xs[-1]], [1, 1], color=MOR, lw=2)
for xi in xs:
    dot(xi, 1, MOR, 45)
ax.text((xs[0] + xs[-1]) / 2, 0.6, "docs/informe-ea3\n(README, informe, cuaderno)", ha="center",
        va="top", fontsize=7)
xm = xs[-1] + 0.5
link(xs[-1], 1, xm, 3, MOR)
dot(xm, 3, AZUL, 90)
ax.text(xm + 0.15, 2.3, "PR → develop", fontsize=8, color=GRIS, weight="bold")
# release to main
link(xm, 3, xm + 1.0, 4, AZUL)
dot(xm + 1.0, 4, ROJO, 110)
ax.text(xm + 0.5, 3.55, "PR (release)", fontsize=8, color=AZUL, weight="bold", ha="right")
ax.text(xm + 1.0, 4.32, "v2.0.0\n→ CD: Render + Pages", ha="center", fontsize=8, color=ROJO,
        weight="bold")
ax.set_xlim(-2.4, xm + 2.2)
ax.set_ylim(0.0, 4.9)
ax.axis("off")
fig.tight_layout()
fig.savefig(OUT / "modelo_ramas_ea3.png", dpi=170, bbox_inches="tight")
plt.close(fig)

# ============================================================ Figura: arquitectura de la app
fig, ax = plt.subplots(figsize=(12, 4.2))
ax.axis("off")
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.2)
box(ax, 0.1, 1.3, 1.9, 1.5, "Cliente", "Navegador /\ncurl / Swagger", GRIS)
box(ax, 2.6, 1.3, 2.6, 1.5, "FastAPI (web.py)", "Uvicorn (ASGI)\nrutas / y /api/*\n/health, /docs", AZUL)
box(ax, 5.8, 2.35, 2.6, 1.0, "pipeline.ejecutar", "orquesta las 5 fases\n(memoizado al arrancar)", VERDE)
box(ax, 5.8, 0.3, 2.6, 1.3, "ml_scraper", "producto · resenas\ncompetencia · analisis\nreporte", VERDE)
box(ax, 9.0, 1.3, 2.7, 1.5, "data/ (snapshot)", "HTML versionado\nreproducible y offline", NAR)
arrow(ax, 2.0, 2.05, 2.6, 2.05, txt="HTTP")
arrow(ax, 5.2, 2.2, 5.8, 2.6)
arrow(ax, 7.1, 2.35, 7.1, 1.6)
arrow(ax, 8.4, 0.95, 9.0, 1.6, txt="lee")
ax.text(3.9, 3.0, "Variables de entorno: APP_TITLE · APP_ENV · APP_DATA_MODE · PORT",
        ha="center", fontsize=8, color=AZUL, style="italic")
fig.tight_layout()
fig.savefig(OUT / "arquitectura_app.png", dpi=170, bbox_inches="tight")
plt.close(fig)

# ============================================================ Figura: pipeline CI/CD EA3
fig, ax = plt.subplots(figsize=(12, 5.4))
ax.axis("off")
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.6)
ax.text(0.1, 5.35, "Integración continua — ci.yml", fontsize=11, weight="bold", color=AZUL)
box(ax, 0.1, 3.5, 1.8, 1.5, "Disparador", "push / PR\na main, develop,\nfeature/*, docs/*", GRIS)
box(ax, 2.5, 3.5, 1.8, 1.5, "lint", "ruff check\nPython 3.12", AZUL)
box(ax, 4.9, 4.15, 2.9, 0.95, "test (matriz)", "pytest cobertura ≥ 85 %\n3.10 · 3.11 · 3.12", AZUL)
box(ax, 4.9, 3.1, 2.9, 0.9, "scrapy", "araña sobre snapshot\n≥ 10 artículos", AZUL)
box(ax, 8.4, 3.5, 3.4, 1.5, "Resultado", "estado ✔/✘ en el PR\nartefactos de cobertura", GRIS)
arrow(ax, 1.9, 4.25, 2.5, 4.25)
arrow(ax, 4.3, 4.4, 4.9, 4.6)
arrow(ax, 4.3, 4.1, 4.9, 3.55)
arrow(ax, 7.8, 4.6, 8.4, 4.4)
arrow(ax, 7.8, 3.55, 8.4, 4.1)

ax.text(0.1, 2.55, "Despliegue continuo del servicio — cd-render.yml", fontsize=11, weight="bold",
        color=ROJO)
box(ax, 0.1, 0.3, 1.8, 1.9, "Disparador", "merge en main\ntag v*\nmanual", GRIS)
box(ax, 2.5, 0.3, 2.2, 1.9, "test", "pytest\n(puerta de\ncalidad)", ROJO)
box(ax, 5.0, 0.3, 2.3, 1.9, "docker", "docker build\ncurl /health\nen el contenedor", ROJO)
box(ax, 7.6, 0.3, 1.9, 1.9, "deploy", "Deploy Hook\nde Render\n(secret)", ROJO)
box(ax, 9.8, 0.3, 2.0, 1.9, "smoke", "curl\n/health en\nproducción", ROJO)
arrow(ax, 1.9, 1.25, 2.5, 1.25)
arrow(ax, 4.7, 1.25, 5.0, 1.25, txt="needs")
arrow(ax, 7.3, 1.25, 7.6, 1.25, txt="needs")
arrow(ax, 9.5, 1.25, 9.8, 1.25, txt="needs")
fig.tight_layout()
fig.savefig(OUT / "pipeline_cicd_ea3.png", dpi=170, bbox_inches="tight")
plt.close(fig)

print("ok:", sorted(p.name for p in OUT.glob("*_ea3.png")) + ["arquitectura_app.png"])
