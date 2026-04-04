from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date as Date, timedelta
from typing import Literal


# ---------------------------------------------------------------------------
# Data objects (immutable-friendly; use dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    time_available: int                      # minutes per day available for pet care
    preferences: dict = field(default_factory=dict)  # e.g. {"preferred_time": "morning"}
    pets: list[Pet] = field(default_factory=list)    # set after Pet is created to avoid circular init


@dataclass
class Pet:
    name: str
    species: Literal["dog", "cat", "other"]
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list by object identity."""
        try:
            self.tasks.remove(task)
        except ValueError as exc:
            raise ValueError("Task not found on this pet") from exc


@dataclass
class Task:
    name: str
    category: Literal["walk", "feeding", "meds", "enrichment", "grooming", "other"]
    duration: int                            # minutes
    priority: Literal["high", "medium", "low"]
    frequency: Literal["daily", "twice_daily", "weekly", "as_needed"]
    notes: str = ""
    scheduled_time: str | None = None   # optional "HH:MM", e.g. "08:30"
    due_date: str | None = None         # "YYYY-MM-DD" of the next occurrence


@dataclass
class ScheduledTask:
    task: Task
    order: int                               # position in the day (1-based)
    status: Literal["pending", "completed", "skipped"] = "pending"
    scheduled_time: str | None = None   # propagated from task.scheduled_time at creation

    def mark_complete(self, completed_on: str | None = None) -> Task | None:
        """Mark this scheduled task as completed.

        For daily and weekly tasks, automatically creates and returns a new Task
        instance for the next occurrence using timedelta:
          - daily  → next due date is completed_on + 1 day
          - weekly → next due date is completed_on + 7 days

        Args:
            completed_on: ISO date string ("YYYY-MM-DD") for when the task was
                          completed. Defaults to today if not provided.

        Returns:
            A new Task for the next occurrence (daily/weekly), or None for
            twice_daily and as_needed tasks which do not auto-reschedule.
        """
        self.status = "completed"

        frequency = self.task.frequency
        if frequency not in ("daily", "weekly"):
            return None

        base_date = Date.fromisoformat(completed_on) if completed_on else Date.today()
        delta = timedelta(days=1) if frequency == "daily" else timedelta(weeks=1)
        next_due = (base_date + delta).isoformat()

        return replace(self.task, due_date=next_due)


@dataclass
class DailyPlan:
    date: str                                # e.g. "2026-04-01"
    owner: Owner
    pet: Pet
    time_available: int                      # required — copied from owner.time_available at plan creation
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    time_used: int = 0                       # sum of scheduled task durations
    reasoning: str = ""                      # plain-text explanation of scheduling decisions
    warnings: list[str] = field(default_factory=list)  # conflict warning messages

    def total_tasks(self) -> int:
        """Return the total number of tasks considered (scheduled + skipped)."""
        return len(self.scheduled_tasks) + len(self.skipped_tasks)

    def summary(self) -> str:
        """Return a short human-readable summary of the plan."""
        scheduled = len(self.scheduled_tasks)
        skipped = len(self.skipped_tasks)
        return (
            f"{self.date}: {scheduled} scheduled, {skipped} skipped, "
            f"{self.time_used}/{self.time_available} minutes used."
        )


# ---------------------------------------------------------------------------
# Scheduler (behaviour class — not a dataclass)
# ---------------------------------------------------------------------------

class Scheduler:
    """Generates a DailyPlan for a specific pet given the owner's time constraints."""

    def __init__(self, owner: Owner, pet: Pet):
        if pet not in owner.pets:
            raise ValueError(f"Pet '{pet.name}' does not belong to owner '{owner.name}'")
        self.owner = owner
        self.pet = pet

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort Task objects by their scheduled_time attribute using a lambda key.

        Tasks are sorted as "HH:MM" strings — Python compares them
        lexicographically, which works correctly for zero-padded times.
        Tasks with no scheduled_time are placed last (sentinel "99:99").
        """
        return sorted(
            tasks,
            key=lambda task: task.scheduled_time if task.scheduled_time is not None else "99:99",
        )

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks into scheduling order using a multi-key lambda.

        The sort key is a tuple compared left-to-right by Python's sorted():
          1. Priority rank (high=0, medium=1, low=2) — most important tasks first.
          2. scheduled_time as an "HH:MM" string — earlier times first within a
             priority band. Tasks with no scheduled_time use the sentinel "99:99",
             which sorts after any valid time lexicographically.
          3. Duration (ascending) — shorter tasks first when time and priority tie,
             maximising the number of tasks that fit in the budget.
          4. Name (alphabetical) — stable tiebreaker so output is deterministic.
        """
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda task: (
                priority_rank.get(task.priority, 3),
                task.scheduled_time if task.scheduled_time is not None else "99:99",
                task.duration,
                task.name,
            ),
        )

    def check_conflicts(self, scheduled_tasks: list[ScheduledTask]) -> list[str]:
        """Return warning messages for any time-overlapping tasks.

        Calls detect_conflicts() and formats each conflicting pair as a
        plain-text warning. Never raises — always returns a (possibly empty) list
        so the caller can print warnings without crashing.
        """
        warnings: list[str] = []
        for a, b in detect_conflicts(scheduled_tasks):
            warnings.append(
                f"WARNING: '{a.task.name}' ({a.scheduled_time}, {a.task.duration} min) "
                f"overlaps with '{b.task.name}' ({b.scheduled_time}, {b.task.duration} min) "
                f"for {self.pet.name}."
            )
        return warnings

    def _build_reasoning(
        self,
        scheduled: list[Task],
        skipped: list[Task],
    ) -> str:
        """Produce a plain-text explanation of why tasks were chosen and ordered."""
        lines: list[str] = []

        if scheduled:
            lines.append("Scheduled the following tasks in priority order:")
            for index, task in enumerate(scheduled, start=1):
                lines.append(
                    f"{index}. {task.name} — priority {task.priority}, {task.duration} min"
                )
        else:
            lines.append("No tasks could be scheduled within the available time.")

        if skipped:
            lines.append("")
            lines.append("Skipped these tasks due to time or frequency constraints:")
            for task in skipped:
                lines.append(
                    f"- {task.name} ({task.frequency}, priority {task.priority}, {task.duration} min)"
                )

        return "\n".join(lines)

    def generate(self, date: str) -> DailyPlan:
        """Build a DailyPlan for the given date using a greedy scheduling algorithm.

        Steps:
          1. Filter — weekly tasks are excluded on any day that is not Monday
             (weekday() == 0); all other frequencies are always eligible.
          2. Sort — eligible tasks are ordered by _sort_tasks() (priority → time
             → duration → name).
          3. Greedy pack — tasks are added one by one in sort order. A task is
             scheduled if its duration fits in the remaining budget; otherwise it
             is skipped. twice_daily tasks consume 2 × duration and produce two
             ScheduledTask entries (morning slot carries the task's scheduled_time;
             the second slot has no explicit time).
          4. Reasoning — a plain-text explanation is generated via _build_reasoning().
          5. Conflict check — check_conflicts() scans the scheduled list for
             overlapping time windows and attaches any warnings to the plan.

        Args:
            date: ISO date string ("YYYY-MM-DD") for which to generate the plan.

        Returns:
            A DailyPlan containing the scheduled tasks, skipped tasks, time used,
            reasoning text, and any conflict warnings.
        """
        plan_date = Date.fromisoformat(date)
        available = self.owner.time_available
        eligible: list[Task] = []
        skipped: list[Task] = []

        for task in self.pet.tasks:
            if task.frequency == "weekly" and plan_date.weekday() != 0:
                skipped.append(task)
            else:
                eligible.append(task)

        sorted_tasks = self._sort_tasks(eligible)
        scheduled: list[ScheduledTask] = []
        time_used = 0

        for task in sorted_tasks:
            if task.frequency == "twice_daily":
                cost = task.duration * 2
                if time_used + cost <= available:
                    time_used += cost
                    scheduled.append(
                        ScheduledTask(task=task, order=len(scheduled) + 1,
                                      scheduled_time=task.scheduled_time)
                    )
                    scheduled.append(
                        ScheduledTask(task=task, order=len(scheduled) + 1,
                                      scheduled_time=None)
                    )
                else:
                    skipped.append(task)
            else:
                if time_used + task.duration <= available:
                    time_used += task.duration
                    scheduled.append(
                        ScheduledTask(task=task, order=len(scheduled) + 1,
                                      scheduled_time=task.scheduled_time)
                    )
                else:
                    skipped.append(task)

        reasoning = self._build_reasoning([task.task for task in scheduled], skipped)
        warnings = self.check_conflicts(scheduled)

        return DailyPlan(
            date=date,
            owner=self.owner,
            pet=self.pet,
            time_available=available,
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            time_used=time_used,
            reasoning=reasoning,
            warnings=warnings,
        )


