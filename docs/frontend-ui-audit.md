# Vista Flare frontend UI audit and refinement

## Baseline

- Existing React/Vite frontend uses Tailwind utilities, local CSS, React Router,
  Recharts, and Lucide icons.
- The main shell previously mixed a dense single-row navigation with separate
  layouts for workspace/auth/detail routes.
- Most feature pages had useful API integrations but inconsistent page headers,
  cards, form labels, tab semantics, provenance copy, and mobile behavior.
- Existing automated checks were already available through Vitest/Testing
  Library; Playwright is configured but requires a local Chromium install.

## Refinement direction

Vista Flare now uses a restrained, corporate-premium SaaS language: slate ink,
soft canvas backgrounds, white panels, blue/indigo action accents, compact
status pills, modest radius, low-elevation borders, and purposeful motion.
Model status, data provenance, stale state, and unavailable data use explicit
text rather than color-only or decorative live indicators.

## Implemented focus

1. Consolidate all route types under one accessible shell.
2. Group navigation into Explore, Plan, and Learn without adding unsupported
   destinations.
3. Add consistent banners, status pills, focus states, responsive containers,
   mobile navigation behavior, reduced-motion handling, and touch targets.
4. Improve page hierarchy, labels, tab semantics, empty/error/loading states,
   provenance language, model-score wording, and responsive feature layouts.
5. Preserve existing API clients, route behavior, persistence, model status,
   and backend contracts.

## Remaining UI limitations

- Role and job deep-link screens still use the existing lightweight detail
  placeholder rather than full live detail panels.
- Notifications, market trends, resume analysis, and interview APIs do not yet
  have dedicated frontend screens.
- The frontend still has seven non-blocking ESLint warnings in existing hook
  dependency/Fast Refresh patterns.
- Full visual browser verification requires installing Chromium for Playwright;
  the deterministic component/integration suite remains runnable locally.
