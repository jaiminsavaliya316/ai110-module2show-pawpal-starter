from __future__ import annotations
from dataclasses import dataclass, field
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
        ...

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list by object identity."""
        ...


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
        ...


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
        ...

    def summary(self) -> str:
        """Return a short human-readable summary of the plan."""
        ...


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
        ...

    def _build_reasoning(
        self,
        scheduled: list[Task],
        skipped: list[Task],
    ) -> str:
        """Produce a plain-text explanation of why tasks were chosen and ordered."""
        ...

    def generate(self, date: str) -> DailyPlan:
        """
        Generate and return a DailyPlan for the given date.

        Algorithm:
        1. Filter pet's tasks by frequency (skip weekly tasks on non-designated days, etc.).
        2. Sort remaining tasks by priority then duration.
        3. Greedily add tasks until time_available is exhausted.
        4. Remaining tasks go into skipped_tasks.
        5. Build reasoning string.
        """
        ...
