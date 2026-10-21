# Requirements: Office Hours Booking (OHB)

Status: M1 baseline v1.0 (21 Oct 2026). Changes after this date are recorded in git history and in the [correction log](REQUIREMENTS_CORRECTION_LOG.md).

## Definitions (used throughout)

| Term | Meaning |
|---|---|
| **Block** | A continuous period an instructor is available on one day, e.g. Tue 10:00–12:00. |
| **Slot** | One equal piece of a block that one student can book, e.g. 10:00–10:15. |
| **Slot length** `L` | The length of every slot in a block, in minutes. Allowed values: 10, 15, 20 or 30. |
| **Active booking** | A booking with status `active` whose slot has not yet started. |
| **now** | The current server time in UTC. Domain functions receive it as a parameter (see [ADR-004](adr/ADR-004-utc-storage-and-injected-clock.md)). |
| **Lead time** | Minutes between *now* and a slot's start. |
| **Interval** `[s, e)` | Half-open time interval: it includes start `s` and excludes end `e`. So 10:00–10:15 and 10:15–10:30 **do not** overlap. |
| **Riyadh time** | Asia/Riyadh, UTC+03:00, no daylight saving. |

**Rule constants** (one place, so tests and code use the same values):

| Constant | Value | Used by |
|---|---|---|
| `MIN_LEAD_MIN` | 60 minutes | FR-08 |
| `MAX_AHEAD_DAYS` | 14 days | FR-08 |
| `MAX_ACTIVE_PER_INSTRUCTOR` | 2 bookings | FR-10 |
| `CANCEL_CUTOFF_MIN` | 120 minutes | FR-12 |
| `ALLOWED_SLOT_LENGTHS` | {10, 15, 20, 30} minutes | FR-03, FR-04 |
| `BLOCK_MIN_MIN` / `BLOCK_MAX_MIN` | 30 / 240 minutes | FR-03 |
| `TOPIC_MAX_CHARS` | 200 characters | FR-07 |

---

## 1. Simulated personas

### P-01 Noura, student (primary persona)
- 3rd-year Software Engineering student, takes 5 courses.
- Visits office hours 1–2 times a week, more often before midterms.
- Pain: she waited 25 minutes outside an office last week, then the instructor had to leave.
- Goal: "I want to know my exact time before I walk across campus."
- Device: phone browser between classes, laptop at home.

### P-02 Dr. Faisal, instructor (secondary persona)
- Teaches 2 sections (about 80 students) and holds 4 hours of office hours a week.
- Pain: too many "are you free at 11?" emails, and the same 3 students take every free minute before exams.
- Goal: "Publish my hours once, see who is coming and what they want to ask."

## 2. User stories

| ID | Story | Persona | Requirements |
|---|---|---|---|
| US-01 | As a user, I want to log in with my email and password so that only I can see and change my bookings. | P-01, P-02 | FR-01, FR-02 |
| US-02 | As an instructor, I want to publish an office-hours block with a slot length so that students can book short, fixed times. | P-02 | FR-03, FR-04 |
| US-03 | As an instructor, I want to cancel a block so that students know when I'm unexpectedly unavailable. | P-02 | FR-05 |
| US-04 | As a student, I want to see an instructor's open slots so that I can pick a time that fits my classes. | P-01 | FR-06 |
| US-05 | As a student, I want to book a slot with a short topic so that the instructor can prepare. | P-01 | FR-07, FR-08, FR-09, FR-11 |
| US-06 | As the course coordinator (via the instructor), I want each student limited to a few active bookings per instructor so that access is fair. | P-02 | FR-10 |
| US-07 | As a student, I want to cancel my booking early enough so that someone else can use the slot. | P-01 | FR-12 |
| US-08 | As a student, I want one page with my upcoming and past bookings so that I don't forget them. | P-01 | FR-13 |
| US-09 | As an instructor, I want to see my schedule with student names and topics so that I can prepare. | P-02 | FR-14 |

## 3. Use cases

### UC-01 Book a slot
- **Actor:** Student. **Precondition:** logged in as a student.
- **Main flow:**
  1. The student opens *Open slots* and picks an instructor.
  2. The system lists open future slots inside the booking window (FR-06, FR-08).
  3. The student picks a slot, optionally types a topic, and presses *Book*.
  4. The system checks FR-08 to FR-11 and creates an active booking.
  5. The system shows a confirmation and the booking appears in *My bookings*.
