# ADR-001: Use a server-rendered modular monolith (Option A)

- **Status:** Accepted
- **Date:** 2026-10-21
- **Deciders:** Tariq Algadheeb, Abdullah
- **Supersedes:** none
- **Related requirements:** FR-06, FR-07, FR-13, FR-14, NFR-04, NFR-05, NFR-08
- **Trade-off matrix rows:** T1, T2, T8, T9

## Context
We are two students with about 6 weeks to build, test and defend the app. M2 (25–29 Oct) needs a working end-to-end slice and a mutation-tested module. Both of us are stronger in Python than in JavaScript frameworks, and each of us must be able to explain and debug every line with AI turned off. We considered two architectures (see [ARCHITECTURE_OPTIONS.md](../architecture/ARCHITECTURE_OPTIONS.md)).

## Decision
Build **one FastAPI application that renders HTML with Jinja2** (Option A), layered as `web → services → domain` and `services → repositories`. All booking rules go in a pure `app/domain` package.

## Rejected alternative
**Option B: React SPA + JSON REST API + PostgreSQL.** Rejected because:
- It adds a second language (TypeScript), a build pipeline and a second deployable unit. That roughly doubles the code each of us must be able to defend (trade-off row T1).
- JWT handling and CORS add security work that doesn't serve any of our requirements (row T9).
- Its main benefit, an API that a future mobile app could reuse, is an explicit non-goal (NG-07).

## Accepted downside
- **Less interactive UI:** every action is a full page reload, and the slot list doesn't update live. A student may try to book a slot that was just taken. We handle this with a clear message (UC-01 flow 4a) instead of live updates.
- **No reusable JSON API:** if a mobile app is ever needed, we would have to add JSON endpoints, or supersede this ADR.

## Consequences
- One process, one language, one deployable unit. That makes NFR-05 (testability) easier, because the domain layer is tested with plain pytest and no HTTP.
- The FastAPI OpenAPI page documents the 10 endpoints for the M4 API documentation.
