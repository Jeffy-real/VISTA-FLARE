# Vista Flare implementation plan

## Audit snapshot

Vista Flare is a React/Vite frontend over a FastAPI/SQLAlchemy backend. The
backend uses the persisted 373-feature skill encoder, 85-class label mapping,
scaler, and ANN artifact for career classification, with a local scikit-learn
fallback when TensorFlow cannot load. SQLite currently contains reference
catalog data (roles, skills, role-skill mappings, jobs, companies, and learning
resources), but no user-owned records. The primary flow already exists:

`skills -> top 3 roles -> skill gap -> roadmap/resources -> jobs/companies`.

## Baseline checks

- `python -m pytest backend/tests -v`: 16 passed, 1 failed because the current
  environment cannot import the TensorFlow ANN and the API honestly reports the
  scikit-learn fallback.
- `npm run build` from `frontend`: passed; Vite reports a large-bundle warning.
- `npm run lint` from `frontend`: unavailable because ESLint 9 has no flat config.

## Focused implementation slice

1. Make model availability explicit without changing preprocessing, class
   ordering, or model artifacts. Surface fallback/degraded status and preserve
   a truthful model label.
2. Make skill-gap analysis reject unknown roles, calculate the selected role's
   model score directly, normalize resource matching, and remove artificial
   company-fit floors.
3. Repair broken frontend actions and make API failures visible with retry
   controls, accessible labels, and semantic score indicators.
4. Persist the current skill profile, selected role, recommendations, and
   roadmap stage completion in browser storage. This is intentionally local
   persistence because the existing application has no authentication or
   user-owned database tables; it does not pretend to be multi-user storage.
5. Keep the existing SQLite catalog, model artifacts, APIs, and three-model
   evaluation lab intact.

## Risks and validation

- TensorFlow compatibility remains an environment/dependency issue; no model is
  retrained or replaced to mask it.
- Existing uncommitted `.claude/settings.json` and generated build-info
  deletions are unrelated and will not be touched.
- Validate with backend tests, frontend production build, and a direct API smoke
  check for prediction, invalid-role analysis, and degraded health reporting.
