"""Genera notebooks/Pedraza_Jeremy_Desplegando_EA3.ipynb (cuaderno ejecutable de la EA3).

Uso:  python build_nb_ea3.py [usuario_github]
El cuaderno recorre, con celdas que se ejecutan en vivo: configuración del entorno, historial
Git, pruebas automatizadas, arranque de la aplicación web y consulta de sus endpoints, los
workflows de GitHub Actions y el despliegue en la nube, y las conclusiones.
"""

import sys
from pathlib import Path

import nbformat as nbf
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

GH = sys.argv[1] if len(sys.argv) > 1 else "Jeremy-Pedraza"
REPO = f"https://github.com/{GH}/Programacion-Analisis-Datos"
RENDER = "https://galaxy-a55-analytics.onrender.com"
SALIDA = Path(__file__).resolve().parents[2] / "notebooks" / "Pedraza_Jeremy_Desplegando_EA3.ipynb"
SALIDA.parent.mkdir(parents=True, exist_ok=True)

md = new_markdown_cell
code = new_code_cell
cells = []

cells.append(md(
    "# Evidencia de Aprendizaje 3 — Optimización de procesos de desarrollo\n"
    "### Automatización con GitHub Actions y despliegue de un servicio en la nube\n\n"
    "**Jeremy Iván Pedraza Hernández** · Programación para Análisis de Datos · IU Digital de Antioquia\n\n"
    f"- Repositorio: {REPO}\n"
    f"- Aplicación web desplegada (Render): {RENDER}\n\n"
    "Este cuaderno es un artefacto **ejecutable**: en lugar de describir el proyecto, lo pone en "
    "marcha. Recorre el historial Git, ejecuta las pruebas, arranca la aplicación web y consulta "
    "sus *endpoints*, y muestra los *workflows* de CI/CD. Funciona tanto en local (dentro del "
    "repositorio) como en Google Colab (clona el repositorio automáticamente)."
))

# ---------------------------------------------------------------- Fase 0
cells.append(md(
    "## Fase 0 — Configuración del entorno\n\n"
    "Detecta si el cuaderno se ejecuta dentro del repositorio o en Colab; en Colab clona el "
    "repositorio. Luego instala el paquete y sus dependencias de desarrollo."
))
cells.append(code(
    "import os, subprocess, sys\n"
    "from pathlib import Path\n\n"
    "def encontrar_raiz():\n"
    "    p = Path.cwd()\n"
    "    for cand in [p, *p.parents]:\n"
    "        if (cand / 'src' / 'ml_scraper' / 'web.py').exists():\n"
    "            return cand\n"
    "    return None\n\n"
    "RAIZ = encontrar_raiz()\n"
    "if RAIZ is None:\n"
    f"    subprocess.run(['git', 'clone', '--depth', '1', '{REPO}.git'], check=True)\n"
    "    RAIZ = Path.cwd() / 'Programacion-Analisis-Datos'\n"
    "os.chdir(RAIZ)\n"
    "print('Raíz del proyecto:', RAIZ)"
))
cells.append(code(
    "subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',\n"
    "                '-r', 'requirements-dev.txt'], check=True)\n"
    "subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-e', '.'], check=True)\n"
    "print('Dependencias instaladas.')"
))

# ---------------------------------------------------------------- Fase 1
cells.append(md(
    "## Fase 1 — Control de versiones (Git)\n\n"
    "El proyecto se construyó con un modelo de ramas (`main`, `develop`, `feature/*`, `docs/*`) e "
    "integraciones por *pull request*. Las celdas muestran el grafo de commits y la convención "
    "*Conventional Commits*."
))
cells.append(code(
    "import subprocess\n"
    "def git(*args):\n"
    "    return subprocess.run(['git', *args], capture_output=True, text=True).stdout\n"
    "print(git('log', '--oneline', '--graph', '--all', '-20'))"
))
cells.append(code(
    "print('Ramas:'); print(git('branch', '-a'))\n"
    "print('Etiquetas:'); print(git('tag'))"
))

# ---------------------------------------------------------------- Fase 2
cells.append(md(
    "## Fase 2 — Pruebas automatizadas (replica la integración continua)\n\n"
    "Las mismas 37 pruebas que ejecuta el *workflow* `ci.yml` en cada *push* y *pull request*, con "
    "cobertura. Son la puerta de calidad que debe pasar antes de desplegar."
))
cells.append(code(
    "import subprocess, sys\n"
    "r = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--cov', '--cov-report=term-missing'],\n"
    "                   capture_output=True, text=True)\n"
    "print(r.stdout[-3000:])\n"
    "print('RUFF:'); print(subprocess.run([sys.executable, '-m', 'ruff', 'check', '.'],\n"
    "                                     capture_output=True, text=True).stdout or 'All checks passed!')"
))

