# Programacion-Analisis-Datos

[![CI](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/ci.yml/badge.svg)](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/ci.yml)
[![CD](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/cd.yml/badge.svg)](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/cd.yml)

Análisis competitivo del **Samsung Galaxy A55 5G 256 GB** en **Mercado Libre Colombia** mediante
*web scraping* (BeautifulSoup, Selenium y Scrapy), convertido en un proyecto de software
versionado con **Git/GitHub** y un flujo **DevOps** de integración y despliegue continuo con
**GitHub Actions**.

> Evidencia de Aprendizaje 2 — *Optimizando la productividad en el mundo del software*
> Programación para Análisis de Datos · Institución Universitaria Digital de Antioquia
> Continuación de la EA1 (*Análisis y herramientas de extracción de datos*).

**Reporte desplegado:** https://jeremy-pedraza.github.io/Programacion-Analisis-Datos/

---

## 1. ¿Qué hace?

| Fase | Herramienta | Módulo | Resultado |
|---|---|---|---|
| 1. Ficha de producto (HTML estático) | BeautifulSoup | `producto.py` | 22 campos, 9 especificaciones |
| 2. Opiniones (renderizadas por JS) | Selenium | `resenas.py` | 5 opiniones |
| 3. Listado de competencia | Scrapy | `competencia.py`, `spiders/` | 12 artículos × 11 campos |
| 4. Indicadores de posicionamiento | pandas | `analisis.py` | precio +17,05 % vs. promedio |
| 5. Reporte web | Matplotlib + HTML | `reporte.py` | `site/index.html` → GitHub Pages |

## 2. Estructura

```
Programacion-Analisis-Datos/
├── .github/
│   ├── workflows/ci.yml          # lint + pruebas (matriz 3.10–3.12) + araña Scrapy
│   ├── workflows/cd.yml          # pruebas → pipeline → GitHub Pages → prueba de humo
│   └── pull_request_template.md
├── data/                         # snapshot HTML versionado (reproducibilidad)
├── docs/informe/                 # informe EA2 (PDF/DOCX), figuras y scripts que lo generan
├── notebooks/                    # cuaderno Jupyter de la EA2
├── spiders/competencia_spider.py # araña Scrapy (reutiliza ml_scraper.competencia)
├── src/ml_scraper/               # paquete Python
├── tests/                        # 30 pruebas automatizadas (pytest)
├── CONTRIBUTING.md               # flujo de ramas, commits y PR
├── CHANGELOG.md
├── pyproject.toml                # dependencias, pytest, cobertura, ruff
└── requirements*.txt
```

## 3. Ejecución local

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt && pip install -e .

pytest --cov                 # pruebas + cobertura
ruff check .                 # análisis estático
python -m ml_scraper         # pipeline completo → out/ y site/index.html
python -m ml_scraper --en-vivo --selenium    # contra el sitio real
```

## 4. Flujo DevOps

```
feature/*  ──PR──►  develop  ──PR (release)──►  main  ──tag vX.Y.Z
   │                  │                          │
   └── CI ────────────┴── CI ────────────────────┴── CD: pruebas → pipeline → Pages → smoke test
```

* **Plan / Code:** cada funcionalidad se desarrolla en una rama `feature/*` creada desde `develop`.
* **Build / Test (CI):** cada push y cada PR ejecutan `ruff`, 30 pruebas en Python 3.10, 3.11 y
  3.12 con umbral de cobertura del 85 % y la araña de Scrapy contra el snapshot.
* **Review / Merge:** los PR usan plantilla y solo se fusionan con CI en verde.
* **Release / Deploy (CD):** al fusionar en `main` se vuelve a probar, se ejecuta el scraping, se
  publica el reporte en GitHub Pages y una prueba de humo verifica que el sitio responde.

Detalles en [CONTRIBUTING.md](CONTRIBUTING.md).

## 5. Consideraciones éticas

Solo información pública de catálogo, `ROBOTSTXT_OBEY=True`, retardo de 2 s, concurrencia ≤ 4,
fines exclusivamente académicos (Ley 1581 de 2012). Por defecto se usa el snapshot versionado,
de modo que CI/CD no genera tráfico hacia Mercado Libre.

## Autor

Jeremy Iván Pedraza Hernández — Ingeniería de Software y Datos, IU Digital (2026).
