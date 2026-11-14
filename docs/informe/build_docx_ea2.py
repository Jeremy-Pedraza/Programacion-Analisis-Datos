"""Genera Pedraza_Jeremy_Optimizando_EA2.docx a partir de la plantilla institucional de la EA1.

Uso:  python build_docx_ea2.py [usuario_github]
Conserva portada, estilos y numeraciones del documento de la EA1 y reemplaza el contenido.
"""

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

BASE = Path(__file__).resolve().parent
import os
PLANTILLA = Path(os.environ.get("EA1_PLANTILLA", BASE.parents[2] / "EV1" / "Pedraza_Jeremy_Analizando_EA1.docx"))
SALIDA = BASE / "Pedraza_Jeremy_Optimizando_EA2.docx"
FIG = BASE / "figuras"
GH = sys.argv[1] if len(sys.argv) > 1 else "Jeremy-Pedraza"
REPO = f"https://github.com/{GH}/Programacion-Analisis-Datos"
PAGES = f"https://{GH.lower()}.github.io/Programacion-Analisis-Datos/"

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


reemplazar(hijos[2], "Evidencia de Aprendizaje 2")
reemplazar(hijos[3], "Optimizando la productividad en el mundo del software")
reemplazar(hijos[4], "Control de versiones y flujo DevOps con Git, GitHub y GitHub Actions")
reemplazar(hijos[13], "Unidad 2")

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

# eliminar contenido de la EA1 (desde «Introducción» hasta antes de sectPr)
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
    """Rótulo APA 7: número en negrita y título en cursiva, encima del elemento."""
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
    """Tabla con el formato de la EA1: bordes simples y encabezado gris D9D9D9."""
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
P("En la Evidencia de Aprendizaje 1 se aplicó la metodología de *web scraping* sobre Mercado Libre "
  "Colombia para evaluar la competitividad del Samsung Galaxy A55 5G 256 GB, combinando "
  "BeautifulSoup, Selenium y Scrapy en un cuaderno Jupyter. El resultado respondió la pregunta de "
  "negocio —el artículo se ofrece 17,05 % por encima del promedio de su mercado inmediato—, pero "
  "dejó al descubierto una limitación propia de los cuadernos aislados: no existía un historial de "
  "cambios, la única forma de comprobar que el código seguía funcionando era ejecutarlo y revisar "
  "las salidas a mano, y el resultado solo podía compartirse enviando archivos.")
P("La presente evidencia aborda esa limitación desde la perspectiva de la ingeniería de software. "
  "El código de la EA1 se reorganizó como un proyecto versionado con **Git** y alojado en "
  "**GitHub**, desarrollado mediante ramas, *commits* descriptivos, fusiones y *pull requests*, y "
  "se le incorporó un flujo **DevOps** implementado con **GitHub Actions**: cada cambio dispara "
  "pruebas automatizadas (integración continua) y cada versión aprobada se publica sin intervención "
  "manual como un reporte web en GitHub Pages (despliegue continuo).")
P("El documento retoma la descripción de la página y el artículo analizados, presenta el tema de "
  "interés y los objetivos, describe la metodología de *scraping* y su reingeniería como paquete "
  "de software, detalla el flujo DevOps implementado y expone los resultados y las conclusiones. "
  "Como anexo se entrega el código fuente completo en el repositorio de GitHub y el cuaderno "
  "Jupyter ejecutado.")

H1("Descripción de la página y el artículo analizado")
H2("La plataforma: Mercado Libre Colombia")
P("Mercado Libre (mercadolibre.com.co) es el *marketplace* líder en América Latina y opera en "
  "Colombia bajo un modelo de intermediación en el que miles de vendedores publican sus artículos "
  "sobre una misma infraestructura. Esta característica lo convierte en un objeto de estudio "
  "valioso: un mismo producto puede encontrarse publicado por distintos vendedores con precios, "
  "descuentos, condiciones de envío y reputaciones diferentes.")
P("Técnicamente, el sitio combina tres capas de información que justificaron el uso de "
  "herramientas distintas en la EA1: el HTML estático que devuelve el servidor (título, precio, "
  "descuento, especificaciones, vendedor), el contenido inyectado por JavaScript después de la "
  "carga (opiniones de compradores) y el listado de resultados distribuido en varias páginas "
  "(artículos competidores). Su marcado se apoya en el sistema de diseño Andes, con clases CSS "
  "estables (`ui-pdp-`, `ui-search-`, `poly-`) que permiten construir selectores legibles.")
H2("El artículo seleccionado")
P("El artículo analizado es el teléfono inteligente **Samsung Galaxy A55 5G de 256 GB y 8 GB de "
  "RAM**, en la categoría Celulares y Teléfonos > Celulares y Smartphones. Se eligió por pertenecer "
  "al segmento de mayor rotación del comercio electrónico colombiano, por contar con un volumen "
  "significativo de opiniones y por tener competidores directos en el mismo rango de precio. La "
  "Tabla 1 resume la ficha extraída, que el pipeline de la EA2 reproduce de forma idéntica.")
