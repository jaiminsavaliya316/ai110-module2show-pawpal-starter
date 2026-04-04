import pytest
from pawpal_system import (
    Owner, Pet, Task, ScheduledTask, DailyPlan, Scheduler,
    filter_plans, detect_conflicts,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def owner():
    return Owner(name="Jordan", time_available=60)


@pytest.fixture
def pet(owner):
    p = Pet(name="Mochi", species="dog", owner=owner)
    owner.pets.append(p)
    return p


@pytest.fixture
def task():
    return Task(
        name="Morning walk",
        category="walk",
        duration=30,
        priority="high",
        frequency="daily",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status(task):
    """mark_complete() should change status from 'pending' to 'completed'."""
    scheduled = ScheduledTask(task=task, order=1)
    assert scheduled.status == "pending"

    scheduled.mark_complete()

    assert scheduled.status == "completed"


def test_mark_complete_daily_returns_next_task():
    """mark_complete() on a daily task should return a new Task due the next day."""
    t = Task(name="Walk", category="walk", duration=20, priority="high", frequency="daily")
    st = ScheduledTask(task=t, order=1)
    next_task = st.mark_complete(completed_on="2026-04-03")
    assert next_task is not None
    assert next_task.due_date == "2026-04-04"


def test_mark_complete_weekly_returns_next_task_7_days_later():
    """mark_complete() on a weekly task should return a new Task due 7 days later."""
    t = Task(name="Bath", category="grooming", duration=30, priority="medium", frequency="weekly")
    st = ScheduledTask(task=t, order=1)
    next_task = st.mark_complete(completed_on="2026-04-03")
    assert next_task is not None
    assert next_task.due_date == "2026-04-10"


def test_mark_complete_next_task_preserves_original_fields():
    """The returned next Task should copy all fields from the original."""
    t = Task(name="Walk", category="walk", duration=20, priority="high",
             frequency="daily", scheduled_time="08:00", notes="leash required")
    st = ScheduledTask(task=t, order=1)
    next_task = st.mark_complete(completed_on="2026-04-03")
    assert next_task.name == "Walk"
    assert next_task.scheduled_time == "08:00"
    assert next_task.notes == "leash required"
    assert next_task.frequency == "daily"


def test_mark_complete_as_needed_returns_none():
    """mark_complete() on an as_needed task should return None (no auto-reschedule)."""
    t = Task(name="Play", category="enrichment", duration=15, priority="low", frequency="as_needed")
    st = ScheduledTask(task=t, order=1)
    assert st.mark_complete(completed_on="2026-04-03") is None


def test_mark_complete_twice_daily_returns_none():
    """mark_complete() on a twice_daily task should return None (no auto-reschedule)."""
    t = Task(name="Feeding", category="feeding", duration=5, priority="high", frequency="twice_daily")
    st = ScheduledTask(task=t, order=1)
    assert st.mark_complete(completed_on="2026-04-03") is None


def test_mark_complete_defaults_to_today():
    """mark_complete() with no date argument should use today's date."""
    from datetime import date, timedelta
    t = Task(name="Walk", category="walk", duration=20, priority="high", frequency="daily")
    st = ScheduledTask(task=t, order=1)
    next_task = st.mark_complete()
    expected = (date.today() + timedelta(days=1)).isoformat()
    assert next_task.due_date == expected


def test_add_task_increases_pet_task_count(pet, task):
    """add_task() should increase the pet's task list by one."""
    before = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == before + 1


# ---------------------------------------------------------------------------
# Feature 1: scheduled_time field and sort order
# ---------------------------------------------------------------------------

def test_task_scheduled_time_defaults_to_none():
    """Task.scheduled_time should be None when not provided."""
    t = Task(name="Walk", category="walk", duration=20, priority="high", frequency="daily")
    assert t.scheduled_time is None


def test_task_scheduled_time_can_be_set():
    """Task.scheduled_time should store a 'HH:MM' string."""
    t = Task(name="Walk", category="walk", duration=20, priority="high",
             frequency="daily", scheduled_time="08:30")
    assert t.scheduled_time == "08:30"


def test_scheduled_task_inherits_scheduled_time(owner, pet):
    """ScheduledTask.scheduled_time should be propagated from task.scheduled_time."""
    t = Task(name="Walk", category="walk", duration=20, priority="high",
             frequency="daily", scheduled_time="07:00")
    pet.add_task(t)
    plan = Scheduler(owner, pet).generate("2026-04-06")  # Monday
    st = plan.scheduled_tasks[0]
    assert st.scheduled_time == "07:00"


def test_sort_tasks_by_scheduled_time_within_priority(owner, pet):
    """Within the same priority, tasks with earlier scheduled_time come first."""
    t1 = Task(name="Late task",  category="walk",    duration=10, priority="high",
              frequency="daily", scheduled_time="10:00")
    t2 = Task(name="Early task", category="feeding", duration=10, priority="high",
              frequency="daily", scheduled_time="07:00")
    t3 = Task(name="No time",    category="other",   duration=10, priority="high",
              frequency="daily")
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    plan = Scheduler(owner, pet).generate("2026-04-06")
    names = [st.task.name for st in plan.scheduled_tasks]
    assert names.index("Early task") < names.index("Late task")
    assert names.index("Late task") < names.index("No time")


# ---------------------------------------------------------------------------
# Feature 2: filter_plans
# ---------------------------------------------------------------------------

def _make_two_pet_plans(owner):
    """Helper: create two pets with one task each and generate their plans."""
    owner2 = Owner(name=owner.name, time_available=owner.time_available,
                   preferences=owner.preferences, pets=[])
    pet_a = Pet(name="Mochi", species="dog", owner=owner2)
    pet_b = Pet(name="Luna",  species="cat", owner=owner2)
    owner2.pets.extend([pet_a, pet_b])
    pet_a.add_task(Task(name="Walk",  category="walk",     duration=10,
                        priority="high",   frequency="daily"))
    pet_b.add_task(Task(name="Brush", category="grooming", duration=10,
                        priority="medium", frequency="daily"))
    today = "2026-04-07"
    plan_a = Scheduler(owner2, pet_a).generate(today)
    plan_b = Scheduler(owner2, pet_b).generate(today)
    return plan_a, plan_b


def test_filter_plans_by_pet_name(owner):
    """filter_plans with pet_name should return only that pet's tasks."""
    plan_a, plan_b = _make_two_pet_plans(owner)
    results = filter_plans([plan_a, plan_b], pet_name="Mochi")
    assert len(results) == 1
    assert results[0].task.name == "Walk"


def test_filter_plans_by_status(owner):
    """filter_plans with status='pending' should return only pending tasks."""
    plan_a, plan_b = _make_two_pet_plans(owner)
    plan_a.scheduled_tasks[0].mark_complete()
    results = filter_plans([plan_a, plan_b], status="pending")
    assert all(r.status == "pending" for r in results)


def test_filter_plans_by_pet_and_status(owner):
    """Combining pet_name and status should narrow results to both criteria."""
    plan_a, plan_b = _make_two_pet_plans(owner)
    plan_a.scheduled_tasks[0].mark_complete()
    results = filter_plans([plan_a, plan_b], pet_name="Mochi", status="completed")
    assert len(results) == 1
    assert results[0].task.name == "Walk"
    assert results[0].status == "completed"


def test_filter_plans_no_filters_returns_all(owner):
    """filter_plans with no filters should return all scheduled tasks."""
    plan_a, plan_b = _make_two_pet_plans(owner)
    results = filter_plans([plan_a, plan_b])
    assert len(results) == 2


# ---------------------------------------------------------------------------
# Feature 3: twice_daily produces two ScheduledTask entries
# ---------------------------------------------------------------------------

def test_twice_daily_produces_two_entries(owner, pet):
    """A twice_daily task should appear twice in scheduled_tasks."""
    t = Task(name="Feeding", category="feeding", duration=5,
             priority="high", frequency="twice_daily")
    pet.add_task(t)
    plan = Scheduler(owner, pet).generate("2026-04-07")
    feeding_entries = [st for st in plan.scheduled_tasks if st.task.name == "Feeding"]
    assert len(feeding_entries) == 2


def test_twice_daily_consumes_double_duration(owner, pet):
    """A twice_daily task should consume 2 * duration minutes."""
    t = Task(name="Feeding", category="feeding", duration=5,
             priority="high", frequency="twice_daily")
    pet.add_task(t)
    plan = Scheduler(owner, pet).generate("2026-04-07")
    assert plan.time_used == 10


def test_twice_daily_skipped_when_budget_insufficient():
    """A twice_daily task is skipped entirely if 2*duration exceeds remaining budget."""
    tight_owner = Owner(name="Tight", time_available=8)
    tight_pet   = Pet(name="P", species="other", owner=tight_owner)
    tight_owner.pets.append(tight_pet)
    t = Task(name="Feeding", category="feeding", duration=5,
             priority="high", frequency="twice_daily")  # needs 10 min
    tight_pet.add_task(t)
    plan = Scheduler(tight_owner, tight_pet).generate("2026-04-07")
    assert len(plan.scheduled_tasks) == 0
    assert t in plan.skipped_tasks


# ---------------------------------------------------------------------------
# Feature 4: detect_conflicts
# ---------------------------------------------------------------------------

def _make_st(name: str, start: str, duration: int) -> ScheduledTask:
    """Helper: create a ScheduledTask with a fixed scheduled_time."""
    t = Task(name=name, category="other", duration=duration,
             priority="low", frequency="daily", scheduled_time=start)
    return ScheduledTask(task=t, order=1, scheduled_time=start)


def test_detect_conflicts_overlapping_tasks():
    """Two tasks whose windows overlap should be reported as a conflict."""
    a = _make_st("Task A", "09:00", 30)   # 09:00–09:30
    b = _make_st("Task B", "09:15", 30)   # 09:15–09:45 → overlap
    conflicts = detect_conflicts([a, b])
    assert len(conflicts) == 1
    assert (a, b) in conflicts


def test_detect_conflicts_no_overlap():
    """Tasks that are strictly sequential should not conflict."""
    a = _make_st("Task A", "09:00", 30)   # 09:00–09:30
    b = _make_st("Task B", "09:30", 30)   # 09:30–10:00 → touching, not overlapping
    assert detect_conflicts([a, b]) == []


def test_detect_conflicts_ignores_tasks_without_time(task):
    """Tasks with no scheduled_time should be ignored by conflict detection."""
    st_no_time = ScheduledTask(task=task, order=1)    # scheduled_time=None
    a = _make_st("Task A", "09:00", 30)
    assert detect_conflicts([a, st_no_time]) == []


def test_detect_conflicts_multiple_pairs():
    """All conflicting pairs in a larger list should be found."""
    a = _make_st("A", "08:00", 60)   # 08:00–09:00
    b = _make_st("B", "08:30", 60)   # 08:30–09:30 → conflicts with A
    c = _make_st("C", "09:00", 60)   # 09:00–10:00 → touches A (no conflict), conflicts with B
    conflicts = detect_conflicts([a, b, c])
    assert (a, b) in conflicts
    assert (b, c) in conflicts
    assert (a, c) not in conflicts
    assert len(conflicts) == 2
