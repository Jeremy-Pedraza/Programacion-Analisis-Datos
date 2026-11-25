# Programacion-Analisis-Datos

[![CI](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/ci.yml/badge.svg)](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/ci.yml)
[![CD Pages](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/cd.yml/badge.svg)](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/cd.yml)
[![CD Render](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/cd-render.yml/badge.svg)](https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos/actions/workflows/cd-render.yml)

Análisis competitivo del **Samsung Galaxy A55 5G 256 GB** en **Mercado Libre Colombia** mediante
*web scraping* (BeautifulSoup, Selenium y Scrapy), convertido en un proyecto de software
versionado con **Git/GitHub** y un flujo **DevOps** completo de integración y **despliegue continuo
de un servicio en la nube** con **GitHub Actions**.

> **Evidencia de Aprendizaje 3** — *Optimización de procesos de desarrollo*
> Programación para Análisis de Datos · Institución Universitaria Digital de Antioquia
> Continuación de la EA1 (*extracción de datos*) y la EA2 (*control de versiones y CI/CD*).

- **Aplicación web (servicio en la nube, Render):** https://galaxy-a55-analytics.onrender.com
- **Reporte estático (GitHub Pages, EA2):** https://jeremy-pedraza.github.io/Programacion-Analisis-Datos/

---

## Introducción

El proyecto nació como un cuaderno de *web scraping* (EA1), se reorganizó como paquete de software
versionado con un pipeline de **integración y despliegue continuos** hacia GitHub Pages (EA2), y en
esta tercera evidencia (EA3) da el paso final de **DevOps**: el análisis se expone como una
**aplicación web con API REST** (FastAPI), se **containeriza** (Docker) y se **despliega
automáticamente en un proveedor de alojamiento en la nube** (Render) mediante un nuevo workflow de
GitHub Actions que prueba, construye la imagen, despliega y verifica el servicio en producción.

### ¿Qué hace?

| Fase | Herramienta | Módulo | Resultado |
|---|---|---|---|
| 1. Ficha de producto (HTML estático) | BeautifulSoup | `producto.py` | 22 campos, 9 especificaciones |
| 2. Opiniones (renderizadas por JS) | Selenium | `resenas.py` | 5 opiniones |
| 3. Listado de competencia | Scrapy | `competencia.py`, `spiders/` | 12 artículos × 11 campos |
| 4. Indicadores de posicionamiento | pandas | `analisis.py` | precio +17,05 % vs. promedio |
| 5. Reporte web estático | Matplotlib + HTML | `reporte.py` | `site/index.html` → GitHub Pages |
| 6. **Servicio web (API + tablero)** | **FastAPI + Uvicorn** | **`web.py`** | **app desplegada en Render** |

### Estructura

```
Programacion-Analisis-Datos/
├── .github/
│   ├── workflows/ci.yml          # lint + pruebas (matriz 3.10–3.12) + araña Scrapy
│   ├── workflows/cd.yml          # CD estático: pipeline → GitHub Pages → prueba de humo
│   ├── workflows/cd-render.yml   # CD del servicio: pruebas → Docker → Render → prueba de humo
│   └── pull_request_template.md
├── data/                         # snapshot HTML versionado (reproducibilidad)
├── docs/informe/                 # informes EA2 y EA3 (PDF/DOCX), figuras y scripts
├── docs/DESPLIEGUE.md            # guía detallada del despliegue en Render
├── notebooks/                    # cuadernos Jupyter de la EA2 y la EA3
├── spiders/competencia_spider.py # araña Scrapy
├── src/ml_scraper/               # paquete: utils, producto, resenas, competencia,
│                                 #          analisis, reporte, pipeline, web (FastAPI)
├── tests/                        # 37 pruebas automatizadas (pytest)
├── Dockerfile · .dockerignore    # contenedor de la aplicación web
├── render.yaml                   # servicio en la nube como código (Blueprint de Render)
├── CONTRIBUTING.md · CHANGELOG.md
├── pyproject.toml                # dependencias, pytest, cobertura, ruff
└── requirements*.txt
```

## Instalación

Requisitos: Python 3.10–3.12 y Git (opcionalmente Docker para el contenedor).

```bash
git clone https://github.com/Jeremy-Pedraza/Programacion-Analisis-Datos.git
cd Programacion-Analisis-Datos

python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt  # dependencias de ejecución + desarrollo
pip install -e .                     # instala el paquete ml_scraper en modo editable
```

## Uso

### Pipeline de scraping (línea de comandos)