rotulo("Tabla", "Ficha del artículo analizado")
tabla(["Campo", "Valor extraído"], [
    ["Título", "Samsung Galaxy A55 5G 256 GB Azul Oscuro 8 GB RAM"],
    ["Precio actual", "$ 1.499.900 COP"],
    ["Precio anterior", "$ 1.899.900 COP (ahorro de $ 400.000)"],
    ["Calificación", "4,7 / 5"],
    ["Campos estructurados", "22 (13 de la ficha y 9 especificaciones técnicas)"],
    ["Opiniones recuperadas", "5 (contenido renderizado por JavaScript)"],
    ["Competidores rastreados", "12 artículos × 11 campos"],
], [1, 2.2])
nota("Datos extraídos del *snapshot* HTML de Mercado Libre Colombia versionado en `data/`. "
     "Elaboración propia.")

H1("Descripción del tema de interés")
P("El tema de interés de esta segunda evidencia es la **aplicación de prácticas DevOps a un "
  "proyecto de extracción y análisis de datos**. La pregunta orientadora es: ¿cómo garantizar que "
  "un proceso de *scraping* siga produciendo resultados correctos a medida que el código evoluciona "
  "y que esos resultados lleguen a sus usuarios sin pasos manuales?")
P("El interés es práctico. Un *scraper* es un software especialmente frágil: depende de un sitio "
  "que cambia sin previo aviso, de varias librerías con sus propias versiones y de decisiones de "
  "diseño (selectores, esperas, criterios de identificación del artículo) que se ajustan con "
  "frecuencia. Sin control de versiones, un cambio que rompe la extracción no deja rastro; sin "
  "pruebas automatizadas, el error se descubre cuando el análisis ya se ha compartido; y sin "
  "despliegue automatizado, cada actualización del reporte depende de que alguien recuerde "
  "ejecutar el cuaderno y distribuir el resultado.")
P("DevOps propone resolver estos problemas integrando desarrollo y operación mediante "
  "automatización y retroalimentación rápida (Kim et al., 2016). En concreto, se trabajó sobre "
  "tres prácticas: el control de versiones distribuido con un modelo de ramas explícito "
  "(Chacon y Straub, 2014; Driessen, 2010), la integración continua, en la que cada cambio se "
  "integra y verifica automáticamente (Fowler, 2006), y la entrega y el despliegue continuos, en los "
  "que el software se mantiene siempre en estado publicable y se libera mediante un proceso "
  "repetible (Humble y Farley, 2010).")

H1("Objetivos")
P("Los objetivos se formulan desde el rol de integrante de un equipo de desarrollo responsable del "
  "proyecto de *scraping* de la EA1, que debe gestionarlo con Git y GitHub y establecer un "
  "pipeline de CI/CD con GitHub Actions que integre pruebas automatizadas y despliegue continuo.")
H2("Objetivo general")
P("Implementar un flujo de trabajo DevOps para el proyecto de *web scraping* de Mercado Libre "
  "Colombia, utilizando Git y GitHub para el control de versiones y GitHub Actions para la "
  "integración de pruebas automatizadas y el despliegue continuo del reporte de análisis, "
  "documentado y presentado en un repositorio público de GitHub.")
H2("Objetivos específicos")
lista([
    "Reestructurar el código del cuaderno de la EA1 en un paquete Python modular y reutilizable, "
    "separando la lógica de extracción del origen del HTML para que pueda probarse de forma "
    "determinista.",
    "Gestionar el desarrollo con Git y GitHub aplicando un modelo de ramas (`main`, `develop`, "
    "`feature/*`, `fix/*`), *commits* con la convención *Conventional Commits*, fusiones sin avance "
    "rápido y *pull requests* revisados.",
    "Diseñar un conjunto de pruebas automatizadas unitarias, de regresión y de integración con "
    "`pytest` que verifique la extracción, los indicadores y la generación del reporte, con una "
    "cobertura mínima del 85 %.",
    "Configurar un workflow de integración continua en GitHub Actions que ejecute análisis "
    "estático, pruebas en varias versiones de Python y la araña de Scrapy en cada *push* y *pull "
    "request*.",
    "Configurar un workflow de despliegue continuo que, al fusionar en `main`, vuelva a probar el "
    "código, ejecute el pipeline de *scraping*, publique el reporte en GitHub Pages y verifique "
    "automáticamente que el sitio responde.",
], num=NUM_DECIMAL)
H2("Métricas de éxito")
P("La solución se considera exitosa si cumple los criterios verificables de la Tabla 2.")
rotulo("Tabla", "Métricas de éxito definidas para la solución")
tabla(["Métrica", "Criterio de aceptación", "Resultado"], [
    ["Uso de ramas", "≥ 1 rama por funcionalidad, fusionadas con --no-ff", "7 ramas de trabajo, 9 fusiones (cumple)"],
    ["Commits descriptivos", "100 % con Conventional Commits", "20/20 (cumple)"],
    ["Pull requests", "Integración a develop y a main mediante PR", "PR #1 y PR #2 fusionados (cumple)"],
    ["Pruebas automatizadas", "≥ 20 pruebas, 0 fallos", "30 pruebas, 0 fallos (cumple)"],
    ["Cobertura", "≥ 85 % del paquete", "93 % (cumple)"],
    ["Integración continua", "CI en cada push y PR, matriz ≥ 3 versiones", "Python 3.10–3.12 (cumple)"],
    ["Despliegue", "Publicación automática y prueba de humo", "GitHub Pages, smoke test en verde (cumple)"],
    ["Regresión de negocio", "Mantener la conclusión de la EA1", "+17,05 % vs. promedio (cumple)"],
], [1.1, 1.6, 1.3])

