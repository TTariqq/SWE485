# Project Charter: Office Hours Booking (OHB)

| Field | Value |
|---|---|
| Course | SWE485 |
| Project type | App (web application) |
| Milestone | M1 Requirements and architecture (due 21 Oct 2026) |
| Declared primary language | **Python 3.12** (see [RULES.md](../RULES.md)) |
| Approved AI tool | DEVAI (see [AI_USE_DISCLOSURE.md](../AI_USE_DISCLOSURE.md)) |
| Data | Synthetic only (fake names, `@example.edu` emails). No real KSU data. |

## 1. Team members

| Member | Role in team | Primary areas (owner) |
|---|---|---|
| Tariq Algadheeb | Developer, requirements lead | Booking rules (domain), booking service, tests for booking |
| Abdullah | Developer, architecture lead | Auth and access control, instructor schedule, deployment, backup |

Both members review each other's pull requests. The member who reads each AI-generated file is named in the disclosure log.

## 2. Stakeholder problem

Instructors hold weekly office hours, but students don't know whether the instructor is free or busy with another student. Students also queue outside the office or send emails asking "are you available at 11?". The result:

- Students waste time waiting, or give up and don't get help.
- Instructors get repeated scheduling emails and can't prepare for the questions in advance.
- Popular instructors before exams get crowded, and a few students take most of the time.

**Stakeholders**
- **Students** (primary): want a guaranteed short slot with a known start time.
- **Instructors** (primary): want to publish their availability once and see who is coming and why.
- **Course coordinator** (secondary, not a system user): wants fair access, meaning no student hoards slots.

## 3. Product scope (in scope)

1. Login for two roles: **Student** and **Instructor** (accounts are seeded with synthetic data).
2. An instructor publishes an office-hours **block** (for example, Tue 10:00–12:00), and the system splits it into equal **slots** (for example, 15 minutes each).
3. A student views open slots for an instructor and books one, with an optional topic.
4. Booking rules: booking window, one student per slot, a per-instructor booking limit, no overlapping bookings, and a cancellation cutoff.
5. A student sees and cancels their own bookings. An instructor sees their schedule and can cancel a whole block.
6. Deployment to one target (Render), with daily disk snapshots.

**Scope caps check (from the brief):**

| Cap | Limit | Planned |
|---|---|---|
| Screens/views | 6 | 4 |
| API endpoints | 10 | 10 |
| Tables | 8 | 4 |
| User roles | 2 | 2 |
| Deployment targets | 1 | 1 |

Screens, endpoints and tables are listed in [REQUIREMENTS.md §6](REQUIREMENTS.md#6-scope-inventory).

## 4. Explicit non-goals

The product will **not** do the following:

- **NG-01** Email, SMS or push notifications.
- **NG-02** Sync with Google Calendar, Outlook or KSU systems, or use single sign-on (SSO).
- **NG-03** Provide an admin role or admin UI. Accounts are created by a seed script.
- **NG-04** Video meetings. The instructor may type an online link as plain text.
- **NG-05** Recurring weekly blocks. Each block is created on its own.
- **NG-06** Waitlists, or automatically moving students when a slot frees up.
- **NG-07** A mobile app, or a public API for third parties.
- **NG-08** Arabic localisation. The UI is in English only.
- **NG-09** Attendance or no-show tracking.
- **NG-10** Any AI feature inside the product. AI is used only for development, through DEVAI.

## 5. Success criteria (for the course)

- An end-to-end booking path works by M2: log in → view slots → book → see the booking.
- The booking-rules module has ≥ 90% branch coverage and a mutation score of ≥ 80% (NFR-05).
- Every requirement traces to architecture, an ADR or scenario, and a planned test ([TRACEABILITY.md](TRACEABILITY.md)).
