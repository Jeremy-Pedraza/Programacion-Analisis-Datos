"""Pruebas de integración: el pipeline completo genera el sitio que se despliega."""

from pathlib import Path

from ml_scraper import pipeline

DATA = Path(__file__).resolve().parents[1] / "data"


def test_pipeline_genera_artefactos(tmp_path):
    r = pipeline.ejecutar(offline=True, data_dir=DATA, out_dir=tmp_path / "out",
                          site_dir=tmp_path / "site")
    for nombre in ("producto_beautifulsoup.csv", "resenas_selenium.csv",
                   "competencia.json", "resumen_analisis.csv"):
        assert (tmp_path / "out" / nombre).stat().st_size > 0
    sitio = tmp_path / "site"
    html = (sitio / "index.html").read_text(encoding="utf-8")
    assert "Galaxy A55" in html and "<table>" in html
    assert (sitio / "analisis_precios.png").stat().st_size > 10_000
    assert (sitio / "data" / "competencia.csv").exists()
    assert (sitio / ".nojekyll").exists()
    assert r["metricas"]["Cumple"].all()


def test_sitio_muestra_commit_de_ci(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_SHA", "abcdef1234567")
    monkeypatch.setenv("GITHUB_RUN_NUMBER", "42")
    pipeline.ejecutar(data_dir=DATA, out_dir=tmp_path / "o", site_dir=tmp_path / "s")
    html = (tmp_path / "s" / "index.html").read_text(encoding="utf-8")
    assert "abcdef1" in html and "Build #42" in html


def test_cli_devuelve_cero(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pipeline, "RAIZ", tmp_path)
    monkeypatch.setattr(pipeline.ejecutar, "__defaults__",
                        (True, DATA, tmp_path / "out", tmp_path / "site", False))
    assert pipeline.main(["--site", str(tmp_path / "site")]) == 0
    assert "Sitio generado" in capsys.readouterr().out
