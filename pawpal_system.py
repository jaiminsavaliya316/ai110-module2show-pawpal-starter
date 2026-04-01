from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date as Date
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


@dataclass
class ScheduledTask:
    task: Task
    order: int                               # position in the day (1-based)
    status: Literal["pending", "completed", "skipped"] = "pending"

    def mark_complete(self) -> None:
        """Mark this scheduled task as completed."""
        self.status = "completed"


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

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high → low), then by duration (short first)."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda task: (
                priority_rank.get(task.priority, 3),
                task.duration,
                task.name,
            ),
        )

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
        """Filter, sort, and greedily schedule the pet's tasks into a DailyPlan."""
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

        for order, task in enumerate(sorted_tasks, start=1):
            if time_used + task.duration <= available:
                time_used += task.duration
                scheduled.append(ScheduledTask(task=task, order=len(scheduled) + 1))
            else:
                skipped.append(task)

        reasoning = self._build_reasoning([task.task for task in scheduled], skipped)

        return DailyPlan(
            date=date,
            owner=self.owner,
            pet=self.pet,
            time_available=available,
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            time_used=time_used,
            reasoning=reasoning,
        )
