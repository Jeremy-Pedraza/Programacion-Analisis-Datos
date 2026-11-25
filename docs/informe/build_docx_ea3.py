"""Genera Pedraza_Jeremy_Desplegando_EA3.docx a partir de la plantilla institucional de la EA1.

Uso:  EA1_PLANTILLA=<ruta EA1.docx> python build_docx_ea3.py [usuario_github]
Conserva portada, estilos y numeraciones del documento de la EA1 y reemplaza el contenido.
"""

import os
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

BASE = Path(__file__).resolve().parent
PLANTILLA = Path(os.environ.get("EA1_PLANTILLA",
                                BASE.parents[2] / "EV1" / "Pedraza_Jeremy_Analizando_EA1.docx"))
SALIDA = BASE / "Pedraza_Jeremy_Desplegando_EA3.docx"
FIG = BASE / "figuras"
GH = sys.argv[1] if len(sys.argv) > 1 else "Jeremy-Pedraza"
REPO = f"https://github.com/{GH}/Programacion-Analisis-Datos"
PAGES = f"https://{GH.lower()}.github.io/Programacion-Analisis-Datos/"
RENDER = "https://galaxy-a55-analytics.onrender.com"

NUM_DECIMAL, NUM_VINETA = "2", "3"

doc = Document(PLANTILLA)
body = doc.element.body
hijos = list(body.iterchildren())


# ---------------------------------------------------------------- portada
def reemplazar(p_el, texto):
    runs = p_el.findall(qn("w:r"))
    for r in runs[1:]:
        p_el.remove(r)
    for pe in p_el.findall(qn("w:proofErr")):
        p_el.remove(pe)
    runs[0].find(qn("w:t")).text = texto


reemplazar(hijos[2], "Evidencia de Aprendizaje 3")
reemplazar(hijos[3], "Optimización de procesos de desarrollo")
reemplazar(hijos[4], "Automatización con GitHub Actions y despliegue de un servicio en la nube")
reemplazar(hijos[13], "Unidad 3")

# ---------------------------------------------------------------- tabla de contenido (campo TOC)
sdt = hijos[26]
p_toc = OxmlElement("w:p")
for tipo, instr in (("begin", None), (None, ' TOC \\o "1-2" \\h \\z \\u '), ("separate", None),
                    (None, None), ("end", None)):
    r = OxmlElement("w:r")
    if tipo:
        fc = OxmlElement("w:fldChar")
        fc.set(qn("w:fldCharType"), tipo)
        r.append(fc)
    elif instr:
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = instr
        r.append(it)
    else:
        t = OxmlElement("w:t")
        t.text = "Actualice la tabla de contenido (clic derecho → Actualizar campo)."
        r.append(t)
    p_toc.append(r)
sdt.addprevious(p_toc)
body.remove(sdt)

for el in hijos[28:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)

# ---------------------------------------------------------------- utilidades de escritura
TOKEN = re.compile(r"(\*\*.+?\*\*|`.+?`|\*.+?\*)")


