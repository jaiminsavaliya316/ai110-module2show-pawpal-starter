from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler, filter_plans, detect_conflicts

# ---------------------------------------------------------------------------
# Setup: owner and pets
# ---------------------------------------------------------------------------

jordan = Owner(name="Jordan", time_available=120)  # 120 minutes available today

mochi = Pet(name="Mochi", species="dog", owner=jordan)
luna  = Pet(name="Luna",  species="cat", owner=jordan)

jordan.pets.extend([mochi, luna])

# ---------------------------------------------------------------------------
# Tasks for Mochi (dog) — added OUT OF ORDER intentionally
# ---------------------------------------------------------------------------

mochi.add_task(Task(
    name="Puzzle toy",
    category="enrichment",
    duration=20,
    priority="low",
    frequency="daily",
    scheduled_time="15:00",   # 3:00 PM — added first but latest in the day
))

mochi.add_task(Task(
    name="Flea medication",
    category="meds",
    duration=5,
    priority="medium",
    frequency="weekly",
    scheduled_time="12:00",   # noon — added second
))

mochi.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration=5,
    priority="high",
    frequency="twice_daily",
    scheduled_time="07:30",   # earliest — added third
))

mochi.add_task(Task(
    name="Morning walk",
    category="walk",
    duration=30,
    priority="high",
    frequency="daily",
    scheduled_time="08:00",   # second earliest — added last
))

# Intentional conflict: "Training session" starts at 08:15, inside the 08:00–08:30 walk window
mochi.add_task(Task(
    name="Training session",
    category="enrichment",
    duration=20,
    priority="medium",
    frequency="daily",
    scheduled_time="08:15",   # overlaps Morning walk (08:00–08:30)
))

# ---------------------------------------------------------------------------
# Tasks for Luna (cat) — also out of order
# ---------------------------------------------------------------------------

luna.add_task(Task(
    name="Feather wand play",
    category="enrichment",
    duration=15,
    priority="low",
    frequency="as_needed",
    scheduled_time="18:00",   # evening — added first
))

luna.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration=5,
    priority="high",
    frequency="twice_daily",
    scheduled_time="07:00",   # morning — added second
))

luna.add_task(Task(
    name="Brushing",
    category="grooming",
    duration=10,
    priority="medium",
    frequency="daily",
    scheduled_time="11:00",   # mid-morning — added last
))

# ---------------------------------------------------------------------------
# Demonstrate sort_by_time() before scheduling
# ---------------------------------------------------------------------------

print("=" * 50)
print("  TASKS ADDED (original order):")
print("=" * 50)
for t in mochi.tasks:
    print(f"  {t.scheduled_time or '??:??'}  {t.name}")

mochi_scheduler = Scheduler(jordan, mochi)
sorted_mochi_tasks = mochi_scheduler.sort_by_time(mochi.tasks)

print("\n  TASKS SORTED BY TIME (sort_by_time lambda key):")
for t in sorted_mochi_tasks:
    print(f"  {t.scheduled_time or 'no time'}  {t.name}")

# ---------------------------------------------------------------------------
# Generate today's schedule (split time evenly across pets)
# ---------------------------------------------------------------------------

today = date.today().isoformat()
time_per_pet = jordan.time_available // len(jordan.pets)

plans = []
for pet in jordan.pets:
    pet_owner = Owner(
        name=jordan.name,
        time_available=time_per_pet,
        preferences=jordan.preferences,
        pets=jordan.pets,
    )
    pet.owner = pet_owner
    plans.append(Scheduler(pet_owner, pet).generate(today))
    pet.owner = jordan

# ---------------------------------------------------------------------------
# Print today's full schedule
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print(f"  TODAY'S SCHEDULE — {today}")
print(f"  Owner : {jordan.name}")
print(f"  Budget: {jordan.time_available} min total / {time_per_pet} min per pet")
print("=" * 50)

for plan in plans:
    print(f"\n--- {plan.pet.name} ({plan.pet.species}) ---")

    if plan.scheduled_tasks:
        for st in plan.scheduled_tasks:
            time_label = st.scheduled_time or "     "
            print(f"  {st.order}. [{st.task.priority.upper():6}] {time_label}  {st.task.name:<22} {st.task.duration} min  [{st.status}]")
    else:
        print("  No tasks scheduled.")

    if plan.skipped_tasks:
        skipped_names = ", ".join(t.name for t in plan.skipped_tasks)
        print(f"  Skipped: {skipped_names}")

    print(f"\n  {plan.summary()}")
    print(f"\n  Reasoning:\n  " + plan.reasoning.replace("\n", "\n  "))

# ---------------------------------------------------------------------------
# Conflict detection — per-pet warnings from Scheduler.check_conflicts()
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("  CONFLICT WARNINGS")
print("=" * 50)

all_warnings = [w for plan in plans for w in plan.warnings]
if all_warnings:
    for w in all_warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# Cross-pet conflict check: find tasks from different pets that overlap in time
all_scheduled = [st for plan in plans for st in plan.scheduled_tasks]
cross_pet_conflicts = detect_conflicts(all_scheduled)
cross_pet_only = [
    (a, b) for a, b in cross_pet_conflicts
    if a not in plans[0].scheduled_tasks or b not in plans[0].scheduled_tasks
]
if cross_pet_only:
    print("\n  Cross-pet conflicts:")
    for a, b in cross_pet_only:
        print(
            f"  WARNING: '{a.task.name}' ({a.scheduled_time}, {a.task.duration} min) "
            f"overlaps with '{b.task.name}' ({b.scheduled_time}, {b.task.duration} min) "
            f"across pets."
        )

# ---------------------------------------------------------------------------
# Demonstrate filter_plans() — filter by pet name and by status
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("  FILTER DEMO")
print("=" * 50)

# Mark one of Mochi's tasks complete to make the status filter interesting
if plans[0].scheduled_tasks:
    plans[0].scheduled_tasks[0].mark_complete()

mochi_tasks = filter_plans(plans, pet_name="Mochi")
print(f"\n  All scheduled tasks for Mochi ({len(mochi_tasks)} tasks):")
for st in mochi_tasks:
    print(f"    {st.scheduled_time or '??:??'}  {st.task.name:<22} [{st.status}]")

pending = filter_plans(plans, status="pending")
print(f"\n  All PENDING tasks across both pets ({len(pending)} tasks):")
for st in pending:
    print(f"    {st.task.name:<22} [{st.status}]")

completed = filter_plans(plans, status="completed")
print(f"\n  All COMPLETED tasks across both pets ({len(completed)} tasks):")
for st in completed:
    print(f"    {st.task.name:<22} [{st.status}]")

print("\n" + "=" * 50)