- **Alternative/failure flows:**
  - 4a. The slot was taken in the meantime: show "This slot was just booked by someone else" and refresh the list (FR-09, NFR-01).
  - 4b. The student already has 2 active bookings with this instructor: show the limit message (FR-10).
  - 4c. The slot overlaps another of the student's bookings: show which booking clashes (FR-11).
  - 4d. The slot starts in less than 60 minutes or more than 14 days ahead: reject (FR-08).
- **Postcondition:** exactly one active booking exists for the slot.

### UC-02 Cancel my booking
- **Actor:** Student. **Main flow:** In *My bookings* the student presses *Cancel* on a booking. The system checks the cutoff (FR-12), sets the status to `cancelled_by_student`, and the slot becomes open again.
- **Failure:** less than 120 minutes before the start → reject with a message to contact the instructor.

### UC-03 Publish office hours
- **Actor:** Instructor. **Main flow:** The instructor enters the date, start time, end time, slot length and location. The system validates (FR-03), generates the slots (FR-04) and shows them in *My schedule*.
- **Failure:** invalid length, end before start, block in the past, or overlapping an existing block of the same instructor → reject with the reason.

### UC-04 Cancel a block
- **Actor:** Instructor. **Main flow:** The instructor presses *Cancel block*. All slots close and every active booking becomes `cancelled_by_instructor` (FR-05). Affected students see the status in *My bookings*.

### UC-05 Log in / log out
- **Actor:** Student or Instructor. **Main flow:** The user enters their email and password. The system verifies the password hash, starts a session and redirects by role (FR-01, FR-02).
- **Failure:** wrong email or password → show a generic "Invalid email or password" and create no session.

## 4. Scenarios (Given–When–Then)

Times are in Riyadh time unless stated. Each scenario becomes at least one automated test in M2. The planned test IDs are in [TRACEABILITY.md](TRACEABILITY.md).

