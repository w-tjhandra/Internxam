# Backend development

Run commands from this directory so the backend package and local `.env` resolve consistently.

## Layout

- `app/main.py` creates the FastAPI application and registers routers.
- `app/routers/` owns HTTP handlers grouped by auth, admin, results, and exam domains.
- `app/runtime.py` provides shared database state, cross-domain dependencies, and export helpers.
- `app/services/exam_workflow.py` owns exam-session lifecycle, scoring coordination, and state construction.
- `app/services/scenario_assessment.py` contains isolated scenario scoring logic.
- `app/db/` owns schema setup, seeding, and database lifecycle.

## Start the API

```bash
uvicorn app.main:app --reload
```

Deployments using the legacy `server:app` import remain supported:

```bash
uvicorn server:app
```

Set `DB_DSN`, `JWT_SECRET`, and other environment-specific settings in `backend/.env`.
Do not commit that file or use production credentials for local development.

## Tests

Install the dependencies from `requirements.txt`, then run isolated unit tests:

```bash
python -m pip install -r requirements.txt
python -m pytest tests/unit
```

API integration tests are skipped by default. They require an explicitly configured API
and may create or update records, so opt in only against a disposable test environment:

```bash
RUN_API_INTEGRATION_TESTS=1 REACT_APP_BACKEND_URL=http://127.0.0.1:8000 \
  python -m pytest tests/integration/test_api.py
```