H1("Metodología empleada de scraping")
P("La metodología de extracción es la definida en la EA1 y se mantiene sin cambios en su lógica: "
  "cada capa de información se atiende con la herramienta adecuada. Lo que cambia en la EA2 es su "
  "organización como software: el código pasó de celdas secuenciales a un paquete Python "
  "(`ml_scraper`) con módulos de responsabilidad única, lo que permite versionarlos, probarlos y "
  "desplegarlos por separado (Tabla 3).")
rotulo("Tabla", "Reorganización del código de la EA1 en el paquete ml_scraper")
tabla(["Fase", "Herramienta", "Módulo", "Responsabilidad"], [
    ["1. Ficha de producto", "BeautifulSoup", "producto.py", "Selectores CSS defensivos de 13 campos y tabla de especificaciones"],
    ["2. Opiniones", "Selenium", "resenas.py", "Chrome *headless*, espera explícita y respaldo al *snapshot*"],
    ["3. Competencia", "Scrapy", "competencia.py, spiders/", "Extracción por tarjeta compartida por la araña y las pruebas"],
    ["4. Análisis", "pandas", "analisis.py", "Indicadores de posicionamiento y métricas de éxito"],
    ["5. Reporte", "Matplotlib", "reporte.py", "Gráfico y sitio estático para GitHub Pages"],
    ["Transversal", "requests", "utils.py, pipeline.py", "Normalización, modo offline/en vivo y orquestación (CLI)"],
], [1.1, 1, 1.2, 2.4])
H2("BeautifulSoup: contenido estático")
P("El HTML se obtiene con `requests` enviando cabeceras `User-Agent` y `Accept-Language` de un "
  "navegador real —sin ellas la plataforma responde con 403— y se analiza con el motor `lxml`. Los "
  "selectores se centralizaron en un diccionario y cada valor se recupera con la función "
  "`texto_de`, que devuelve `None` cuando el nodo no existe. Esta extracción defensiva, ya presente "
  "en la EA1, quedó ahora protegida por pruebas que alimentan el extractor con HTML vacío o "
  "incompleto y verifican que no se produzcan excepciones (Richardson, 2024).")
rotulo("Fragmento", "Extracción defensiva de la ficha (src/ml_scraper/producto.py)")
codigo('''
def extraer_ficha(html: str, url: str = URL_PRODUCTO) -> dict:
    sopa = BeautifulSoup(html, "lxml")
    s = SELECTORES_FICHA
    ficha = {
        "titulo": texto_de(sopa, s["titulo"]),
        "precio_actual": a_entero(texto_de(sopa, s["precio_actual"])),
        "precio_anterior": a_entero(texto_de(sopa, s["precio_anterior"])),
        "calificacion": _a_flotante(texto_de(sopa, s["calificacion"])),
        ...
    }
    ficha["ahorro_cop"] = (ficha["precio_anterior"] or 0) - (ficha["precio_actual"] or 0)
    return ficha
''')
H2("Selenium: contenido renderizado por JavaScript")
P("Las opiniones se inyectan en el DOM después de la carga inicial, por lo que requieren un "
  "navegador automatizado. Se usa Chrome en modo *headless* con `WebDriverWait` y la condición "
  "`presence_of_element_located` en lugar de pausas fijas (Selenium Project, 2024). En la EA2 el "
  "import de Selenium se hizo diferido: si el navegador no está disponible —como ocurre en los "
  "*runners* de integración continua—, la función recurre al *snapshot* con la misma lógica de "
  "extracción, y una prueba automatizada verifica ese comportamiento simulando la ausencia de la "
  "librería.")
