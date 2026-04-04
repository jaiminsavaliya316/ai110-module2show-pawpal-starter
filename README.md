# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler has been extended beyond basic priority-and-time-budget packing with four new features:

**Time-of-day sorting** — `Task` objects now accept an optional `scheduled_time` field (`"HH:MM"`). `Scheduler.sort_by_time()` uses a lambda key to sort tasks as strings, which works correctly for zero-padded times (e.g. `"08:00" < "09:30"`). Tasks with no time are placed last using the sentinel `"99:99"`. Within the full scheduling pipeline, `_sort_tasks()` uses time as a secondary key after priority, so high-priority tasks still come first but are ordered chronologically among equals.

**Filtering by pet and status** — `filter_plans(plans, pet_name=..., status=...)` queries across multiple `DailyPlan` objects and returns a flat list of matching `ScheduledTask` entries. Both filters are optional and can be combined (e.g. all completed tasks for a specific pet).

**Recurring task auto-scheduling** — `ScheduledTask.mark_complete(completed_on=...)` now returns a new `Task` instance for the next occurrence instead of just setting the status. `daily` tasks get a `due_date` of `completed_on + timedelta(days=1)`; `weekly` tasks get `+ timedelta(weeks=1)`. `twice_daily` and `as_needed` tasks return `None` since they don't have a fixed recurrence interval. The `twice_daily` frequency also now correctly produces two `ScheduledTask` entries and consumes `2 × duration` from the time budget.

**Lightweight conflict detection** — `detect_conflicts(scheduled_tasks)` compares every pair of timed tasks using half-open interval math (`[start, start+duration)`) and returns a list of conflicting pairs without raising. `Scheduler.check_conflicts()` wraps this into plain-text warning strings that are stored on `DailyPlan.warnings` and printed at runtime — the program never crashes on a scheduling conflict.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
