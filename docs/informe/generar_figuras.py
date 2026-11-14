"""Genera los diagramas del informe: python generar_figuras.py figuras"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(sys.argv[1])
AZUL, ROJO, VERDE, GRIS, NAR = "#1b3a5c", "#b31b35", "#2e7d32", "#6b7280", "#c77700"

# ---------- Figura: modelo de ramas ----------
fig, ax = plt.subplots(figsize=(12, 4.6))
lanes = {"main": 4, "develop": 3, "feature/*": 2, "fix/*": 1.2, "docs/notebook-ea2": 0.4}
colors = {"main": ROJO, "develop": AZUL, "feature/*": VERDE, "fix/*": NAR, "docs/notebook-ea2": GRIS}
for name, y in lanes.items():
    ax.text(-0.3, y, name, ha="right", va="center", fontsize=10, color=colors[name], weight="bold")
ax.plot([0, 22.5], [4, 4], color=ROJO, lw=2.5)
ax.plot([0.8, 21.5], [3, 3], color=AZUL, lw=2.5)


def dot(x, y, c, s=70):
    ax.scatter([x], [y], s=s, color=c, zorder=3, edgecolors="white", linewidths=1.2)


def link(x1, y1, x2, y2, c):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10,
                                 color=c, lw=1.3, connectionstyle="arc3,rad=0"))


dot(0, 4, ROJO)
ax.text(0, 4.3, "chore: estructura\ninicial", ha="center", fontsize=7.5)
link(0, 4, 0.8, 3, AZUL)
feats = [("extraccion-\nproducto", 3), ("rastreo-\ncompetencia", 2), ("analisis-\nreporte", 3),
         ("ci-github-\nactions", 2), ("cd-github-\npages", 2)]
x = 1.2
for nombre, n in feats:
    link(x, 3, x + 0.4, 2, VERDE)
    xs = [x + 0.4 + i * 0.55 for i in range(n)]
    ax.plot([xs[0], xs[-1]], [2, 2], color=VERDE, lw=2)
    for xi in xs:
        dot(xi, 2, VERDE, 45)
    ax.text((xs[0] + xs[-1]) / 2, 1.62, nombre, ha="center", va="top", fontsize=7)
    xm = xs[-1] + 0.45
    link(xs[-1], 2, xm, 3, VERDE)
    dot(xm, 3, AZUL)
    x = xm + 0.25
# fix
link(x, 3, x + 0.4, 1.2, NAR)
dot(x + 0.4, 1.2, NAR, 45)
ax.text(x + 0.4, 0.95, "contraste-\nencabezado", ha="center", va="top", fontsize=7)
link(x + 0.4, 1.2, x + 0.9, 3, NAR)
dot(x + 0.9, 3, AZUL)
# docs branch from earlier develop
xd0 = x - 0.1
xd = x + 1.4
link(xd0, 3, xd0 + 0.3, 0.4, GRIS)
ax.plot([xd0 + 0.3, xd + 1.2], [0.4, 0.4], color=GRIS, lw=2)
for xi in (xd0 + 0.3, xd0 + 0.75, xd0 + 1.2):
    dot(xi, 0.4, GRIS, 45)
link(x + 0.9, 3, xd + 0.6, 0.4, AZUL)
dot(xd + 0.6, 0.4, GRIS)
ax.text(xd0 + 0.75, 0.1, "notebook · changelog", ha="center", va="top", fontsize=7)
# PR 1 and PR 2
link(xd + 1.2, 0.4, xd + 1.7, 3, GRIS)
dot(xd + 1.7, 3, AZUL, 90)
ax.text(xd + 1.85, 2.15, "PR #1", fontsize=8, color=GRIS, weight="bold")
link(xd + 1.7, 3, xd + 2.6, 4, AZUL)
dot(xd + 2.6, 4, ROJO, 110)
ax.text(xd + 2.0, 3.55, "PR #2\n(release)", fontsize=8, color=AZUL, weight="bold", ha="right")
ax.text(xd + 2.6, 4.3, "v1.0.0\n→ CD: GitHub Pages", ha="center", fontsize=8, color=ROJO,
        weight="bold")
ax.set_xlim(-2.6, xd + 3.6)
ax.set_ylim(-0.5, 4.9)
ax.axis("off")
fig.tight_layout()
fig.savefig(OUT / "modelo_ramas.png", dpi=170, bbox_inches="tight")
plt.close(fig)

# ---------- Figura: pipeline CI/CD ----------
fig, ax = plt.subplots(figsize=(12, 5.2))
ax.axis("off")
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.4)


def box(x, y, w, h, titulo, cuerpo, c):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc="white", ec=c, lw=1.8))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.42), w, 0.42,
                                boxstyle="round,pad=0.04,rounding_size=0.12", fc=c, ec=c))
    ax.text(x + w / 2, y + h - 0.21, titulo, ha="center", va="center", color="white",
            fontsize=9, weight="bold")
    ax.text(x + w / 2, y + (h - 0.42) / 2, cuerpo, ha="center", va="center", fontsize=7.8,
            color="#1f2937", linespacing=1.35)


def arrow(x1, y1, x2, y2, c=GRIS, txt=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                 color=c, lw=1.5))
    if txt:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, txt, ha="center", fontsize=7.5, color=c)


ax.text(0.1, 5.15, "Integración continua — ci.yml", fontsize=11, weight="bold", color=AZUL)
ax.text(0.1, 2.35, "Despliegue continuo — cd.yml", fontsize=11, weight="bold", color=ROJO)
box(0.1, 3.2, 1.9, 1.6, "Disparador", "push a feature/*,\nfix/*, develop, main\n\npull_request\n→ main / develop", GRIS)
box(2.7, 3.2, 2.0, 1.6, "lint", "ruff check\n(E, F, W, I, B, UP)\nPython 3.12", AZUL)
box(5.5, 3.95, 2.9, 1.05, "test  (matriz)", "pytest + cobertura ≥ 85 %\nPython 3.10 · 3.11 · 3.12", AZUL)
box(5.5, 2.85, 2.9, 0.95, "scrapy", "araña sobre el snapshot\n≥ 10 artículos", AZUL)
box(9.2, 3.2, 2.7, 1.6, "Resultado", "estado ✔ / ✘ en el PR\n\nartefactos: coverage.xml,\nreporte-pruebas.xml", GRIS)
arrow(2.0, 4.0, 2.7, 4.0)
arrow(4.7, 4.2, 5.5, 4.45)
arrow(4.7, 3.8, 5.5, 3.35)
arrow(8.4, 4.45, 9.2, 4.2)
arrow(8.4, 3.35, 9.2, 3.8)

box(0.1, 0.3, 1.9, 1.7, "Disparador", "merge en main\n(PR de release)\n\ntag v*  ·  manual", GRIS)
box(2.7, 0.3, 2.6, 1.7, "build", "pytest (puerta de calidad)\npython -m ml_scraper\nupload-pages-artifact\nartefacto out/", ROJO)
box(6.0, 0.3, 2.4, 1.7, "deploy", "actions/deploy-pages\nentorno github-pages", ROJO)
box(9.2, 0.3, 2.7, 1.7, "smoke", "curl al sitio publicado\nverifica «Galaxy A55»\n\nhttps://jeremy-pedraza.github.io/\nProgramacion-Analisis-Datos/", ROJO)
arrow(2.0, 1.15, 2.7, 1.15)
arrow(5.3, 1.15, 6.0, 1.15, txt="needs")
arrow(8.4, 1.15, 9.2, 1.15, txt="needs")
fig.tight_layout()
fig.savefig(OUT / "pipeline_cicd.png", dpi=170, bbox_inches="tight")
plt.close(fig)
print("ok")
