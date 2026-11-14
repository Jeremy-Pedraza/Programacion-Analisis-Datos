# Guía de contribución y flujo de trabajo

## Modelo de ramas (GitFlow simplificado)

| Rama | Propósito | Se crea desde | Se fusiona en |
|---|---|---|---|
| `main` | Código en producción; cada commit se despliega | — | — |
| `develop` | Integración de funcionalidades terminadas | `main` | `main` (vía `release/*`) |
| `feature/<tema>` | Una funcionalidad | `develop` | `develop` |
| `fix/<tema>` | Corrección | `develop` | `develop` |
| `release/vX.Y.Z` | Estabilización de una versión | `develop` | `main` y `develop` |

## Ciclo de una funcionalidad

```bash
git switch develop && git pull
git switch -c feature/mi-cambio
# ... código + pruebas ...
pytest && ruff check .
git add -A && git commit -m "feat(competencia): soporte de paginación"
git push -u origin feature/mi-cambio
# Abrir Pull Request feature/mi-cambio → develop en GitHub
```

El PR se fusiona con **Create a merge commit** (`--no-ff`) para conservar la historia de la rama,
y solo cuando el workflow **CI** está en verde.

## Mensajes de commit (Conventional Commits)

`<tipo>(<alcance>): <descripción en imperativo>`

Tipos: `feat`, `fix`, `test`, `docs`, `ci`, `refactor`, `chore`.
Ejemplos: `feat(producto): extraer tabla de especificaciones`, `ci: añadir matriz de Python`.

## Protección de ramas (Settings → Branches)

Para `main` y `develop`:

- Require a pull request before merging.
- Require status checks to pass: `Lint (ruff)`, `Pruebas (Python 3.10/3.11/3.12)`, `Araña Scrapy`.
- Do not allow bypassing the above settings.

## Versionado

Semántico (`MAJOR.MINOR.PATCH`). Cada release se etiqueta (`git tag -a v1.0.0`) y se registra en
`CHANGELOG.md`.
