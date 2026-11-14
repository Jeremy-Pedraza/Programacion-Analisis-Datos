"""Araña de Scrapy para el rastreo del listado de competencia.

Reutiliza ``ml_scraper.competencia.extraer_tarjeta`` para que la lógica de extracción
sea la misma que validan las pruebas automatizadas.

Ejecución::

    scrapy runspider spiders/competencia_spider.py -a start_url=file:///.../data/ml_resultados.html
"""

import scrapy
from bs4 import BeautifulSoup

from ml_scraper.competencia import SELECTOR_TARJETA, extraer_tarjeta
from ml_scraper.utils import HEADERS


class CompetenciaSpider(scrapy.Spider):
    name = "competencia_ml"

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,  # scraping responsable
        "CONCURRENT_REQUESTS": 4,
        "RETRY_TIMES": 3,
        "AUTOTHROTTLE_ENABLED": True,
        "USER_AGENT": HEADERS["User-Agent"],
        "FEEDS": {"out/competencia_scrapy.json": {"format": "json", "encoding": "utf-8",
                                                  "overwrite": True, "indent": 2}},
        "LOG_LEVEL": "ERROR",
    }

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]

    def parse(self, response):
        sopa = BeautifulSoup(response.text, "lxml")
        for posicion, tarjeta in enumerate(sopa.select(SELECTOR_TARJETA), start=1):
            yield extraer_tarjeta(tarjeta, posicion)

        siguiente = response.css("a.andes-pagination__link[title='Siguiente']::attr(href)").get()
        if siguiente:
            yield response.follow(siguiente, callback=self.parse)
