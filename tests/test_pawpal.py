import pytest
from pawpal_system import Owner, Pet, Task, ScheduledTask


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


def test_add_task_increases_pet_task_count(pet, task):
    """add_task() should increase the pet's task list by one."""
    before = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == before + 1
