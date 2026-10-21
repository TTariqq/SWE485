# ADR-002: Store data in SQLite on a Render persistent disk

- **Status:** Accepted
- **Date:** 2026-10-21
- **Deciders:** Tariq Algadheeb, Abdullah
- **Supersedes:** none
- **Related requirements:** NFR-01, NFR-04, NFR-06, FR-09
- **Trade-off matrix rows:** T3, T6, T7

## Context
The app has 4 tables and a small pilot load: about 3,000 sessions per month (see [COST_MODEL.md](../COST_MODEL.md)). We need persistence that is cheap, simple to run locally and in tests, and safe for concurrent bookings (NFR-01). Render's free web instances can't attach a disk, and Render's free Postgres expires after 30 days.

## Decision
Use **SQLite** (accessed through SQLAlchemy) stored on a **1 GB Render persistent disk** attached to one Starter web service. Recovery relies on Render's **automatic daily disk snapshots** (kept for at least 7 days) plus a documented restore runbook (NFR-06).

## Rejected alternative
**Render Postgres Basic-256mb (managed PostgreSQL).** Rejected because:
- It costs more per month ($6 instance + $0.30/GB storage, versus $0.25 for a 1 GB disk; row T7).
- It needs a separate server for local development and tests, or a Docker setup that both members must maintain.
- Its strengths, many concurrent writers and multiple app instances, aren't needed at pilot scale.

## Accepted downside
- **Single instance only:** a Render disk can attach to only one instance, so the app **cannot scale horizontally**.
- **No zero-downtime deploys:** Render stops the old instance before starting the new one, so each deploy causes a few seconds of downtime.
- **Single writer:** SQLite allows one writer at a time. Bookings are serialised, which is fine at the pilot load but limits throughput.
- **Up to 24 hours of data loss** if we have to restore from a daily snapshot (NFR-06 measure).

## Consequences
- Tests use an in-memory or temporary-file SQLite database. No external services are needed in CI.
- If NFR-04 fails at scale, or a second instance is needed, write a new ADR that supersedes this one and migrate to Postgres. SQLAlchemy keeps that migration contained in the repositories.