# ---------------------------------------------------------------- Fase 3
cells.append(md(
    "## Fase 3 — La aplicación web en marcha\n\n"
    "Se arranca la aplicación FastAPI **en proceso** con `TestClient` (sin servidor externo) y se "
    "consultan sus *endpoints*: el estado del servicio, los indicadores de posicionamiento y la "
    "ficha del producto. Es el mismo código que se despliega en la nube."
))
cells.append(code(
    "from fastapi.testclient import TestClient\n"
    "from ml_scraper.web import app\n"
    "cliente = TestClient(app)\n"
    "print('GET /health ->', cliente.get('/health').json())"
))
cells.append(code(
    "import pandas as pd\n"
    "ind = cliente.get('/api/indicadores').json()\n"
    "pd.DataFrame(ind.items(), columns=['Indicador', 'Valor'])"
))
cells.append(code(
    "comp = pd.DataFrame(cliente.get('/api/competencia').json())\n"
    "print('Competidores:', len(comp))\n"
    "comp[['titulo', 'precio', 'calificacion']].sort_values('precio').head(12)"
))
cells.append(code(
    "# Regresión de negocio: la conclusión de la EA1 debe mantenerse en la API desplegada.\n"
    "assert abs(ind['Desviación vs. promedio (%)'] - 17.05) < 0.01\n"
    "print('OK — el artículo se ofrece', ind['Desviación vs. promedio (%)'], '% por encima del promedio.')"
))

# ---------------------------------------------------------------- Fase 4
cells.append(md(
    "## Fase 4 — Automatización y despliegue (GitHub Actions + Render)\n\n"
    "Los tres *workflows* del repositorio: integración continua (`ci.yml`), despliegue del reporte "
    "estático (`cd.yml`) y **despliegue del servicio en la nube** (`cd-render.yml`). Este último "
    "encadena: pruebas → build de la imagen Docker → *Deploy Hook* de Render → prueba de humo."
))
cells.append(code(
    "from pathlib import Path\n"
    "wf = Path('.github/workflows')\n"
    "for f in ['ci.yml', 'cd.yml', 'cd-render.yml']:\n"
    "    print('='*70); print(f); print('='*70)\n"
    "    print((wf / f).read_text(encoding='utf-8'))"
))
cells.append(code(
    "print('Dockerfile:'); print(Path('Dockerfile').read_text(encoding='utf-8'))\n"
    "print('render.yaml:'); print(Path('render.yaml').read_text(encoding='utf-8'))"
))
cells.append(md(
    f"La aplicación está desplegada en **{RENDER}**. Si el servicio está activo, la siguiente celda "
    "consulta su estado en producción (en Colab con red). En el plan gratuito el primer acceso puede "
    "tardar unos segundos por el arranque en frío."
))
cells.append(code(
    "import urllib.request, json\n"
    "try:\n"
    f"    with urllib.request.urlopen('{RENDER}/health', timeout=60) as r:\n"
    "        print('Producción /health ->', json.load(r))\n"
    "except Exception as e:\n"
    "    print('No se pudo consultar producción (servicio dormido o sin red):', e)"
))

# ---------------------------------------------------------------- Fase 5
cells.append(md(
    "## Fase 5 — Conclusiones\n\n"
    "- El análisis dejó de ser un reporte estático y se convirtió en un **servicio web** con API REST.\n"
    "- La **contenerización** garantiza que lo probado es lo desplegado; GitHub Actions es el único "
    "origen de los despliegues.\n"
    "- El pipeline `test → docker → deploy → smoke` solo publica lo que superó todas las "
    "verificaciones, y la prueba de humo confirma que el servicio quedó en línea.\n"
    "- La **regresión de negocio** (+17,05 %) se mantiene verificable en la API desplegada.\n"
    "- Se completó el ciclo DevOps de las tres evidencias: extracción (EA1) → CI/CD y software "
    "versionado (EA2) → despliegue de un servicio en la nube (EA3)."
))

nb = new_notebook(cells=cells, metadata={
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12"},
})
nbf.write(nb, SALIDA)
print("Cuaderno generado:", SALIDA, "| celdas:", len(cells))