def runs(p, texto, size=None, italic=False):
    for parte in TOKEN.split(texto):
        if not parte:
            continue
        if parte.startswith("**"):
            r = p.add_run(parte[2:-2])
            r.bold = True
        elif parte.startswith("`"):
            r = p.add_run(parte[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(10)
        elif parte.startswith("*"):
            r = p.add_run(parte[1:-1])
            r.italic = True
        else:
            r = p.add_run(parte)
        if size and not parte.startswith("`"):
            r.font.size = Pt(size)
        if italic:
            r.italic = True
    return p


def H1(t):
    doc.add_paragraph(t, style="Heading 1")


def H2(t):
    doc.add_paragraph(t, style="Heading 2")


def P(t):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return runs(p, t)


def lista(items, num=NUM_VINETA):
    for t in items:
        p = doc.add_paragraph(style="List Paragraph")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(5)
        ppr = p._p.get_or_add_pPr()
        numpr = OxmlElement("w:numPr")
        for tag, val in (("w:ilvl", "0"), ("w:numId", num)):
            e = OxmlElement(tag)
            e.set(qn("w:val"), val)
            numpr.append(e)
        ppr.append(numpr)
        runs(p, t)


CONT = {"Tabla": 0, "Figura": 0, "Fragmento": 0}


def rotulo(tipo, titulo):
    CONT[tipo] += 1
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(f"{tipo} {CONT[tipo]}")
    r.bold = True
    r.font.size = Pt(11)
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(4)
    p2.paragraph_format.keep_with_next = True
    runs(p2, titulo, size=11, italic=True)
    return CONT[tipo]


def nota(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("Nota. ")
    r.italic = True
    r.font.size = Pt(9.5)
    runs(p, t, size=9.5)


def _celda(c, texto, ancho, fondo=None, negrita=False):
    tcpr = c._tc.get_or_add_tcPr()
    w = OxmlElement("w:tcW")
    w.set(qn("w:w"), str(ancho))
    w.set(qn("w:type"), "dxa")
    tcpr.append(w)
    if fondo:
        shd = OxmlElement("w:shd")
        for k, v in (("w:val", "clear"), ("w:color", "auto"), ("w:fill", fondo)):
            shd.set(qn(k), v)
        tcpr.append(shd)
    mar = OxmlElement("w:tcMar")
    for lado, v in (("top", 60), ("left", 100), ("bottom", 60), ("right", 100)):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tcpr.append(mar)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    runs(p, str(texto), size=10)
    if negrita:
        for r in p.runs:
            r.bold = True


def tabla(enc, filas, anchos, primera_negrita=True):
    total = 9000
    anchos = [int(total * a / sum(anchos)) for a in anchos]
    t = doc.add_table(rows=1 + len(filas), cols=len(enc))
    tblpr = t._tbl.tblPr
    w = OxmlElement("w:tblW")
    w.set(qn("w:w"), str(total))
    w.set(qn("w:type"), "dxa")
    tblpr.append(w)
    bordes = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        for k, v in (("w:val", "single"), ("w:sz", "4"), ("w:space", "0"), ("w:color", "auto")):
            e.set(qn(k), v)
        bordes.append(e)
    tblpr.append(bordes)
    for i, h in enumerate(enc):
        _celda(t.rows[0].cells[i], h, anchos[i], "D9D9D9", True)
    trpr = t.rows[0]._tr.get_or_add_trPr()
    trpr.append(OxmlElement("w:tblHeader"))
    for fi, fila in enumerate(filas, start=1):
        for i, v in enumerate(fila):
            _celda(t.rows[fi].cells[i], v, anchos[i], None, primera_negrita and i == 0)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def figura(ruta, ancho_cm=16):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(ruta), width=Cm(ancho_cm))


def figura_captura(ruta, ancho_cm=15, etiqueta="Captura"):
    """Inserta la imagen si existe; si no, un recuadro gris indicando que la captura está pendiente."""
    ruta = Path(ruta)
    if ruta.exists():
        figura(ruta, ancho_cm)
        return
    t = doc.add_table(rows=1, cols=1)
    t.alignment = 1
    cell = t.rows[0].cells[0]
    tcpr = cell._tc.get_or_add_tcPr()
    w = OxmlElement("w:tcW")
    w.set(qn("w:w"), str(int(9000 * ancho_cm / 16)))
    w.set(qn("w:type"), "dxa")
    tcpr.append(w)
    bordes = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{lado}")
        for k, v in (("w:val", "dashed"), ("w:sz", "6"), ("w:space", "0"), ("w:color", "999999")):
            e.set(qn(k), v)
        bordes.append(e)
    tcpr.append(bordes)
    shd = OxmlElement("w:shd")
    for k, v in (("w:val", "clear"), ("w:color", "auto"), ("w:fill", "F2F2F2")):
        shd.set(qn(k), v)
    tcpr.append(shd)
    for _ in range(3):
        cell.add_paragraph()
    pc = cell.paragraphs[0]
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = pc.add_run(f"[ {etiqueta}: pegar aquí la captura de pantalla — {ruta.name} ]")
    r.italic = True
    r.font.size = Pt(10)
    r.font.color.rgb = None
    for _ in range(3):
        cell.add_paragraph()
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def codigo(texto):
    p = doc.add_paragraph()
    ppr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    for k, v in (("w:val", "clear"), ("w:color", "auto"), ("w:fill", "F2F2F2")):
        shd.set(qn(k), v)
    ppr.append(shd)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.0
    lineas = texto.strip("\n").split("\n")
    for i, linea in enumerate(lineas):
        r = p.add_run(linea)
        r.font.name = "Consolas"
        r._r.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), "Consolas")
        r.font.size = Pt(9)
        if i < len(lineas) - 1:
            r.add_break()


def referencia(t):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(1.27)
    pf.first_line_indent = Cm(-1.27)
    pf.space_after = Pt(8)
    pf.line_spacing = 1.5
    runs(p, t)


# ================================================================ CONTENIDO
H1("Introducción")
P("Esta evidencia cierra un recorrido de ingeniería de software iniciado en la Evidencia de "
  "Aprendizaje 1. En la EA1 se aplicó *web scraping* sobre Mercado Libre Colombia para evaluar la "
  "competitividad del Samsung Galaxy A55 5G 256 GB, combinando BeautifulSoup, Selenium y Scrapy en "
  "un cuaderno Jupyter. En la EA2 ese cuaderno se reorganizó como un paquete Python versionado con "
  "**Git** y **GitHub**, con pruebas automatizadas y un flujo **DevOps** de integración continua "
  "(CI) y despliegue continuo (CD) que publicaba un reporte estático en GitHub Pages.")
P("La EA3 da el paso que faltaba para hablar de un verdadero despliegue de servicios: el análisis "
  "deja de ser un reporte estático y se convierte en una **aplicación web con interfaz de "
  "programación (API REST)** construida con **FastAPI**, que se **empaqueta en un contenedor "
  "Docker** y se **despliega de forma automática en un proveedor de alojamiento en la nube "
  "(Render)**. Un nuevo *workflow* de **GitHub Actions** prueba el código, construye y verifica la "
  "imagen del contenedor, dispara el despliegue en la nube y comprueba que el servicio responde en "
  "producción, de modo que cada versión aprobada llega a los usuarios sin intervención manual.")
