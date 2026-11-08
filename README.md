# Admit Compass (team noble-shape, MGT 656)

Staging: https://noble-shape-staging.onrender.com (free plan; first request after idle takes ~1 min)

Build a college shortlist from federal College Scorecard data, then ask
questions about it. Django + PostgreSQL, deployed on Render with a Neon
database.

## Run it locally (3 steps)

```sh
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env && python manage.py migrate && python manage.py runserver
```

Open http://127.0.0.1:8000/ . With `DEBUG=True` and no `DATABASE_URL`, the app
uses a local SQLite file. To use Postgres, set `DATABASE_URL` in `.env`.

Before opening a PR, run what CI runs:

```sh
ruff check . && python manage.py test
```

## Who owns what

| Folder | Owner | What goes there |
| --- | --- | --- |
| `config/`, `requirements*.txt`, `build.sh`, `render.yaml`, `.github/` | A | settings, dependencies, deploy, CI |
| `accounts/`, `templates/`, `static/` | B | sign up / log in / log out, base layout |
| `abtest/` | C | `/fd986fa` A/B page and `/fd986fa/stats` |
| `core/` | D | models, `seed` management command |
| `docs/` | E | `docs/mgt656/` reports, backlog notes |

All three apps are already in `INSTALLED_APPS` and their `urls.py` files are
already included from `config/urls.py`, so you only edit files inside your own
app. Need a new dependency or setting? Open a PR and ask A to review.

Rules: work on a branch, PR says `Closes #<issue>`, a teammate reviews before
merge, each app makes its own migrations.

Deployment: see [DEPLOY.md](DEPLOY.md).
