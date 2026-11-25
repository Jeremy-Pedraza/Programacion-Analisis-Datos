# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y versionado semántico.

## [2.0.0] - 2026-11-25

### Añadido
- **Aplicación web (FastAPI)** `ml_scraper.web`: tablero HTML en `/` y API REST (`/health`,
  `/api/indicadores`, `/api/producto`, `/api/competencia`, `/api/metricas`, `/docs`). Configurable
  por variables de entorno (`APP_TITLE`, `APP_ENV`, `APP_DATA_MODE`, `PORT`, `APP_WORK_DIR`).
- **Contenedor Docker** (`Dockerfile`, `.dockerignore`) con usuario sin privilegios y lectura del
  puerto desde `$PORT`.
- **Despliegue en la nube (Render)** definido como código en `render.yaml` (*health check* `/health`,
  `autoDeploy: false`).
- Workflow **CD · Render** (`cd-render.yml`): pruebas → build y verificación de la imagen Docker →
  disparo del *Deploy Hook* de Render → prueba de humo contra `/health` en producción.
- 7 pruebas nuevas de la API web con `TestClient` (total: 37).
- Guía de despliegue `docs/DESPLIEGUE.md` e informe y cuaderno de la EA3.

### Cambiado
- Dependencias de ejecución: `fastapi`, `uvicorn[standard]`; de desarrollo: `httpx`.
- README reorganizado con secciones de instalación, uso, automatización y despliegue.

## [1.0.0] - 2026-11-14

### Añadido
- Paquete `ml_scraper` con los extractores de la EA1 refactorizados en módulos probables:
  `producto` (BeautifulSoup), `resenas` (Selenium con respaldo), `competencia` (lógica compartida
  con la araña de Scrapy), `analisis` (indicadores) y `reporte` (sitio estático).
- CLI `python -m ml_scraper` con modos offline y en vivo.
- 30 pruebas automatizadas (unitarias, de regresión e integración) con cobertura ≥ 85 %.
- Workflow **CI**: ruff, pytest en matriz 3.10–3.12, ejecución de la araña de Scrapy.
- Workflow **CD**: pruebas, pipeline de scraping, despliegue en GitHub Pages y prueba de humo.
- Plantilla de PR, guía de contribución y cuaderno Jupyter de la EA2.