P("El documento retoma la descripción de la página y el artículo analizados, plantea el tema de "
  "interés y los objetivos, resume la metodología de *scraping*, describe la arquitectura de la "
  "aplicación web y —como núcleo de la evidencia— detalla la **automatización con GitHub Actions** y "
  "el **despliegue del servicio en la nube**, antes de exponer los resultados y las conclusiones. "
  "Como anexo se entrega el código fuente completo en GitHub y el cuaderno Jupyter ejecutado.")

H1("Descripción de la página y el artículo analizado")
P("La fuente de datos es **Mercado Libre Colombia** (mercadolibre.com.co), el *marketplace* líder "
  "en América Latina. Bajo su modelo de intermediación, un mismo producto aparece publicado por "
  "distintos vendedores con precios, descuentos, envíos y reputaciones diferentes, lo que lo "
  "convierte en un objeto de estudio ideal para un análisis competitivo. El sitio combina HTML "
  "estático (título, precio, especificaciones), contenido inyectado por JavaScript (opiniones) y un "
  "listado paginado de resultados (competencia), con un marcado basado en el sistema de diseño "
  "Andes y clases CSS estables.")
P("El artículo analizado es el teléfono **Samsung Galaxy A55 5G de 256 GB y 8 GB de RAM**, de alta "
  "rotación en el comercio electrónico colombiano. La aplicación de la EA3 reproduce exactamente la "
  "ficha y los indicadores de la EA1 a partir del *snapshot* versionado (Tabla 1).")
rotulo("Tabla", "Ficha del artículo analizado")
tabla(["Campo", "Valor extraído"], [
    ["Título", "Samsung Galaxy A55 5G 256 GB Azul Oscuro 8 GB RAM"],
    ["Precio actual", "$ 1.499.900 COP"],
    ["Precio anterior", "$ 1.899.900 COP (ahorro de $ 400.000)"],
    ["Calificación", "4,7 / 5"],
    ["Campos estructurados", "22 (13 de la ficha y 9 especificaciones técnicas)"],
    ["Competidores rastreados", "12 artículos × 11 campos"],
], [1, 2.2])
nota("Datos del *snapshot* HTML de Mercado Libre Colombia versionado en `data/`. Elaboración propia.")

H1("Descripción del tema de interés")
P("El tema de interés de esta evidencia es la **automatización del despliegue de servicios de "
  "software mediante DevOps**. La pregunta orientadora es: ¿cómo lograr que una aplicación llegue a "
  "producción —y se mantenga disponible— de forma automática, repetible y segura cada vez que el "
  "código cambia?")
P("Pasar de un reporte estático a un **servicio en ejecución** introduce preocupaciones nuevas: el "
  "software debe empaquetarse con todas sus dependencias (contenedores), configurarse mediante "
  "**variables de entorno** según el entorno (desarrollo o producción), exponerse por una red con "
  "comprobaciones de salud (*health checks*) y publicarse en infraestructura gestionada por un "
  "tercero. DevOps aborda estas preocupaciones integrando desarrollo y operación mediante "
  "automatización y retroalimentación rápida (Kim et al., 2016): la **entrega y el despliegue "
  "continuos** mantienen el software siempre en estado publicable y lo liberan con un proceso "
  "automatizado y confiable (Humble y Farley, 2010), y la **contenerización** garantiza que lo que "
  "se probó es exactamente lo que se despliega (Merkel, 2014).")

H1("Objetivos")
P("Los objetivos se formulan desde el rol de integrante de un equipo de desarrollo responsable del "
  "proyecto, que gestiona el código con Git y GitHub y establece un pipeline de CI/CD con GitHub "
  "Actions que integra pruebas automatizadas y el despliegue continuo del servicio en la nube.")
H2("Objetivo general")
P("Automatizar, mediante GitHub Actions, la integración y el despliegue continuos de una aplicación "
  "web construida sobre el proyecto de *web scraping*, desplegándola en un servicio de alojamiento "
  "en la nube de forma efectiva y escalable, documentada en un repositorio público de GitHub.")
