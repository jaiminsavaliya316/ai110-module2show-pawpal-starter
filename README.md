# PawPal+

A Streamlit app that helps busy pet owners build a realistic daily care plan — sorted by priority and time, with automatic conflict detection.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Using the App](#using-the-app)
  - [Step 1: Set Owner](#step-1-set-owner)
  - [Step 2: Set Pet](#step-2-set-pet)
  - [Step 3: Add Tasks](#step-3-add-tasks)
  - [Step 4: Generate Schedule](#step-4-generate-schedule)
  - [Reading Your Plan](#reading-your-plan)
- [Scheduling Logic](#scheduling-logic)
- [Conflict Warnings](#conflict-warnings)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)

---

## Overview

PawPal+ takes a pet owner's available time and a list of care tasks, then produces an ordered daily plan that fits within the time budget. High-priority tasks are always scheduled first. Tasks with explicit times are sorted chronologically. If two tasks overlap on the clock, PawPal+ warns you before your day begins so you can adjust.

---

## Features

| Feature | Description |
|---|---|
| Owner + pet profiles | Set your name, daily time budget, pet name, and species |
| Task management | Add tasks with category, duration, priority, frequency, and optional scheduled time |
| Priority-first scheduling | High → medium → low; ties broken by time, duration, then name |
| Time-of-day sorting | Tasks with an `HH:MM` time are shown and scheduled in chronological order |
| Conflict detection | Overlapping timed tasks are flagged with a warning and a fix tip |
| Skipped task report | Tasks that don't fit the time budget are listed with the reason |
| Scheduling reasoning | Plain-language explanation of every scheduling decision |
| Recurring task support | `daily` and `weekly` tasks auto-generate their next due date on completion |

---

## Installation

**Requirements:** Python 3.10+

```bash
# 1. Clone or download the project
cd ai110-module2show-pawpal-starter

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the App

```bash
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

> **Note:** Do not run `python app.py` directly — Streamlit must serve the file or you will see `missing ScriptRunContext` warnings and no UI.

---

## Using the App

Work through the four steps in order. Each step unlocks the next.

### Step 1: Set Owner

| Field | Description |
|---|---|
| Owner name | Your name — used in plan summaries |
| Minutes available today | Total minutes you have for pet care (10–480) |

Click **Set Owner** to save. Changing the owner resets the pet and all tasks.

---

### Step 2: Set Pet

| Field | Description |
|---|---|
| Pet name | Your pet's name |
| Species | `dog`, `cat`, or `other` |

Click **Set Pet** to save. Changing the pet clears all tasks.

---

### Step 3: Add Tasks

| Field | Description |
|---|---|
| Task name | Short description, e.g. "Morning walk" |
| Category | `walk`, `feeding`, `meds`, `enrichment`, `grooming`, `other` |
| Duration (min) | How long the task takes in minutes |
| Priority | `high`, `medium`, or `low` |
| Frequency | `daily`, `twice_daily`, `weekly`, or `as_needed` |
| Scheduled time | Optional. Enter `HH:MM` (e.g. `08:30`) to pin the task to a specific time |
| Notes | Any extra context (optional) |

Click **Add Task** to save it. The task list below updates immediately, sorted by scheduled time (untimed tasks appear last).

**Frequency behaviour:**

| Frequency | Scheduling behaviour |
|---|---|
| `daily` | Scheduled every day |
| `twice_daily` | Counts as two slots; consumes `2 × duration` from the budget |
| `weekly` | Only scheduled on Mondays; skipped on all other days |
| `as_needed` | Scheduled when time allows, no fixed recurrence |

---

### Step 4: Generate Schedule

Click **Generate Schedule**. PawPal+ runs the scheduling algorithm and displays your plan immediately below.

---

### Reading Your Plan

**Metrics row** — time used, time available, and number of tasks scheduled.

**Free time banner** — green (`st.success`) if you have comfortable breathing room, amber (`st.warning`) if 15 minutes or fewer remain or time is fully used.

**Scheduled Tasks table** — tasks in their scheduled order, with priority icons (🔴 🟡 🟢) and status.

**Skipped Tasks table** — tasks that did not fit, with the reason (`insufficient time remaining` or `weekly task — not scheduled today`).

**Scheduling Reasoning** — expandable plain-text log explaining exactly why each task was included or excluded.

---

## Scheduling Logic

PawPal+ uses a **greedy priority-first algorithm**:

1. **Filter** — `weekly` tasks are removed on any day that is not Monday.
2. **Sort** — remaining tasks are ordered by:
   1. Priority rank (`high` → `medium` → `low`)
   2. Scheduled time (`HH:MM` ascending; untimed tasks last)
   3. Duration (shorter first — fits more tasks in the budget)
   4. Name (alphabetical tiebreaker for deterministic output)
3. **Pack** — tasks are added one by one. A task is scheduled if its duration fits in the remaining budget; otherwise it is skipped.
4. **Conflict check** — scheduled tasks with explicit times are scanned for overlapping windows.

---

## Conflict Warnings

A conflict occurs when two tasks with explicit `HH:MM` times have overlapping windows — i.e. the first task has not finished before the second begins.

When PawPal+ detects a conflict it:

1. Shows a **red error banner** at the top of your plan naming the number of conflicts.
2. Shows an **amber warning** for each conflicting pair, listing both task names, their times, and durations.
3. Includes a **fix tip** — adjust the scheduled time of one task or move the lower-priority task to a different slot.

Back-to-back tasks (e.g. one ends at `09:00` and the next starts at `09:00`) are **not** flagged — they are treated as valid sequential scheduling.

---

## Running Tests

```bash
python -m pytest tests/test_pawpal.py -v
```

The test suite covers 38 cases across sorting, recurrence, conflict detection, and core scheduling logic. All tests run in under 0.1 seconds.

---

## Project Structure

```
ai110-module2show-pawpal-starter/
├── app.py              # Streamlit UI
├── pawpal_system.py    # Core data model and scheduling logic
├── main.py             # CLI entry point (non-Streamlit usage)
├── uml.js              # Class diagram (Mermaid syntax, commented)
├── tests/
│   └── test_pawpal.py  # Pytest test suite
└── requirements.txt    # Python dependencies
```

---

## Key Classes (Quick Reference)

| Class | Role |
|---|---|
| `Owner` | Stores the owner's name and daily time budget |
| `Pet` | Stores pet info and owns the task list |
| `Task` | A single care activity with priority, duration, and optional time |
| `ScheduledTask` | Wraps a `Task` with its position in the day and completion status |
| `DailyPlan` | The output of the scheduler — scheduled tasks, skipped tasks, warnings, and reasoning |
| `Scheduler` | Generates a `DailyPlan` from an `Owner` and `Pet` |
