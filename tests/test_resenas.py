from ml_scraper.resenas import extraer_resenas, html_con_selenium


def test_extrae_resenas_del_dom(html_producto):
    resenas = extraer_resenas(html_producto)
    assert len(resenas) >= 3
    assert all(1 <= r["estrellas"] <= 5 for r in resenas)
    assert all(r["comentario"] for r in resenas)


def test_sin_resenas_devuelve_lista_vacia():
    assert extraer_resenas("<html><body></body></html>") == []


def test_selenium_con_respaldo_al_snapshot(tmp_path, monkeypatch):
    """Sin navegador disponible (caso del runner de CI) se usa el snapshot."""
    import builtins

    snap = tmp_path / "p.html"
    snap.write_text("<html>snap</html>", encoding="utf-8")
    import_original = builtins.__import__

    def sin_selenium(nombre, *args, **kwargs):
        if nombre.startswith("selenium"):
            raise ImportError("selenium no instalado")
        return import_original(nombre, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", sin_selenium)
    html, motor = html_con_selenium("https://ejemplo", snap, offline=True)
    assert html == "<html>snap</html>"
    assert motor == "snapshot (fallback)"
