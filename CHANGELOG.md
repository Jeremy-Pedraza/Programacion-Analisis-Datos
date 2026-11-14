# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y versionado semántico.

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