H2("Scrapy: listado de competencia")
P("La araña `competencia_ml` conserva la configuración de *scraping* responsable de la EA1: "
  "`ROBOTSTXT_OBEY = True`, `DOWNLOAD_DELAY = 2`, `CONCURRENT_REQUESTS = 4`, reintentos y "
  "`AUTOTHROTTLE` (Zyte, 2024). La mejora de diseño consistió en extraer la lógica de cada tarjeta a "
  "la función `extraer_tarjeta` del módulo `competencia.py`. La araña la invoca y las pruebas la "
  "validan directamente, sin arrancar el reactor de Twisted; además, el workflow de CI ejecuta la "
  "araña real contra el *snapshot* y comprueba que recupera al menos diez artículos.")
H2("Reproducibilidad: modo offline")
P("El pipeline acepta dos modos. Por defecto procesa el *snapshot* HTML versionado en `data/`, que "
  "replica el DOM real de la plataforma; con la opción `--en-vivo` realiza peticiones reales. Los "
  "selectores son idénticos en ambos casos. Esta separación es la que hace posible la integración "
  "continua: las pruebas producen siempre el mismo resultado, no dependen del estado del sitio y no "
  "generan tráfico hacia Mercado Libre en cada *commit*.")
H2("Consideraciones éticas y legales")
lista([
    "Se extrae únicamente información pública de catálogo, sin datos personales identificables, en "
    "concordancia con la Ley 1581 de 2012 (Congreso de la República de Colombia, 2012).",
    "Se respeta `robots.txt`, se aplica un retardo de dos segundos entre peticiones y una "
    "concurrencia máxima de cuatro.",
    "Los workflows de CI/CD trabajan sobre el *snapshot*; el modo en vivo solo se activa de forma "
    "manual, lo que evita peticiones automáticas recurrentes al sitio.",
    "La finalidad es exclusivamente académica y los datos no se redistribuyen con fines comerciales.",
])

H1("Implementación del flujo DevOps")
P("El flujo implementado recorre las etapas clásicas de DevOps —planificar, codificar, construir, "
  "probar, liberar y desplegar— apoyándose en tres componentes de GitHub: el repositorio con su "
  "modelo de ramas, los *pull requests* como punto de revisión e integración, y GitHub Actions como "
  "motor de automatización (GitHub, s. f.-a).")
H2("Repositorio y estructura del proyecto")
P(f"El proyecto se aloja en el repositorio público **{REPO}**. Su estructura separa código, "
  "pruebas, datos de referencia, automatización y documentación:")
rotulo("Fragmento", "Estructura del repositorio Programacion-Analisis-Datos")
codigo('''
Programacion-Analisis-Datos/
├── .github/workflows/ci.yml       integración continua
├── .github/workflows/cd.yml       despliegue continuo
├── .github/pull_request_template.md
├── data/                          snapshot HTML versionado
├── notebooks/                     cuaderno Jupyter de la EA2
├── spiders/competencia_spider.py  araña Scrapy
├── src/ml_scraper/                paquete: utils, producto, resenas,
│                                  competencia, analisis, reporte, pipeline
├── tests/                         30 pruebas pytest
├── README.md · CONTRIBUTING.md · CHANGELOG.md
└── pyproject.toml · requirements.txt · requirements-dev.txt
''')
H2("Modelo de ramas")
P("Se adoptó un GitFlow simplificado (Driessen, 2010). La rama `main` contiene únicamente código "
  "liberado y cada *commit* que llega a ella se despliega; `develop` integra las funcionalidades "
  "terminadas; y cada funcionalidad o corrección se desarrolla en una rama propia creada desde "
  "`develop`. Todas las integraciones se hicieron con fusiones sin avance rápido (`--no-ff`), de "
  "modo que el historial conserva explícitamente qué *commits* pertenecieron a cada rama (Figura 1).")
rotulo("Figura", "Historial de ramas y fusiones del repositorio")
figura(FIG / "modelo_ramas.png", 16.5)
nota("Cada punto verde es un *commit* en una rama `feature/*`; los puntos azules sobre `develop` "
     "son las fusiones. La rama `docs/notebook-ea2` se integra a `develop` mediante el PR #1 y "
     "`develop` se libera hacia `main` mediante el PR #2, que dispara el despliegue. Elaboración "
     "propia a partir de `git log --graph`.")
