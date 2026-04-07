# DEV_AGENT_PROMPT — newpush-labs-template-server

> Minimal **Python Flask** template server with **Gunicorn** for Procfile-based deployment (Heroku, Railway, Render). Three files total — simplicity is the point.

---

## 1. Orientation — Read the Docs

Before touching any file, read and internalise:

| Document | Why |
|----------|-----|
| `app.py` | **Entire application** — Flask routes and logic |
| `requirements.txt` | Python dependencies |
| `Procfile` | Process definition for platform deployment |
| `README.md` | Project purpose |

### Tech Stack

- **Python 3** with **Flask**
- **Gunicorn** WSGI server (production)
- **Procfile** deployment (Heroku-compatible platforms)

### Key Patterns

- This is a **template** repo — it exists to be cloned and extended
- `app.py` is the single entry point — keep it minimal and well-commented
- `Procfile` format: `web: gunicorn app:app`
- `requirements.txt` pins dependencies — keep it up to date
- No tests, no CI, no build step — intentionally minimal
- Any additions should serve the "template" purpose (easily removable scaffolding)

---

## 2. Plan — Write a Plan

Before writing code, create a plan in `docs/IMPLEMENTATION_PLAN.md`:

1. **What** — the enhancement or fix
2. **Template impact** — does this change make the template less generic?
3. **Dependency impact** — any new entries in `requirements.txt`?
4. **Deployment test** — verify Procfile still works on target platform

Keep the template nature in mind — additions should be **exemplary scaffolding** that users can easily understand and modify.

---

## 3. Documentation — Write User Docs First

- `README.md` — update with any new routes, environment variables, or setup steps
- Inline comments in `app.py` — this is a template, so every pattern needs explanation
- If adding configuration, document environment variables clearly

---

## 4. Tests — Write Tests First

Even for a template, basic verification matters:

```python
# tests/test_app.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get('/')
    assert rv.status_code == 200
```

- Add `pytest` to `requirements.txt` if adding tests
- Test every route defined in `app.py`
- Verify `gunicorn app:app` starts without error

---

## 5. Code — Write the Code

### Flask Rules

- Keep `app.py` as the single application file unless complexity demands splitting
- Use Flask factory pattern (`create_app()`) if adding configuration
- Environment variables via `os.environ.get()` with sensible defaults
- JSON responses for API endpoints: `return jsonify({...})`
- Health check endpoint at `/` or `/health` — always present

### Dependency Rules

- Pin exact versions in `requirements.txt` (e.g., `flask==3.0.0`)
- Minimal dependencies — this is a template, not a framework
- `gunicorn` must always be present for Procfile deployment

### Template Rules

- Every file should be self-explanatory to a developer cloning this repo
- Avoid framework-specific magic — keep patterns explicit
- Include comments explaining "why" not just "what"

---

## 6. Test the Code — Verify Everything

```bash
pip install -r requirements.txt
python app.py                      # Dev server starts
gunicorn app:app                   # Production server starts
pytest tests/ -v                   # If tests exist
```

- Verify all routes return expected status codes
- Check Procfile deployment on target platform

---

## Branch Workflow

```
feature/* ──► develop ──► main
```

- All work on `feature/*` branches off `develop`
- PR to `develop` for review
- `develop` → `main` via PR only (enforced by CI)
