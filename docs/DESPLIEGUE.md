# Guía de despliegue — Aplicación web en Render

Esta guía documenta, paso a paso, el despliegue de la aplicación web (`ml_scraper.web:app`) en
**Render**, un proveedor de alojamiento en la nube (PaaS), y su automatización desde **GitHub
Actions**. El despliegue lo dispara el workflow `cd-render.yml` tras superar las pruebas; Render no
despliega en cada *push* (`autoDeploy: false`), por lo que solo llega a producción el código
verificado.

- **URL del servicio en producción:** `https://galaxy-a55-analytics.onrender.com`
- **Endpoint de salud:** `https://galaxy-a55-analytics.onrender.com/health`
- **Workflow:** [`.github/workflows/cd-render.yml`](../.github/workflows/cd-render.yml)
- **Servicio como código:** [`render.yaml`](../render.yaml) · **Contenedor:** [`Dockerfile`](../Dockerfile)

---

## 1. Arquitectura del despliegue

```
 Desarrollador ──git push──► GitHub ──PR──► main
                                              │
                                   dispara    ▼
                            ┌───────  GitHub Actions (cd-render.yml)  ───────┐
                            │  1. test    pytest (puerta de calidad)         │
                            │  2. docker  docker build + curl /health        │
                            │  3. deploy  curl $RENDER_DEPLOY_HOOK_URL  ──────┼──► Render
                            │  4. smoke   curl $RENDER_SERVICE_URL/health     │     (build de la
                            └─────────────────────────────────────────────────┘      imagen Docker
                                                                                      y publicación)
                                                                               │
                                                      Usuarios ◄───HTTPS───────┘
```

Render construye la imagen a partir del `Dockerfile`, inyecta la variable `PORT`, ejecuta el
contenedor y expone el servicio por HTTPS con certificado gestionado. El *health check* a `/health`
permite a Render reiniciar el servicio si deja de responder (auto-recuperación).

## 2. Requisitos previos

- Cuenta gratuita en [Render](https://render.com) (se puede crear con la cuenta de GitHub).
- Repositorio en GitHub con el `Dockerfile` y el `render.yaml` (este repositorio).
- Permisos de administrador en el repositorio para configurar *secrets* y *variables*.

## 3. Crear el servicio en Render

### Opción A — Blueprint (recomendada, infraestructura como código)

1. En Render: **New + → Blueprint**.
2. Conectar el repositorio `Programacion-Analisis-Datos`.
3. Render lee [`render.yaml`](../render.yaml) y propone el servicio `galaxy-a55-analytics`
   (runtime Docker, plan *free*, *health check* `/health`). Confirmar con **Apply**.

### Opción B — Web Service manual

1. **New + → Web Service** y conectar el repositorio.
2. **Runtime:** Docker · **Branch:** `main` · **Plan:** Free.
3. **Health Check Path:** `/health`.
4. **Auto-Deploy:** *No* (el despliegue lo dispara GitHub Actions).

> 📸 **Captura 1 — Creación del servicio en Render** (pegar en el informe, Figura «Servicio en Render»).

## 4. Configurar las variables de entorno

En Render, **Dashboard del servicio → Environment → Environment Variables**:

| Variable | Valor | Propósito |
|---|---|---|
| `APP_TITLE` | `Análisis competitivo — Samsung Galaxy A55 5G 256 GB` | Título del tablero |
| `APP_ENV` | `production` | Identifica el entorno |
| `APP_DATA_MODE` | `snapshot` | Usa el *snapshot* versionado (sin tráfico al sitio real) |
| `PORT` | *(lo inyecta Render automáticamente)* | Puerto de escucha del contenedor |

> 📸 **Captura 2 — Variables de entorno en Render** (Figura «Variables de entorno»).

No se almacenan credenciales ni datos sensibles: el servicio solo sirve datos públicos de catálogo.

## 5. Conectar GitHub Actions con Render

1. En Render: **Settings → Deploy Hook** y copiar la URL (tiene la forma
   `https://api.render.com/deploy/srv-XXXX?key=YYYY`).
2. En GitHub: **Settings → Secrets and variables → Actions**:
   - Pestaña **Secrets** → *New repository secret*:
     - **Name:** `RENDER_DEPLOY_HOOK_URL` · **Value:** la URL del Deploy Hook.
   - Pestaña **Variables** → *New repository variable*:
     - **Name:** `RENDER_SERVICE_URL` · **Value:** `https://galaxy-a55-analytics.onrender.com`.

> 📸 **Captura 3 — Secret y variable configurados en GitHub** (Figura «Secrets de Actions»).

El *secret* se usa para disparar el despliegue y la *variable* para la prueba de humo. Mientras no
estén configurados, `cd-render.yml` termina en verde omitiendo el despliegue (no rompe `main`).

## 6. Desplegar

- **Automático:** cada fusión en `main` (o *tag* `v*`) dispara `cd-render.yml`.
- **Manual:** en GitHub, **Actions → CD · Render → Run workflow**.

El workflow ejecuta las pruebas, construye y verifica la imagen Docker, dispara el despliegue en
Render y realiza la prueba de humo contra `/health` en producción.

> 📸 **Captura 4 — Ejecución de `cd-render.yml` en verde** (Figura «CD en GitHub Actions»).
> 📸 **Captura 5 — Aplicación en producción** (`https://galaxy-a55-analytics.onrender.com`).

## 7. Verificación

```bash
curl https://galaxy-a55-analytics.onrender.com/health
# {"status":"ok","version":"2.0.0","entorno":"production","modo_datos":"snapshot","commit":"…"}

curl https://galaxy-a55-analytics.onrender.com/api/indicadores
```

## 8. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `deploy` omitido con *warning* | Falta el secret `RENDER_DEPLOY_HOOK_URL` | Configurarlo (paso 5) |
| `smoke` no se ejecuta | Falta la variable `RENDER_SERVICE_URL` | Configurarla (paso 5) |
| 502 / *Bad Gateway* temporal | El plan *free* "duerme" tras inactividad | La primera petición lo despierta (~30 s) |
| Build de Docker falla | Dependencia o ruta | Revisar el log de build en Render y el job `docker` |

## 9. Notas del plan gratuito

El plan *free* de Render suspende el servicio tras un periodo de inactividad y lo reactiva con la
primera petición (arranque en frío de unos segundos). La prueba de humo de `cd-render.yml`
contempla esa latencia reintentando hasta ~5 minutos.