H2("Objetivos específicos")
lista([
    "Construir una aplicación web simple (API REST y tablero) con FastAPI que exponga el análisis "
    "competitivo del artículo y se configure mediante variables de entorno.",
    "Empaquetar la aplicación en una imagen Docker reproducible, apta para ejecutarse en cualquier "
    "proveedor de nube.",
    "Gestionar el desarrollo con Git y GitHub aplicando un modelo de ramas (`main`, `develop`, "
    "`feature/*`, `docs/*`), *commits* con la convención *Conventional Commits* y *pull requests*.",
    "Configurar un workflow de despliegue continuo en GitHub Actions que pruebe el código, construya "
    "y verifique la imagen del contenedor, despliegue el servicio en Render y realice una prueba de "
    "humo contra el entorno de producción.",
    "Documentar de forma detallada el flujo de automatización y el proceso de despliegue "
    "(configuración del entorno, variables de entorno, *secrets* y enlaces de verificación).",
], num=NUM_DECIMAL)
H2("Métricas de éxito")
P("La solución se considera exitosa si cumple los criterios verificables de la Tabla 2.")
rotulo("Tabla", "Métricas de éxito definidas para la solución")
tabla(["Métrica", "Criterio de aceptación", "Resultado"], [
    ["Aplicación web", "API REST + tablero funcionales", "7 endpoints (cumple)"],
    ["Contenerización", "Imagen Docker que arranca y responde /health", "Verificada en CI (cumple)"],
    ["Pruebas automatizadas", "≥ 30 pruebas, 0 fallos", "37 pruebas, 0 fallos (cumple)"],
    ["Cobertura", "≥ 85 % del paquete", "≥ 95 % (cumple)"],
    ["Integración continua", "CI en cada push y PR, matriz ≥ 3 versiones", "Python 3.10–3.12 (cumple)"],
    ["Despliegue en la nube", "Servicio publicado y prueba de humo", "Render + smoke test (cumple)"],
    ["Documentación", "README y guía de despliegue completos", "README + DESPLIEGUE.md (cumple)"],
    ["Regresión de negocio", "Mantener la conclusión de la EA1", "+17,05 % vs. promedio (cumple)"],
], [1.1, 1.7, 1.2])

H1("Metodología empleada de scraping")
P("La metodología de extracción es la definida en la EA1 y consolidada en la EA2, y se mantiene sin "
  "cambios: cada capa de información del sitio se atiende con la herramienta adecuada dentro del "
  "paquete `ml_scraper` (Tabla 3). La aplicación web de la EA3 no vuelve a diseñar la extracción: "
  "**reutiliza** el orquestador `pipeline.ejecutar`, que corre las cinco fases sobre el *snapshot* "
  "versionado al arrancar el servicio y memoiza el resultado para servirlo por la API.")
rotulo("Tabla", "Fases del pipeline reutilizadas por la aplicación web")
tabla(["Fase", "Herramienta", "Módulo", "Responsabilidad"], [
    ["1. Ficha de producto", "BeautifulSoup", "producto.py", "Selectores CSS defensivos de 13 campos y especificaciones"],
    ["2. Opiniones", "Selenium", "resenas.py", "Chrome *headless* con respaldo al *snapshot*"],
    ["3. Competencia", "Scrapy", "competencia.py, spiders/", "Extracción por tarjeta compartida con las pruebas"],
    ["4. Análisis", "pandas", "analisis.py", "Indicadores de posicionamiento y métricas de éxito"],
    ["5. Reporte / datos", "Matplotlib", "reporte.py", "Gráfico y tablas que consume la API y el tablero"],
    ["Transversal", "requests", "utils.py, pipeline.py", "Modo offline/en vivo y orquestación"],
], [1.1, 1, 1.2, 2.4])
P("Se conservan las **consideraciones éticas** de las evidencias anteriores: solo información "
  "pública de catálogo (Ley 1581 de 2012), `ROBOTSTXT_OBEY = True`, retardo de dos segundos y "
  "concurrencia máxima de cuatro. El servicio se despliega en modo *snapshot* (`APP_DATA_MODE="
  "snapshot`), por lo que no genera tráfico automático hacia Mercado Libre.")

H1("Arquitectura de la aplicación web")
P("La aplicación se implementó con **FastAPI**, un *framework* ASGI de alto rendimiento que genera "
  "documentación interactiva de la API automáticamente (Ramírez, 2024), servido por **Uvicorn**. El "
  "módulo `src/ml_scraper/web.py` define la aplicación, ejecuta el pipeline una sola vez al arrancar "
  "y expone el resultado tanto como un **tablero HTML** (ruta `/`) como una **API REST** en formato "
  "JSON (Figura 1 y Tabla 4).")
rotulo("Figura", "Arquitectura de la aplicación web y origen de los datos")
figura(FIG / "arquitectura_app.png", 16.5)
nota("La aplicación reutiliza el pipeline de *scraping* sobre el *snapshot* versionado. Elaboración propia.")
rotulo("Tabla", "Endpoints expuestos por la aplicación")
tabla(["Endpoint", "Método", "Respuesta"], [
    ["/", "GET", "Tablero HTML con KPI, gráfico y tabla de competencia"],
    ["/health", "GET", "Estado del servicio (JSON) — usado por el health check y la prueba de humo"],
    ["/api/indicadores", "GET", "Indicadores de posicionamiento (JSON)"],
    ["/api/producto", "GET", "Ficha y especificaciones del artículo (JSON)"],
    ["/api/competencia", "GET", "Listado de competencia rastreado (JSON)"],
    ["/api/metricas", "GET", "Métricas de éxito de la solución (JSON)"],
    ["/docs", "GET", "Documentación interactiva OpenAPI/Swagger"],
], [1.4, 0.5, 2.3])
P("La aplicación se **configura mediante variables de entorno**, de modo que el mismo artefacto "
  "sirve en desarrollo y en producción sin cambios de código: `APP_TITLE` (título del tablero), "
  "`APP_ENV` (`local`/`production`), `APP_DATA_MODE` (`snapshot`/`en-vivo`), `APP_WORK_DIR` (carpeta "
  "de trabajo) y `PORT` (puerto, inyectado por la plataforma). El endpoint de salud refleja esa "
  "configuración:")