rotulo("Tabla", "Ramas del proyecto")
tabla(["Rama", "Propósito", "Commits"], [
    ["feature/extraccion-producto", "Utilidades, ficha (BeautifulSoup) y opiniones (Selenium)", "3"],
    ["feature/rastreo-competencia", "Extracción del listado y araña Scrapy", "2"],
    ["feature/analisis-reporte", "Indicadores, gráfico, sitio estático y CLI", "3"],
    ["feature/ci-github-actions", "Workflow de CI, plantilla de PR y guía de contribución", "2"],
    ["feature/cd-github-pages", "Workflow de CD y README", "2"],
    ["fix/contraste-encabezado", "Corrección de contraste del reporte en modo oscuro", "1"],
    ["docs/notebook-ea2", "Cuaderno, cobertura, CHANGELOG, URLs, CI e informe (PR #1)", "6"],
], [1.6, 2.4, 0.6])
H2("Convención de commits")
P("Los mensajes siguen la especificación *Conventional Commits* (Conventional Commits, 2019): "
  "`tipo(alcance): descripción en imperativo`, con un cuerpo que explica el porqué cuando no es "
  "evidente. Los tipos usados fueron `feat` (funcionalidad), `fix` (corrección), `ci` "
  "(automatización), `docs` (documentación) y `chore` (mantenimiento). Esta convención hace el "
  "historial legible y permite, por ejemplo, generar el CHANGELOG a partir de él.")
rotulo("Fragmento", "Extracto del historial (git log --oneline --graph)")
codigo('''
*   Merge branch 'fix/contraste-encabezado' into develop
|\\
| * fix(reporte): contraste del encabezado en modo oscuro
|/
*   Merge branch 'feature/cd-github-pages' into develop
|\\
| * docs(readme): propósito, estructura, ejecución y flujo DevOps
| * ci(cd): despliegue continuo del reporte en GitHub Pages
|/
*   Merge branch 'feature/ci-github-actions' into develop
|\\
| * docs: guía de contribución, modelo de ramas y plantilla de PR
| * ci: workflow de integración continua con ruff, pytest y Scrapy
|/
*   Merge branch 'feature/analisis-reporte' into develop
|\\
| * feat(pipeline): orquestador de las cinco fases y CLI python -m ml_scraper
| * feat(reporte): gráfico y sitio estático con los resultados
| * feat(analisis): indicadores de posicionamiento y métricas de éxito
|/
...
* chore: estructura inicial del proyecto y snapshot HTML de la EA1
''')
H2("Pull requests y protección de ramas")
P("Los *pull requests* son el punto en el que el trabajo de una rama se propone, se revisa y se "
  "integra (GitHub, s. f.-b). Cada PR utiliza la plantilla `.github/pull_request_template.md`, que "
  "exige describir el cambio, clasificarlo y confirmar que las pruebas y el *lint* pasan. La guía "
  "`CONTRIBUTING.md` establece como política que `main` y `develop` solo reciben cambios mediante "
  "PR y que los *checks* de CI (`Lint (ruff)`, `Pruebas (Python 3.10/3.11/3.12)` y `Araña "
  "Scrapy`) deben estar en verde antes de fusionar. Se gestionaron dos PR:")
lista([
    "**PR #1 — `docs/notebook-ea2` → `develop`:** incorpora el cuaderno de la EA2, la configuración "
    "de cobertura, el CHANGELOG y el informe. Su apertura disparó el workflow de CI sobre el "
    "resultado de la fusión, y se fusionó con *Create a merge commit* cuando quedó en verde.",
    "**PR #2 — `develop` → `main` (release v1.0.0):** promueve la versión a producción. Al "
    "fusionarlo se ejecutó el workflow de CD y se creó la etiqueta anotada `v1.0.0` sobre el "
    "*commit* de fusión.",
])
H2("Pruebas automatizadas")
P("Las pruebas son la condición que hace seguro el despliegue continuo: sin ellas, publicar en "
  "cada fusión solo automatizaría la propagación de errores (Humble y Farley, 2010). Se escribieron "
  "30 pruebas con `pytest` (Krekel y pytest-dev team, 2024) organizadas en tres niveles: "
  "**unitarias**, que verifican funciones aisladas como la normalización de precios o el cálculo "
  "de descuentos; de **regresión**, que fijan la conclusión de negocio de la EA1 para que una "
  "refactorización no la altere silenciosamente; y de **integración**, que ejecutan el pipeline "
  "completo y verifican los archivos y el sitio generados (Tabla 5).")
