# Vista Flare feature audit — October 2026

## Fully implemented and verified

- Existing ANN/MLP prediction pipeline, persisted encoders/scaler, fallback
  inference, skill-gap analysis, seed catalog, jobs, companies, resources, and
  Deep Learning Lab artifacts.
- Cookie-session authentication, CSRF checks, password hashing, protected
  user-owned roadmap/saved-job/application/practice records, and cross-user
  isolation tests.
- URL routing, protected-route redirects, comparison query state, 404 view,
  guest local-data import action, and browser-local guest journey support.
- External job normalization, deduplication, upserts, stale policy, provider
  diagnostics, persisted observations, change events, in-app notification
  records, alert preference APIs, and timestamped market-trend APIs.
- Ephemeral resume-text matching, upload validation, deterministic role coach,
  and private interview-practice progress APIs.
- Backend test suite, frontend component/integration tests, CI workflow,
  frontend production build, TypeScript compilation, and lint execution.

## Implemented but incomplete

- Roadmap records are server-persisted, but task statuses/notes/completion
  timestamps are still primarily handled by the browser-local progress widget.
- Profile import persists a bounded guest journey payload in a normalized
  profile table, but profile skills/preferences do not yet have dedicated
  relational child tables.
- Provider ingestion currently has a production-tested Arbeitnow adapter and a
  seed provider. Adzuna and Remotive are listed in the example configuration
  but do not have active adapters in the repository.
- Notifications, alert preferences, provider status, and market trends have
  backend APIs but are not yet integrated into dedicated frontend views.
- Resume matching supports plain text immediately; PDF/DOCX extraction remains
  explicitly unavailable until `pypdf` or `python-docx` is installed.
- Interview/portfolio coach APIs exist, but there is no complete frontend
  preparation workspace yet.

## Implemented but operationally limited

- The optional in-process scheduler is suitable only for a single API process.
  It must not run across multiple production workers.
- SQLite remains appropriate for controlled single-instance use, not a
  horizontally scaled deployment.
- Authentication has no built-in login rate limiting, email verification, or
  password-reset flow. Use an authenticated reverse proxy/API gateway before
  public exposure.

## Blocked or awaiting configuration

- TensorFlow ANN loading remains environment-dependent; the current runtime may
  report and use the existing scikit-learn fallback.
- External provider freshness depends on network availability and provider
  response behavior. No live provider call is treated as successful in tests.
- Local Playwright execution requires a one-time Chromium install:
  `npx playwright install chromium`.

## Intentional non-claims

The system does not claim instantaneous global job-market coverage, guaranteed
employment outcomes, live company-wide hiring status, or successful email
delivery. Seed, cached, external, stale, and unavailable records remain
distinct in the backend provenance model.