# ---------------------------------------------------------------------------
# Utility: filtering and conflict detection
# ---------------------------------------------------------------------------

def filter_plans(
    plans: list[DailyPlan],
    *,
    pet_name: str | None = None,
    status: Literal["pending", "completed", "skipped"] | None = None,
) -> list[ScheduledTask]:
    """Return ScheduledTask entries across all plans matching the given filters.

    Args:
        plans:     list of DailyPlan objects (typically one per pet).
        pet_name:  if given, only include tasks from plans whose pet.name matches.
        status:    if given, only include ScheduledTask entries with this status.

    Returns:
        A flat list of matching ScheduledTask objects, preserving plan order.
    """
    results: list[ScheduledTask] = []
    for plan in plans:
        if pet_name is not None and plan.pet.name != pet_name:
            continue
        for st in plan.scheduled_tasks:
            if status is None or st.status == status:
                results.append(st)
    return results


def _parse_time(t: str) -> int:
    """Convert an "HH:MM" string to total minutes elapsed since midnight.

    Splits the string on ':' to extract hours and minutes, then computes:
        total_minutes = hours * 60 + minutes

    This produces a single integer that can be compared with simple arithmetic,
    avoiding the need to import datetime.time just for overlap calculations.

    Example: "08:30" → 8 * 60 + 30 = 510
    """
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def detect_conflicts(
    scheduled_tasks: list[ScheduledTask],
) -> list[tuple[ScheduledTask, ScheduledTask]]:
    """Find all pairs of scheduled tasks whose time windows overlap.

    Algorithm (O(n²) pairwise comparison):
      1. Filter the input down to only tasks that have a scheduled_time, since
         tasks without an explicit time cannot be checked for overlap.
      2. For every unique pair (i, j) where i < j, convert both scheduled_times
         to minutes-since-midnight using _parse_time(), then compute each task's
         end time as start + duration.
      3. Two intervals [a_start, a_end) and [b_start, b_end) overlap when:
             NOT (a_end <= b_start OR b_end <= a_start)
         Touching endpoints (a_end == b_start) are treated as back-to-back, not
         overlapping, consistent with half-open interval semantics.
      4. Each conflicting pair is appended exactly once (i < j ordering).

    The O(n²) approach is intentional — a daily task list rarely exceeds a few
    dozen items, so the simplicity outweighs any benefit from a more complex
    sweep-line algorithm.

    Args:
        scheduled_tasks: the list of ScheduledTask objects to check.

    Returns:
        A list of (task_a, task_b) tuples where each pair represents a conflict.
    """
    timed = [st for st in scheduled_tasks if st.scheduled_time is not None]
    conflicts: list[tuple[ScheduledTask, ScheduledTask]] = []
    for i in range(len(timed)):
        for j in range(i + 1, len(timed)):
            a = timed[i]
            b = timed[j]
            a_start = _parse_time(a.scheduled_time)  # type: ignore[arg-type]
            a_end   = a_start + a.task.duration
            b_start = _parse_time(b.scheduled_time)  # type: ignore[arg-type]
            b_end   = b_start + b.task.duration
            if not (a_end <= b_start or b_end <= a_start):
                conflicts.append((a, b))
    return conflicts