rotulo("Tabla", "Pruebas automatizadas por módulo")
tabla(["Archivo de prueba", "Pruebas", "Qué verifica"], [
    ["test_utils.py", "9", "Conversión de precios, extracción defensiva, modo offline y en vivo (cabeceras y retardo simulados)"],
    ["test_producto.py", "4", "Campos de la ficha, cobertura mínima, HTML vacío y calificación no numérica"],
    ["test_resenas.py", "3", "Opiniones del DOM, ausencia de opiniones y respaldo sin Selenium"],
    ["test_competencia.py", "4", "Esquema de 11 campos, cálculo de descuentos, tarjeta incompleta y paginación"],
    ["test_analisis.py", "7", "Identificación del artículo, exclusión de reacondicionados, indicadores y regresión +17,05 %"],
    ["test_pipeline.py", "3", "Pipeline completo, sitio con commit/build de CI y código de salida de la CLI"],
], [1.3, 0.6, 3.2])
rotulo("Fragmento", "Prueba de regresión de la conclusión de negocio (tests/test_analisis.py)")
codigo('''
def test_resultado_de_negocio_ea1(df_competencia, ficha):
    """Regresión: la conclusión de la EA1 (≈ +17 % sobre el promedio) debe mantenerse."""
    ind = calcular_indicadores(df_competencia, ficha)
    assert ind["Desviación vs. promedio (%)"] == pytest.approx(17.05, abs=0.01)
''')
H2("Integración continua (ci.yml)")
P("El workflow de CI se ejecuta en cada *push* a las ramas de trabajo y en cada *pull request* "
  "hacia `main` o `develop` (Figura 2, parte superior). Primero corre el análisis estático con "
  "`ruff`; si pasa, se ejecutan en paralelo las pruebas en una matriz de tres versiones de Python "
  "—con umbral de cobertura del 85 % que hace fallar el trabajo si no se alcanza— y la araña de "
  "Scrapy contra el *snapshot*. Los reportes de cobertura y de pruebas (formato JUnit) se publican "
  "como artefactos del *run*. Un bloque `concurrency` cancela ejecuciones obsoletas de la misma rama.")
rotulo("Figura", "Pipeline de integración y despliegue continuo con GitHub Actions")
figura(FIG / "pipeline_cicd.png", 16.5)
nota("Elaboración propia a partir de `.github/workflows/ci.yml` y `cd.yml`.")
H2("Despliegue continuo (cd.yml)")
P("El workflow de CD se dispara al fusionar en `main`, al crear una etiqueta `v*` o manualmente "
  "(con la opción de ejecutar el *scraping* en vivo). Consta de tres trabajos encadenados con "
  "`needs`: **build** vuelve a ejecutar las pruebas como puerta de calidad, ejecuta el pipeline "
  "(`python -m ml_scraper`), guarda los datos extraídos como artefacto y empaqueta el sitio; "
  "**deploy** lo publica en GitHub Pages en el entorno `github-pages` (GitHub, s. f.-c); y "
  "**smoke** realiza una prueba de humo que consulta la URL publicada y verifica que contiene el "
  "reporte. Si cualquier paso falla, el despliegue se detiene y la versión anterior sigue en línea.")
rotulo("Fragmento", "Trabajos de despliegue (extracto de .github/workflows/cd.yml)")
codigo('''
  deploy:
    name: Desplegar en GitHub Pages
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4

  smoke:
    name: Prueba de humo del despliegue
    needs: deploy
    steps:
      - run: |
          URL="https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}/"
          curl -fsSL "$URL" | grep -q "Galaxy A55"
''')

H1("Resultados")
H2("Control de versiones")
P("El repositorio registra 20 *commits* de trabajo y 9 fusiones sin avance rápido distribuidos en "
  "siete ramas de trabajo, incluidas las fusiones de los dos *pull requests* de integración y "
  "liberación. El 100 % de los "
  "mensajes cumple la convención *Conventional Commits*, y cada *commit* intermedio de las ramas "
  "`feature/*` se verificó con la batería de pruebas antes de fusionarse, de modo que cualquier "
  "punto del historial es ejecutable.")
H2("Pruebas y cobertura")
P("Las 30 pruebas pasan en Python 3.10, 3.11 y 3.12, con una cobertura total del 93 % (Tabla 6). "
  "La cobertura parcial de `resenas.py` corresponde al bloque que controla Chrome, que no puede "
  "ejecutarse en un *runner* sin navegador; su ruta alternativa sí está probada.")
rotulo("Tabla", "Cobertura de pruebas por módulo")
tabla(["Módulo", "Sentencias", "Sin cubrir", "Cobertura"], [
    ["analisis.py", "21", "0", "100 %"], ["producto.py", "23", "0", "100 %"],
    ["reporte.py", "68", "0", "100 %"], ["utils.py", "27", "0", "100 %"],
    ["pipeline.py", "46", "1", "98 %"], ["competencia.py", "21", "2", "90 %"],
    ["resenas.py", "32", "13", "59 %"], ["**Total**", "**239**", "**16**", "**93 %**"],
], [1.6, 1, 1, 1])
nota("Resultado de `pytest --cov`; el punto de entrada `__main__.py` se excluye de la medición.")
H2("Despliegue del reporte")
P(f"Cada fusión en `main` publica el reporte en **{PAGES}**. La página presenta los indicadores "
  "clave, la visualización, la tabla de competidores, la ficha, las opiniones, las métricas de "
  "éxito y los datos descargables en CSV, e indica en el pie el número de *build* y el *commit* que "
  "la generó, lo que vincula cada versión publicada con su origen exacto en el historial (Figura 3).")
