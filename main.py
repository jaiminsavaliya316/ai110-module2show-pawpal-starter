from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Setup: owner and pets
# ---------------------------------------------------------------------------

jordan = Owner(name="Jordan", time_available=90)  # 90 minutes available today

mochi = Pet(name="Mochi", species="dog", owner=jordan)
luna  = Pet(name="Luna",  species="cat", owner=jordan)

jordan.pets.extend([mochi, luna])

# ---------------------------------------------------------------------------
# Tasks for Mochi (dog)
# ---------------------------------------------------------------------------

mochi.add_task(Task(
    name="Morning walk",
    category="walk",
    duration=30,
    priority="high",
    frequency="daily",
))

mochi.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration=5,
    priority="high",
    frequency="twice_daily",
))

mochi.add_task(Task(
    name="Flea medication",
    category="meds",
    duration=5,
    priority="medium",
    frequency="weekly",
))

mochi.add_task(Task(
    name="Puzzle toy",
    category="enrichment",
    duration=20,
    priority="low",
    frequency="daily",
))

# ---------------------------------------------------------------------------
# Tasks for Luna (cat)
# ---------------------------------------------------------------------------

luna.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration=5,
    priority="high",
    frequency="twice_daily",
))

luna.add_task(Task(
    name="Brushing",
    category="grooming",
    duration=10,
    priority="medium",
    frequency="daily",
))

luna.add_task(Task(
    name="Feather wand play",
    category="enrichment",
    duration=15,
    priority="low",
    frequency="as_needed",
))

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
    # Temporarily point the pet to the split-budget owner for scheduling
    pet.owner = pet_owner
    plans.append(Scheduler(pet_owner, pet).generate(today))
    pet.owner = jordan  # restore original owner reference

# ---------------------------------------------------------------------------
# Print today's schedule
# ---------------------------------------------------------------------------

print("=" * 50)
print(f"  TODAY'S SCHEDULE — {today}")
print(f"  Owner : {jordan.name}")
print(f"  Budget: {jordan.time_available} min total / {time_per_pet} min per pet")
print("=" * 50)

for plan in plans:
    print(f"\n--- {plan.pet.name} ({plan.pet.species}) ---")

    if plan.scheduled_tasks:
        for st in plan.scheduled_tasks:
            print(f"  {st.order}. [{st.task.priority.upper():6}] {st.task.name:<22} {st.task.duration} min")
    else:
        print("  No tasks scheduled.")

    if plan.skipped_tasks:
        skipped_names = ", ".join(t.name for t in plan.skipped_tasks)
        print(f"  Skipped: {skipped_names}")

    print(f"\n  {plan.summary()}")
    print(f"\n  Reasoning:\n  " + plan.reasoning.replace("\n", "\n  "))

print("\n" + "=" * 50)