rotulo("Fragmento", "Endpoint de salud (src/ml_scraper/web.py)")
codigo('''
@app.get("/health")
def health() -> dict:
    """Comprobación de salud usada por Render y por la prueba de humo del CD."""
    return {"status": "ok", "version": __version__, "entorno": APP_ENV,
            "modo_datos": APP_DATA_MODE, "commit": COMMIT}
''')

H1("Automatización con GitHub Actions")
P("El proyecto se aloja en el repositorio público **" + REPO + "** y aplica un flujo DevOps con "
  "tres *workflows* de GitHub Actions: integración continua (`ci.yml`), despliegue continuo del "
  "reporte estático heredado de la EA2 (`cd.yml`) y, como aporte central de la EA3, el despliegue "
  "continuo del servicio en la nube (`cd-render.yml`). GitHub Actions ejecuta estos *workflows* en "
  "*runners* efímeros en respuesta a eventos del repositorio —`push`, `pull_request`, `workflow_"
  "dispatch` y etiquetas— sin necesidad de servidores propios (GitHub, s. f.-a).")
H2("Modelo de ramas y pull requests")
P("Se mantuvo el GitFlow simplificado de la EA2 (Driessen, 2010): cada funcionalidad se desarrolla "
  "en una rama propia creada desde `develop`, se integra a `develop` mediante *pull request* y, "
  "cuando el conjunto está listo, `develop` se promueve a `main` mediante un PR de *release* que "
  "dispara los despliegues y se etiqueta con versión semántica (Figura 2).")
rotulo("Figura", "Modelo de ramas y fusiones de la EA3")
figura(FIG / "modelo_ramas_ea3.png", 16.5)
nota("Las ramas `feature/webapp-fastapi` y `feature/deploy-render` aportan la aplicación y su "
     "despliegue; `docs/informe-ea3` aporta documentación, informe y cuaderno. La promoción a "
     "`main` se etiqueta `v2.0.0`. Elaboración propia a partir de `git log --graph`.")
rotulo("Tabla", "Ramas de trabajo de la EA3")
tabla(["Rama", "Propósito"], [
    ["feature/webapp-fastapi", "Aplicación FastAPI (API REST + tablero) y sus pruebas"],
    ["feature/deploy-render", "Dockerfile, render.yaml y workflow de despliegue en Render"],
    ["docs/informe-ea3", "README, guía de despliegue, informe EA3 y cuaderno Jupyter"],
], [1.3, 2.6])
H2("Integración continua (ci.yml)")
P("El *workflow* de CI se ejecuta en cada *push* a las ramas de trabajo y en cada *pull request* "
  "hacia `main` o `develop`. Primero corre el análisis estático con `ruff`; si pasa, se ejecutan en "
  "paralelo las pruebas en una **matriz** de tres versiones de Python —con umbral de cobertura del "
  "85 % que hace fallar el trabajo si no se alcanza— y la araña de Scrapy contra el *snapshot*. Un "
  "bloque `concurrency` cancela ejecuciones obsoletas de la misma rama (Figura 3, parte superior).")
rotulo("Figura", "Pipeline de integración y despliegue continuos con GitHub Actions")
figura(FIG / "pipeline_cicd_ea3.png", 16.5)
nota("Elaboración propia a partir de `.github/workflows/ci.yml` y `cd-render.yml`.")
H2("Despliegue continuo del servicio (cd-render.yml)")
P("Este *workflow* es el aporte central de la evidencia. Se dispara al fusionar en `main`, al crear "
  "una etiqueta `v*` o de forma manual, y encadena cuatro trabajos con la cláusula `needs`, de modo "
  "que cada uno solo se ejecuta si el anterior tuvo éxito:")
lista([
    "**test** — vuelve a ejecutar `pytest` con cobertura como puerta de calidad previa al despliegue.",
    "**docker** — construye la imagen con `docker build`, levanta el contenedor y comprueba que "
    "responde `/health`, verificando que el artefacto que se desplegará realmente arranca.",
    "**deploy** — dispara el despliegue en Render invocando su *Deploy Hook* (una URL secreta) con "
    "`curl`; el *secret* se inyecta como variable de entorno del paso.",
    "**smoke** — realiza una prueba de humo contra la URL pública del servicio, reintentando hasta "
    "que `/health` responde `status: ok` en producción.",
])
P("El diseño contempla que los *secrets* puedan no estar configurados todavía: en ese caso el paso "
  "de despliegue emite una advertencia y termina en verde, para no bloquear `main`. Los fragmentos "
  "siguientes muestran la verificación del contenedor y el disparo del despliegue con su prueba de "
  "humo.")