P("El primer despliegue evidenció el valor de la prueba de humo. La ejecución de CD posterior al "
  "PR #2 construyó y publicó el sitio, pero el trabajo **smoke** falló: la URL respondía 404. El "
  "diagnóstico mostró que la cuenta tenía configurado un dominio personalizado heredado del sitio "
  "de usuario (`jeremy-pedraza.github.io`), que redirigía todos los proyectos a un servidor externo "
  "sin el reporte. Tras retirar esa configuración se relanzó el workflow manualmente y la ejecución "
  "#2 completó los tres trabajos en verde. Sin la prueba de humo, el pipeline habría reportado éxito "
  "con un sitio inaccesible.")
rotulo("Figura", "Reporte generado por el pipeline y publicado en GitHub Pages")
figura(FIG / "sitio_reporte.png", 14)
nota(f"Captura del sitio publicado en {PAGES} (ejecución #2 de CD, *commit* `5a0bfc3`).")
H2("Resultados del análisis")
P("La prueba de regresión garantiza que la reingeniería no alteró los hallazgos de la EA1, que el "
  "pipeline reproduce de forma idéntica en cada despliegue (Tabla 7 y Figura 4).")
rotulo("Tabla", "Posicionamiento del artículo analizado frente a su mercado")
tabla(["Indicador", "Valor"], [
    ["Artículos competidores rastreados", "12"],
    ["Precio del artículo analizado", "$ 1.499.900 COP"],
    ["Precio mínimo / máximo del mercado", "$ 899.900 / $ 1.799.900 COP"],
    ["Precio promedio / mediana", "$ 1.281.416 / $ 1.229.450 COP"],
    ["Desviación frente al promedio", "+17,05 %"],
    ["Ranking de precio (1 = más barato)", "10 de 12"],
    ["Descuento promedio del mercado", "20,9 %"],
    ["Calificación del artículo / del mercado", "4,7 / 4,56"],
], [1.6, 1.4])
rotulo("Figura", "Precio del artículo frente a la competencia y relación precio-calificación")
figura(FIG / "analisis_precios.png", 16.5)
nota("El artículo analizado aparece en rojo; el tamaño del punto representa el número de "
     "opiniones. Generado automáticamente por `reporte.graficar`.")

H1("Conclusiones")
lista([
    "Git y GitHub transformaron un cuaderno aislado en un activo trazable: cada cambio del proyecto "
    "tiene autor, motivo, rama de origen y revisión, y cualquier versión puede reconstruirse. El "
    "modelo de ramas con fusiones `--no-ff` hace visible en el historial cómo se construyó cada "
    "funcionalidad.",
    "Las pruebas automatizadas son la condición que vuelve seguro el despliegue continuo. La prueba "
    "de regresión sobre el +17,05 % convierte la conclusión de negocio de la EA1 en un contrato "
    "verificable: si una modificación la alterara, el *pull request* quedaría bloqueado.",
    "Separar la lógica de extracción del origen del HTML fue la decisión de diseño más importante. "
    "Permitió probar el *scraping* de forma determinista en CI, reutilizar la misma función en la "
    "araña de Scrapy y en las pruebas, y evitar tráfico automático hacia Mercado Libre.",
    "GitHub Actions integró en un mismo lugar el código, las pruebas y el despliegue. El encadenamiento "
    "lint → pruebas → construcción → despliegue → prueba de humo asegura que solo se publica lo que "
    "pasó todas las verificaciones y que lo publicado efectivamente está en línea.",
    "La corrección de contraste, detectada al revisar el reporte y resuelta en una rama `fix/*`, "
    "ilustra el ciclo completo de mejora continua: el defecto se aísla, se corrige con un *commit* "
    "explicado, se integra con las pruebas en verde y se despliega sin pasos manuales.",
])

