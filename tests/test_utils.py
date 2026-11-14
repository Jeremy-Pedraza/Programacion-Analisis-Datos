from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from ml_scraper import utils


@pytest.mark.parametrize(
    "texto, esperado",
    [("$ 1.499.900", 1499900), ("(1.248)", 1248), ("21 % OFF", 21), ("", None),
     (None, None), ("sin numeros", None)],
)
def test_a_entero(texto, esperado):
    assert utils.a_entero(texto) == esperado


def test_texto_de_devuelve_none_si_no_existe():
    sopa = BeautifulSoup("<div><p class='a'> hola </p></div>", "lxml")
    assert utils.texto_de(sopa, "p.a") == "hola"
    assert utils.texto_de(sopa, "p.inexistente") is None
    assert utils.texto_de(None, "p") is None


def test_obtener_html_offline(tmp_path: Path):
    snap = tmp_path / "snap.html"
    snap.write_text("<html>ok</html>", encoding="utf-8")
    assert utils.obtener_html("https://ejemplo", snap, offline=True) == "<html>ok</html>"


def test_obtener_html_en_vivo_usa_cabeceras_y_retardo(monkeypatch, tmp_path):
    llamadas = {}

    class Respuesta:
        text = "<html>vivo</html>"

        def raise_for_status(self):
            llamadas["status"] = True

    class Sesion:
        def get(self, url, headers, timeout):
            llamadas.update(url=url, headers=headers, timeout=timeout)
            return Respuesta()

    monkeypatch.setattr(utils.time, "sleep", lambda s: llamadas.setdefault("sleep", s))
    html = utils.obtener_html("https://ejemplo", tmp_path / "x", offline=False, sesion=Sesion())
    assert html == "<html>vivo</html>"
    assert llamadas["headers"]["User-Agent"].startswith("Mozilla")
    assert llamadas["sleep"] == utils.RETARDO_SEGUNDOS
    assert llamadas["status"] is True