rotulo("Fragmento", "Verificación del contenedor y disparo del despliegue (.github/workflows/cd-render.yml)")
codigo('''
  docker:
    name: Construir imagen del contenedor
    needs: test
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ml-scraper-web:${{ github.sha }} .
      - name: Verificar que el contenedor arranca y responde /health
        run: |
          docker run -d --name app -p 8000:8000 ml-scraper-web:${{ github.sha }}
          for i in $(seq 1 10); do
            if curl -fsS http://localhost:8000/health | grep -q '"status":"ok"'; then exit 0; fi
            sleep 3
          done
          docker logs app; exit 1

  deploy:
    name: Desplegar en Render
    needs: docker
    environment:
      name: render
      url: ${{ vars.RENDER_SERVICE_URL }}
    steps:
      - name: Disparar el Deploy Hook de Render
        env:
          HOOK: ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
        run: |
          if [ -z "$HOOK" ]; then echo "::warning::sin secret; se omite"; exit 0; fi
          curl -fsS -o /dev/null -w '%{http_code}' "$HOOK"
''')
P("La prueba de humo cierra el ciclo: comprueba, desde fuera, que el despliegue efectivamente dejó "
  "el servicio en línea. El plan gratuito de Render suspende el servicio tras un periodo de "
  "inactividad, por lo que la prueba reintenta durante varios minutos para contemplar el arranque "
  "en frío.")
rotulo("Fragmento", "Prueba de humo contra producción (.github/workflows/cd-render.yml)")
codigo('''
  smoke:
    name: Prueba de humo del despliegue
    needs: deploy
    if: vars.RENDER_SERVICE_URL != ''
    steps:
      - run: |
          URL="${{ vars.RENDER_SERVICE_URL }}/health"
          for i in $(seq 1 20); do
            if curl -fsS "$URL" | grep -q '"status":"ok"'; then echo "OK: $URL"; exit 0; fi
            sleep 15
          done
          echo "sin respuesta de $URL"; exit 1
''')

H1("Despliegue del servicio en la nube")
P("El servicio se despliega en **Render**, una plataforma como servicio (PaaS) que construye la "
  "imagen a partir del `Dockerfile`, la ejecuta e inyecta las variables de entorno y el puerto, y "
  "expone el servicio por HTTPS con certificado gestionado. El despliegue está definido como código "
  "en `render.yaml` (*Blueprint*), lo que lo hace reproducible y auditable. La guía paso a paso "
  "completa está en el archivo `docs/DESPLIEGUE.md` del repositorio.")
H2("Contenerización")
P("El `Dockerfile` parte de `python:3.12-slim`, instala primero las dependencias (capa cacheable), "
  "copia el código y los datos de referencia, instala el paquete, crea un **usuario sin "
  "privilegios** y arranca Uvicorn leyendo el puerto de `$PORT`. Separar la instalación de "
  "dependencias del copiado del código acelera las reconstrucciones.")
rotulo("Fragmento", "Contenedor de la aplicación (Dockerfile)")
codigo('''
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 APP_ENV=production APP_WORK_DIR=/tmp/ml_scraper
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY pyproject.toml ./ ; COPY src ./src ; COPY data ./data
RUN pip install --no-cache-dir -e .
RUN useradd --create-home app && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn ml_scraper.web:app --host 0.0.0.0 --port ${PORT:-8000}"]
''')
H2("Servicio como código y variables de entorno")
P("El archivo `render.yaml` declara el servicio web, su runtime Docker, el plan, la ruta de "
  "*health check* `/health` y las variables de entorno. La opción `autoDeploy: false` es "
  "deliberada: el despliegue no ocurre con cada *push* a Render, sino que lo **dispara GitHub "
  "Actions** tras pasar las pruebas, de modo que GitHub Actions es el único origen de los "
  "despliegues (Tabla 5).")
rotulo("Fragmento", "Servicio como código (render.yaml)")
codigo('''
services:
  - type: web
    name: galaxy-a55-analytics
    runtime: docker
    plan: free
    dockerfilePath: ./Dockerfile
    autoDeploy: false            # el despliegue lo dispara GitHub Actions
    healthCheckPath: /health
    envVars:
      - key: APP_TITLE
        value: "Análisis competitivo — Samsung Galaxy A55 5G 256 GB"
      - key: APP_ENV
        value: production
      - key: APP_DATA_MODE
        value: snapshot
''')
rotulo("Tabla", "Variables de entorno configuradas en el servicio en la nube")
tabla(["Variable", "Valor", "Propósito"], [
    ["APP_TITLE", "Análisis competitivo — Galaxy A55", "Título del tablero"],
    ["APP_ENV", "production", "Identifica el entorno de ejecución"],
    ["APP_DATA_MODE", "snapshot", "Usa el snapshot versionado (sin tráfico al sitio real)"],
    ["PORT", "(inyectada por Render)", "Puerto de escucha del contenedor"],
], [1, 1.3, 2.3])
H2("Enlace entre GitHub Actions y Render")
P("Para que GitHub Actions dispare y verifique el despliegue, se configuran en el repositorio un "
  "*secret* y una *variable*: el **Deploy Hook** del servicio (`RENDER_DEPLOY_HOOK_URL`, una URL "
  "secreta que, al recibir una petición, lanza un nuevo despliegue) y la **URL pública** "
  "(`RENDER_SERVICE_URL`), ambos en *Settings → Secrets and variables → Actions*. Guardar el "
  "*hook* como *secret* evita exponer una credencial que permitiría desplegar a cualquiera.")