H1("Bibliografía")
for ref in [
    "Chacon, S., y Straub, B. (2014). *Pro Git* (2.ª ed.). Apress. https://git-scm.com/book/es/v2",
    "Congreso de la República de Colombia. (2012). *Ley 1581 de 2012, por la cual se dictan "
    "disposiciones generales para la protección de datos personales*. Diario Oficial No. 48.587.",
    "Conventional Commits. (2019). *Conventional Commits 1.0.0*. "
    "https://www.conventionalcommits.org/es/v1.0.0/",
    "Driessen, V. (2010, 5 de enero). *A successful Git branching model*. nvie.com. "
    "https://nvie.com/posts/a-successful-git-branching-model/",
    "Fowler, M. (2006, 1 de mayo). *Continuous integration*. martinfowler.com. "
    "https://martinfowler.com/articles/continuousIntegration.html",
    "GitHub. (s. f.-a). *Documentación de GitHub Actions*. GitHub Docs. Recuperado el 14 de "
    "noviembre de 2026, de https://docs.github.com/es/actions",
    "GitHub. (s. f.-b). *Acerca de las solicitudes de incorporación de cambios*. GitHub Docs. "
    "Recuperado el 14 de noviembre de 2026, de https://docs.github.com/es/pull-requests/"
    "collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/"
    "about-pull-requests",
    "GitHub. (s. f.-c). *Uso de flujos de trabajo personalizados con GitHub Pages*. GitHub Docs. "
    "Recuperado el 14 de noviembre de 2026, de https://docs.github.com/es/pages/"
    "getting-started-with-github-pages/using-custom-workflows-with-github-pages",
    "Humble, J., y Farley, D. (2010). *Continuous delivery: Reliable software releases through "
    "build, test, and deployment automation*. Addison-Wesley.",
    "Kim, G., Humble, J., Debois, P., y Willis, J. (2016). *The DevOps handbook: How to create "
    "world-class agility, reliability, and security in technology organizations*. IT Revolution Press.",
    "Krekel, H., y pytest-dev team. (2024). *pytest documentation*. https://docs.pytest.org/",
    "McKinney, W. (2022). *Python for data analysis: Data wrangling with pandas, NumPy, and "
    "Jupyter* (3.ª ed.). O'Reilly Media.",
    "Mitchell, R. (2018). *Web scraping with Python: Collecting more data from the modern web* "
    "(2.ª ed.). O'Reilly Media.",
    "Richardson, L. (2024). *Beautiful Soup documentation* (versión 4.12). "
    "https://www.crummy.com/software/BeautifulSoup/bs4/doc/",
    "Selenium Project. (2024). *Selenium WebDriver documentation*. "
    "https://www.selenium.dev/documentation/webdriver/",
    "Zyte. (2024). *Scrapy documentation* (versión 2.11). https://docs.scrapy.org/en/latest/",
]:
    referencia(ref)

H1("Anexos")
H2("Anexo A. Repositorio y reporte desplegado")
P(f"Repositorio de GitHub (código fuente completo, historial, *pull requests* y ejecuciones de "
  f"GitHub Actions): **{REPO}**")
P(f"Reporte desplegado en GitHub Pages: **{PAGES}**")
H2("Anexo B. Código fuente y descripción de la implementación")
P("El código fuente se entrega en el repositorio. Sus componentes son:")
lista([
    "`src/ml_scraper/utils.py`: cabeceras HTTP, `a_entero`, `texto_de` y `obtener_html` (offline/en vivo).",
    "`src/ml_scraper/producto.py`: `extraer_ficha` y `extraer_especificaciones` (BeautifulSoup).",
    "`src/ml_scraper/resenas.py`: `html_con_selenium` con respaldo y `extraer_resenas`.",
    "`src/ml_scraper/competencia.py`: `extraer_tarjeta`, `extraer_listado` y `siguiente_pagina`.",
    "`spiders/competencia_spider.py`: araña Scrapy con configuración de *scraping* responsable.",
    "`src/ml_scraper/analisis.py`: `marcar_articulo`, `calcular_indicadores` y `evaluar_metricas_exito`.",
    "`src/ml_scraper/reporte.py`: `graficar` y `generar_sitio` (HTML adaptable a modo claro y oscuro).",
    "`src/ml_scraper/pipeline.py`: orquestador `ejecutar` y CLI `python -m ml_scraper [--en-vivo] [--selenium]`.",
    "`tests/`: 30 pruebas `pytest`; `.github/workflows/`: `ci.yml` y `cd.yml`.",
    "`notebooks/Pedraza_Jeremy_Optimizando_EA2.ipynb`: cuaderno ejecutado que recorre el historial "
    "Git, ejecuta las pruebas y el pipeline y presenta los workflows.",
])
H2("Anexo C. Reproducción local")
codigo(f'''
git clone {REPO}.git
cd Programacion-Analisis-Datos
python -m venv .venv && .venv\\Scripts\\activate     # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
pytest --cov                # 30 pruebas, cobertura 93 %
ruff check .                # análisis estático
python -m ml_scraper        # genera out/ y site/index.html
''')

doc.core_properties.title = "Optimizando la productividad en el mundo del software — EA2"
doc.core_properties.subject = "Control de versiones y DevOps con Git, GitHub y GitHub Actions"
doc.core_properties.author = "Jeremy Iván Pedraza Hernández"
doc.save(SALIDA)
print("Documento generado:", SALIDA, "| tablas:", CONT["Tabla"], "figuras:", CONT["Figura"],
      "fragmentos:", CONT["Fragmento"], "| repo:", REPO)