```bash
python -m ml_scraper                          # modo offline (snapshot) → out/ y site/index.html
python -m ml_scraper --en-vivo --selenium     # peticiones reales al sitio
pytest --cov                                   # 37 pruebas + cobertura
ruff check .                                    # análisis estático
```

### Aplicación web (API REST + tablero)

```bash
uvicorn ml_scraper.web:app --reload           # http://localhost:8000
python -m ml_scraper.web                       # equivalente, lee el puerto de $PORT
```

| Endpoint | Descripción |
|---|---|
| `GET /` | Tablero HTML con KPI, gráfico y tabla de competencia |
| `GET /health` | Estado del servicio en JSON (lo usa el *health check* y la prueba de humo) |
| `GET /api/indicadores` | Indicadores de posicionamiento |
| `GET /api/producto` | Ficha y especificaciones del artículo |
| `GET /api/competencia` | Listado de competencia rastreado |
| `GET /api/metricas` | Métricas de éxito de la solución |
| `GET /docs` | Documentación interactiva OpenAPI/Swagger |

Variables de entorno: `APP_TITLE`, `APP_ENV` (`local`/`production`), `APP_DATA_MODE`
(`snapshot`/`en-vivo`), `PORT` y `APP_WORK_DIR`.

### Contenedor (Docker)

```bash
docker build -t ml-scraper-web .
docker run -p 8000:8000 -e APP_ENV=local ml-scraper-web
```

## Automatización (GitHub Actions)

El repositorio tiene tres workflows. El detalle de cada paso está en el informe de la EA3 y en
[CONTRIBUTING.md](CONTRIBUTING.md).

```
feature/*  ──PR──►  develop  ──PR (release)──►  main  ──tag vX.Y.Z
   │                  │                          │
   └── CI ────────────┴── CI ──────────────────┬┴── cd.yml       → GitHub Pages (reporte)
                                                └── cd-render.yml → Render (aplicación web)
```

- **`ci.yml` — Integración continua.** En cada *push* y *pull request*: `ruff`, 37 pruebas en la
  matriz Python 3.10/3.11/3.12 con cobertura ≥ 85 %, y la araña de Scrapy contra el *snapshot*.
- **`cd.yml` — Despliegue continuo estático.** Al fusionar en `main`: pruebas → pipeline de
  scraping → publicación del reporte en GitHub Pages → prueba de humo.
- **`cd-render.yml` — Despliegue continuo del servicio.** Al fusionar en `main`: pruebas →
  construcción y verificación de la imagen Docker → disparo del *Deploy Hook* de Render → prueba de
  humo contra `/health` en producción.

## Despliegue (servicio en la nube — Render)

La aplicación web se despliega en **Render** como servicio Docker. El despliegue lo **dispara
GitHub Actions** (no el *push* directo), de modo que solo llega a producción el código que superó
las pruebas. Pasos resumidos (guía completa en **[docs/DESPLIEGUE.md](docs/DESPLIEGUE.md)**):

1. Crear en Render un *Web Service* desde este repositorio (runtime **Docker**) o con el *Blueprint*
   `render.yaml`.
2. Configurar las **variables de entorno** (`APP_TITLE`, `APP_ENV=production`, `APP_DATA_MODE`) y la
   ruta de *health check* `/health`.
3. Copiar el **Deploy Hook** del servicio y guardarlo como *secret* `RENDER_DEPLOY_HOOK_URL`, y la
   URL pública como *variable* `RENDER_SERVICE_URL`, en *Settings → Secrets and variables → Actions*
   del repositorio en GitHub.
4. Cada fusión en `main` dispara `cd-render.yml`, que despliega y verifica el servicio.

## Pruebas

37 pruebas con `pytest` (unitarias, de regresión y de integración, más las de la API web con
`TestClient`), con cobertura ≥ 85 % verificada en CI. La prueba de regresión fija la conclusión de
negocio de la EA1 (+17,05 % sobre el promedio del mercado) para que ninguna refactorización la
altere.

## Consideraciones éticas

Solo información pública de catálogo, `ROBOTSTXT_OBEY=True`, retardo de 2 s, concurrencia ≤ 4,
fines exclusivamente académicos (Ley 1581 de 2012). Por defecto se usa el *snapshot* versionado, de
modo que CI/CD y el servicio desplegado no generan tráfico hacia Mercado Libre.

## Autor

Jeremy Iván Pedraza Hernández — Ingeniería de Software y Datos, IU Digital (2026).