rotulo("Figura", "Creación del servicio en Render")
figura_captura(FIG / "render_servicio.png", 15, "Captura 1")
nota("Servicio `galaxy-a55-analytics` creado en Render a partir del Dockerfile. Captura propia.")
rotulo("Figura", "Variables de entorno del servicio en Render")
figura_captura(FIG / "render_variables.png", 15, "Captura 2")
nota("Variables `APP_TITLE`, `APP_ENV` y `APP_DATA_MODE` configuradas en Render. Captura propia.")
rotulo("Figura", "Secret y variable de Render en GitHub Actions")
figura_captura(FIG / "github_secrets.png", 15, "Captura 3")
nota("`RENDER_DEPLOY_HOOK_URL` (secret) y `RENDER_SERVICE_URL` (variable) en el repositorio. Captura propia.")
rotulo("Figura", "Ejecución del workflow cd-render.yml en verde")
figura_captura(FIG / "cd_render_run.png", 15, "Captura 4")
nota("Los cuatro trabajos (test → docker → deploy → smoke) completados. Captura propia.")
rotulo("Figura", "Aplicación web en producción")
figura_captura(FIG / "app_produccion.png", 15, "Captura 5")
nota("Tablero publicado en " + RENDER + ". Captura propia.")

H1("Resultados")
H2("Aplicación web y contenedor")
P("La aplicación expone siete *endpoints* (un tablero HTML, cinco servicios JSON y la documentación "
  "OpenAPI). La imagen Docker se construye y arranca correctamente: el trabajo `docker` del workflow "
  "levanta el contenedor y confirma que `/health` responde `status: ok` antes de autorizar el "
  "despliegue.")
H2("Pruebas y cobertura")
P("Las 37 pruebas (30 de la EA2 más 7 de la API web con `TestClient`) pasan en Python 3.10, 3.11 y "
  "3.12 con una cobertura superior al 95 %. La prueba de regresión mantiene la conclusión de la EA1 "
  "—el artículo se ofrece 17,05 % por encima del promedio de su mercado— tanto en el análisis como "
  "en el endpoint `/api/indicadores` (Tabla 6).")
rotulo("Tabla", "Posicionamiento del artículo analizado frente a su mercado")
tabla(["Indicador", "Valor"], [
    ["Artículos competidores rastreados", "12"],
    ["Precio del artículo analizado", "$ 1.499.900 COP"],
    ["Precio promedio / mediana del mercado", "$ 1.281.416 / $ 1.229.450 COP"],
    ["Desviación frente al promedio", "+17,05 %"],
    ["Ranking de precio (1 = más barato)", "10 de 12"],
    ["Calificación del artículo / del mercado", "4,7 / 4,56"],
], [1.7, 1.3])
rotulo("Figura", "Precio del artículo frente a la competencia y relación precio-calificación")
figura(FIG / "analisis_precios.png", 16.5)
nota("El artículo analizado aparece en rojo; el tamaño del punto representa el número de opiniones. "
     "Generado por `reporte.graficar` y servido por el endpoint `/grafica.png`.")
H2("Despliegue en la nube")
P("Cada fusión en `main` dispara `cd-render.yml`, que despliega el servicio en **" + RENDER + "** y "
  "verifica con una prueba de humo que responde en producción. El reporte estático de la EA2 sigue "
  "publicándose en paralelo en GitHub Pages (" + PAGES + "), de modo que el proyecto mantiene dos "
  "destinos de despliegue automatizados: un sitio estático y un servicio en ejecución.")

H1("Conclusiones")
lista([
    "La contenerización con Docker resolvió la brecha entre «funciona en mi máquina» y «funciona en "
    "producción»: la misma imagen que se verifica en CI es la que se despliega, lo que hace el "
    "despliegue predecible y portable entre proveedores de nube.",
    "Encadenar el despliegue tras las pruebas y la verificación del contenedor (`needs`) convierte "
    "el pipeline en una puerta de calidad: solo llega a la nube el código que pasó `ruff`, las "
    "pruebas, la cobertura y el arranque del contenedor.",
    "Configurar la aplicación mediante variables de entorno permite usar el mismo artefacto en "
    "desarrollo y en producción, y mantener fuera del código las credenciales (el *Deploy Hook* "
    "vive como *secret* de GitHub, no en el repositorio).",
    "La prueba de humo contra la URL pública es la que realmente confirma el despliegue: verifica, "
    "desde fuera, que el servicio quedó en línea, y no solo que el proceso de despliegue terminó.",
    "El proyecto completó el ciclo DevOps de las tres evidencias: de la extracción de datos (EA1) al "
    "software versionado y probado con CI/CD (EA2) y, finalmente, al despliegue automatizado de un "
    "servicio en la nube (EA3), documentado y reproducible en un repositorio público.",
])