| ID | Given | When | Then | Type |
|---|---|---|---|---|
| SC-01 | A block on 2026-11-03 from 10:00 to 11:00 with `L` = 15 | the instructor publishes it | 4 slots exist: 10:00, 10:15, 10:30, 10:45 | Happy path |
| SC-02 | A block from 10:00 to 10:50 with `L` = 15 | the instructor publishes it | 3 slots exist (10:00, 10:15, 10:30); the leftover 5 minutes are not a slot | Boundary |
| SC-03 | A block with `L` = 25 | the instructor publishes it | it is rejected with "slot length must be 10, 15, 20 or 30" | Failure |
| SC-04 | An open slot starting at 14:00, now = 12:59 | Noura books it | the booking is created (lead time 61 min ≥ 60) | Boundary |
| SC-05 | An open slot starting at 14:00, now = 13:01 | Noura books it | it is rejected (lead time 59 min < 60) | Boundary/failure |
| SC-06 | A slot exactly 14 days ahead vs 14 days + 1 minute ahead | Noura books each | the first succeeds, the second is rejected | Boundary |
| SC-07 | Noura already has 2 active future bookings with Dr. Faisal | she books a 3rd slot with Dr. Faisal | it is rejected with the limit message; booking with another instructor still works | Failure |
| SC-08 | Noura has a booking 10:00–10:15 with Dr. Faisal | she books 10:15–10:30 with Dr. Sara | it succeeds (touching intervals don't overlap) | Boundary |
| SC-09 | Noura has a booking 10:00–10:20 with Dr. Faisal | she books 10:15–10:30 with Dr. Sara | it is rejected and names the clashing booking | Failure |
| SC-10 | Two students submit a booking for the same open slot at the same moment | both requests are processed | exactly one gets the booking; the other sees "just booked by someone else" | Concurrency |
| SC-11 | Noura's booking starts at 14:00, now = 12:00 | she cancels | the cancellation succeeds (exactly 120 min) and the slot becomes open | Boundary |
| SC-12 | Noura's booking starts at 14:00, now = 12:01 | she cancels | it is rejected (119 min < 120) | Boundary/failure |
| SC-13 | Logged in as a student | the student sends `POST /blocks` | the response is 403 and nothing changes in the database | Security |
| SC-14 | A block with 2 active bookings | Dr. Faisal cancels the block | both bookings show `cancelled_by_instructor`; the slots are no longer listed | Happy path |
| SC-15 | A slot stored as 07:00 UTC | Noura views it | it shows as 10:00 Riyadh time | Time correctness |
| SC-16 | A wrong password for an existing email | the user logs in | "Invalid email or password"; no session cookie is set | Failure/security |

## 5. Requirements

### 5.1 Functional requirements

#### FR-01 Log in and out
Users log in with an email and password and can log out. Accounts are created by a seed script with synthetic data (NG-03). *Scenarios: SC-16.*

#### FR-02 Role-based access
Each user has exactly one role, `student` or `instructor`. Instructor-only actions (FR-03, FR-05, FR-14) are refused for students, and student-only actions (FR-07, FR-12, FR-13) are refused for instructors. *Scenarios: SC-13.*

#### FR-03 Publish a block
An instructor creates a block with a date, start, end, slot length `L` and location text. It is valid only if: `L` ∈ `ALLOWED_SLOT_LENGTHS`; the start is in the future; start and end are on the same day; the block length is between `BLOCK_MIN_MIN` and `BLOCK_MAX_MIN` minutes; and it doesn't overlap another non-cancelled block of the same instructor. *Scenarios: SC-01, SC-03.*

#### FR-04 Generate slots
When a block is published, the system creates `floor(block length ÷ L)` slots of length `L`, starting at the block start. Leftover minutes are discarded. *Scenarios: SC-01, SC-02.*

#### FR-05 Cancel a block
An instructor can cancel their own future block. All its slots stop being bookable, and all active bookings in it get status `cancelled_by_instructor`. *Scenarios: SC-14.*

#### FR-06 View open slots
A student can choose an instructor and see that instructor's slots that are not booked, not cancelled, and inside the booking window (FR-08), shown in Riyadh time. *Scenarios: SC-15.*

#### FR-07 Book a slot
A student can book one open slot with an optional topic of at most `TOPIC_MAX_CHARS` characters. The booking is created only if FR-08 to FR-11 all pass. *Scenarios: SC-04.*

#### FR-08 Booking window
A slot can be booked only if `MIN_LEAD_MIN` ≤ lead time and slot start ≤ now + `MAX_AHEAD_DAYS`. *Scenarios: SC-04, SC-05, SC-06.*

#### FR-09 One student per slot
A slot can have at most one active booking. *Scenarios: SC-10.*

#### FR-10 Per-instructor limit
A student can hold at most `MAX_ACTIVE_PER_INSTRUCTOR` active bookings with the same instructor. *Scenarios: SC-07.*

#### FR-11 No overlapping bookings
A student can't hold two active bookings whose intervals `[start, end)` overlap, even with different instructors. *Scenarios: SC-08, SC-09.*

#### FR-12 Student cancels a booking
A student can cancel their own active booking only if the lead time is ≥ `CANCEL_CUTOFF_MIN`. The slot then becomes open again. *Scenarios: SC-11, SC-12.*

#### FR-13 My bookings
A student sees their upcoming and past bookings with instructor, time (Riyadh), location, topic and status. *Scenarios: SC-14.*

#### FR-14 Instructor schedule
An instructor sees their future blocks, each slot's state (open/booked/cancelled), and the booked student's name and topic. *Scenarios: SC-14.*

### 5.2 Non-functional requirements (quality-attribute scenarios)

Each NFR uses the six parts of a quality-attribute scenario: **source → stimulus → artifact → environment → response → response measure**.

#### NFR-01 Booking integrity under concurrency
| Part | Value |
|---|---|
| Source | Two or more students |
| Stimulus | Submit `POST /bookings` for the same open slot at the same time |
| Artifact | Booking service + database |
| Environment | Normal operation, single app instance |
| Response | Exactly one booking is created; the others get a "slot already booked" message |
| Measure | **0 slots with more than one active booking** after 100 runs of a 10-thread race test; integrity query `SELECT slot_id FROM bookings WHERE status='active' GROUP BY slot_id HAVING COUNT(*)>1` returns 0 rows |

#### NFR-02 Access control
| Part | Value |
|---|---|
| Source | A logged-in student, or an anonymous user |
| Stimulus | Calls an instructor-only endpoint, or another user's booking |
| Artifact | Web layer authorisation checks |
| Environment | Normal operation |
| Response | Request refused, no data changed |
| Measure | **100%** of instructor-only endpoints return 403 for a student session, and 303 to login for anonymous users, in the automated access-matrix test; 0 database rows changed |

#### NFR-03 Credential and secret protection
| Part | Value |
|---|---|
| Source | An attacker who gets a copy of the database or the repository |
| Stimulus | Reads the `users` table or the git history |
| Artifact | Password storage, repository |
| Environment | Development and production |
| Response | No plaintext passwords or live secrets are found |
| Measure | All passwords stored as **bcrypt hashes (cost ≥ 12)**; secret scanner (gitleaks) reports **0 findings** on the full history in CI; session cookie has `HttpOnly`, `Secure` and `SameSite=Lax` set |

#### NFR-04 Performance of the slot list
| Part | Value |
|---|---|
| Source | 20 students at the same time |
| Stimulus | Open *Open slots* for an instructor (`GET /slots`) |
| Artifact | Web app + SQLite |
| Environment | Render Starter instance (0.5 CPU, 512 MB), seeded with 20 instructors × 14 days of slots |
| Response | Page returned |
| Measure | **p95 latency < 300 ms** over a 60-second load test (Locust); error rate 0% |

#### NFR-05 Testability of booking rules
| Part | Value |
|---|---|
| Source | Developer or instructor |
| Stimulus | Changes a booking rule, or introduces a mutation |
| Artifact | `app/domain` module (pure functions) |
| Environment | CI, before merge |
| Response | Tests detect the change |
| Measure | **≥ 90% branch coverage** (coverage.py) and **mutation score ≥ 80%** (mutmut) on `app/domain` |

#### NFR-06 Recoverability
| Part | Value |
|---|---|
| Source | Operator mistake or a corrupted deploy |
| Stimulus | The database file is lost or corrupted |
| Artifact | SQLite file on the Render disk |
| Environment | Production |
| Response | Restore from the latest daily disk snapshot following the runbook |
| Measure | **Data loss ≤ 24 hours** (snapshot age); **restore completed in ≤ 15 minutes** in a timed drill |

#### NFR-07 Time correctness
| Part | Value |
|---|---|
| Source | Any user |
| Stimulus | Creates or views a slot |
| Artifact | Storage and display layers |
| Environment | Server running in UTC |
| Response | Times stored in UTC and displayed in Riyadh time |
| Measure | **100% of timestamp columns are UTC**; SC-15 passes; the domain tests use an injected clock, not the system clock (0 calls to `datetime.now()` inside `app/domain`, checked by a grep test) |

#### NFR-08 Usability of booking
| Part | Value |
|---|---|
| Source | A student new to the app |
| Stimulus | Wants to book a slot |
| Artifact | UI |
| Environment | Phone browser, 375 px wide |
| Response | Completes the booking |
| Measure | **≤ 3 interactions after login** (pick instructor → pick slot → confirm), checked by a scripted Playwright test; no horizontal scrolling at 375 px |

## 6. Scope inventory

**Screens (4 of 6):** S1 Login · S2 Open slots (pick instructor + book) · S3 My bookings (student) · S4 My schedule (instructor: blocks, slots, create/cancel block).

**Endpoints (10 of 10):**

| # | Method and path | Role | Requirements |
|---|---|---|---|
| E1 | `GET /login` | anyone | FR-01 |
| E2 | `POST /login` | anyone | FR-01 |
| E3 | `POST /logout` | logged in | FR-01 |
| E4 | `GET /slots?instructor_id=` | student | FR-06, FR-08 |
| E5 | `POST /bookings` | student | FR-07 to FR-11 |
| E6 | `POST /bookings/{id}/cancel` | student | FR-12 |
| E7 | `GET /me/bookings` | student | FR-13 |
| E8 | `GET /schedule` | instructor | FR-14 |
| E9 | `POST /blocks` | instructor | FR-03, FR-04 |
| E10 | `POST /blocks/{id}/cancel` | instructor | FR-05 |

Render's health check uses `GET /login`, so there is no extra endpoint.

**Tables (4 of 8):** `users`, `blocks`, `slots`, `bookings`.

**Roles (2 of 2):** student, instructor.
