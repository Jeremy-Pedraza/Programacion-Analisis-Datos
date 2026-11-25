# Imagen de la aplicación web (FastAPI) que se despliega como servicio en la nube (Render).
# Build:  docker build -t ml-scraper-web .
# Run:    docker run -p 8000:8000 -e APP_ENV=local ml-scraper-web
FROM python:3.12-slim

# Buenas prácticas: sin buffer en logs, sin caché de pip, sin .pyc.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    APP_DATA_MODE=snapshot \
    APP_WORK_DIR=/tmp/ml_scraper

WORKDIR /app

# 1) Dependencias primero (capa cacheable mientras requirements.txt no cambie).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) Código y datos de referencia (snapshot versionado) e instalación del paquete.
COPY pyproject.toml ./
COPY src ./src
COPY data ./data
RUN pip install --no-cache-dir -e .

# 3) Usuario sin privilegios.
RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 8000

# Render inyecta el puerto en $PORT; en local se usa 8000 por defecto.
CMD ["sh", "-c", "uvicorn ml_scraper.web:app --host 0.0.0.0 --port ${PORT:-8000}"]