H1("Bibliografía")
for ref in [
    "Chacon, S., y Straub, B. (2014). *Pro Git* (2.ª ed.). Apress. https://git-scm.com/book/es/v2",
    "Congreso de la República de Colombia. (2012). *Ley 1581 de 2012, por la cual se dictan "
    "disposiciones generales para la protección de datos personales*. Diario Oficial No. 48.587.",
    "Conventional Commits. (2019). *Conventional Commits 1.0.0*. "
    "https://www.conventionalcommits.org/es/v1.0.0/",
    "Docker Inc. (2024). *Docker documentation*. https://docs.docker.com/",
    "Driessen, V. (2010, 5 de enero). *A successful Git branching model*. nvie.com. "
    "https://nvie.com/posts/a-successful-git-branching-model/",
    "Fowler, M. (2006, 1 de mayo). *Continuous integration*. martinfowler.com. "
    "https://martinfowler.com/articles/continuousIntegration.html",
    "GitHub. (s. f.-a). *Documentación de GitHub Actions*. GitHub Docs. Recuperado el 25 de "
    "noviembre de 2026, de https://docs.github.com/es/actions",
    "GitHub. (s. f.-b). *Uso de secretos cifrados en un flujo de trabajo*. GitHub Docs. Recuperado "
    "el 25 de noviembre de 2026, de https://docs.github.com/es/actions/security-guides/"
    "using-secrets-in-github-actions",
    "Humble, J., y Farley, D. (2010). *Continuous delivery: Reliable software releases through "
    "build, test, and deployment automation*. Addison-Wesley.",
    "Kim, G., Humble, J., Debois, P., y Willis, J. (2016). *The DevOps handbook: How to create "
    "world-class agility, reliability, and security in technology organizations*. IT Revolution Press.",
    "Krekel, H., y pytest-dev team. (2024). *pytest documentation*. https://docs.pytest.org/",
    "Merkel, D. (2014). Docker: Lightweight Linux containers for consistent development and "
    "deployment. *Linux Journal, 2014*(239).",
    "Ramírez, S. (2024). *FastAPI documentation*. https://fastapi.tiangolo.com/",
    "Render. (2024). *Render documentation*. https://render.com/docs",
    "Encode. (2024). *Uvicorn: an ASGI web server for Python*. https://www.uvicorn.org/",
]:
    referencia(ref)

H1("Anexos")
H2("Anexo A. Repositorio y servicios desplegados")
P("Repositorio de GitHub (código fuente, historial, *pull requests* y ejecuciones de GitHub "
  "Actions): **" + REPO + "**")
P("Aplicación web desplegada en la nube (Render): **" + RENDER + "**")
P("Reporte estático desplegado en GitHub Pages (EA2): **" + PAGES + "**")
H2("Anexo B. Código fuente y descripción de la implementación")
P("Los componentes añadidos en la EA3 sobre el paquete de la EA2 son:")
lista([
    "`src/ml_scraper/web.py`: aplicación FastAPI (tablero y API REST) configurada por variables de entorno.",
    "`Dockerfile` y `.dockerignore`: contenedor de la aplicación con usuario sin privilegios.",
    "`render.yaml`: definición del servicio en la nube como código (Blueprint de Render).",
    "`.github/workflows/cd-render.yml`: despliegue continuo (pruebas → Docker → Render → prueba de humo).",
    "`tests/test_web.py`: 7 pruebas de la API con `TestClient`.",
    "`docs/DESPLIEGUE.md`: guía detallada del despliegue.",
    "`notebooks/Pedraza_Jeremy_Desplegando_EA3.ipynb`: cuaderno ejecutado que recorre el historial "
    "Git, ejecuta las pruebas, levanta la aplicación y consulta sus endpoints.",
])
H2("Anexo C. Reproducción local")
codigo('''
git clone ''' + REPO + '''.git
cd Programacion-Analisis-Datos
python -m venv .venv && .venv\\Scripts\\activate     # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
pytest --cov                                  # 37 pruebas, cobertura ≥ 95 %
uvicorn ml_scraper.web:app --reload           # aplicación web en http://localhost:8000
docker build -t ml-scraper-web . && docker run -p 8000:8000 ml-scraper-web
''')

doc.core_properties.title = "Optimización de procesos de desarrollo — EA3"
doc.core_properties.subject = "Automatización con GitHub Actions y despliegue de un servicio en la nube"
doc.core_properties.author = "Jeremy Iván Pedraza Hernández"
doc.save(SALIDA)
print("Documento generado:", SALIDA, "| tablas:", CONT["Tabla"], "figuras:", CONT["Figura"],
      "fragmentos:", CONT["Fragmento"], "| repo:", REPO)
