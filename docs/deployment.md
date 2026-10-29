# Vista Flare deployment and operations

## Current deployment shape

Vista Flare can run as a single FastAPI process serving the API and a built
Vite frontend behind a reverse proxy. SQLite remains supported for a
single-instance deployment. It should not be used for multiple concurrent API
workers without a deliberate database migration and backup strategy.

## Configuration and production validation

Copy `.env.example` to `.env` and set a high-entropy `SECRET_KEY`. In a
production environment set `APP_ENV=production`, `DEBUG=false`,
`SECURE_COOKIES=true`, and a non-empty `INGESTION_ADMIN_SECRET`. Keep `.env`
outside source control.

The frontend uses the `/api` same-origin path. Serve the Vite `frontend/dist`
directory through the same origin or configure a reverse proxy that forwards
`/api` and `/reports` to FastAPI and falls back to `index.html` for client-side
routes.

Before starting a production process, fail the deployment if any of these are
true: `APP_ENV` is not `production`, `DEBUG=true`, `SECURE_COOKIES` is not
`true`, `SECRET_KEY` is empty or still contains the example value, or
`INGESTION_ADMIN_SECRET` is empty. A deployment check can be performed without
logging secret values:

```powershell
$required = 'APP_ENV','SECRET_KEY','INGESTION_ADMIN_SECRET'
foreach ($name in $required) { if (-not [Environment]::GetEnvironmentVariable($name)) { throw "$name is required" } }
if ($env:APP_ENV -ne 'production' -or $env:DEBUG -eq 'true' -or $env:SECURE_COOKIES -ne 'true') { throw 'Unsafe production flags' }
if ($env:SECRET_KEY -eq 'your-secret-key-here-change-in-production') { throw 'Example SECRET_KEY is not allowed' }
```

Keep secrets in the process manager/secret store and rotate them through a
planned session invalidation window. Never commit `.env`, cookies, or admin
headers to logs or CI artifacts.

## Commands

```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

```powershell
Set-Location frontend
npm run build
npx playwright install chromium   # one-time per developer/runner
npm run e2e
```

The Playwright smoke test uses the built frontend preview and does not require
live API services. CI installs Chromium explicitly; a fresh local checkout
must run the one-time browser install command before `npm run e2e`.

Run the protected ingestion maintenance call only from an authorized
maintenance environment:

```powershell
curl -X POST http://localhost:8000/api/admin/jobs/ingest `
  -H "X-Ingestion-Secret: <configured-secret>"
```

The endpoint is not a public frontend action. Provider failures preserve prior
records; external rows expose source and freshness metadata, while seed rows
remain distinguishable.

For a controlled single-instance refresh loop, set
`ENABLE_INGESTION_SCHEDULER=true` and configure
`INGESTION_INTERVAL_MINUTES`. Leave it disabled when an external scheduler or
maintenance process owns refreshes. The process contains one guarded loop and
must not be started with multiple production workers.

## Database backup and recovery

Stop the API before copying the SQLite file, or use SQLite's online backup
command. Keep dated copies of `data/vista_flare.db` before schema changes:

```powershell
Copy-Item data/vista_flare.db backups/vista_flare-$(Get-Date -Format yyyyMMdd-HHmmss).db
```

Startup schema changes are additive. Restore the latest verified backup if a
deployment must be rolled back. Do not delete or recreate the database to
recover from an application error.

## Health and limitations

- `/health` reports application reachability.
- `/api/health` reports database and model state, including TensorFlow versus
  scikit-learn fallback inference.
- Use `/health` for a lightweight load-balancer liveness probe and `/api/health`
  for readiness. A readiness check should require an HTTP 200 response,
  `database: "ok"`, and an expected `model_loaded`/`model_type` state. After
  ingestion, verify the returned job `last_seen_at`/`stale` metadata and alert
  when the newest provider data exceeds `INGESTION_STALE_AFTER_HOURS`.
- Authentication uses an HTTP-only session cookie and a separate CSRF cookie
  for browser mutations.
- SQLite, in-process ingestion locking, and the current maintenance-secret
  trigger are suitable for a controlled single-instance deployment, not a
  horizontally scaled production fleet.
- The application does not currently enforce request rate limits. Put an
  authenticated reverse-proxy/API gateway in front of it before public
  exposure, with separate limits for login/register, prediction, catalog
  reads, and the ingestion endpoint; return 429 and monitor rejected requests.
- Email verification, password reset, centralized logging, and a managed
  database remain recommended before public internet exposure.

### Operational check examples

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

Run both checks after deploy and after model/data refresh. Treat a failed
readiness check or stale job feed as an incident, while keeping the liveness
probe independent so the orchestrator can distinguish an unhealthy process
from a temporarily unavailable dependency.
