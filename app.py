import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------------------------------------------------------------------------
# Section 1: Owner
# ---------------------------------------------------------------------------
st.subheader("Step 1: Owner")
owner_name = st.text_input("Owner name", value="Jordan")
time_available = st.number_input(
    "Minutes available today", min_value=10, max_value=480, value=90
)

if st.button("Set Owner"):
    st.session_state.owner = Owner(
        name=owner_name.strip(), time_available=int(time_available)
    )
    st.session_state.pet = None
    st.session_state.tasks = []
    st.session_state.plan = None
    st.success(f"Owner '{owner_name.strip()}' saved.")

if st.session_state.owner is None:
    st.info("Set an owner above to continue.")
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Pet
# ---------------------------------------------------------------------------
st.subheader("Step 2: Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Set Pet"):
    # Clear any previous pet from owner's list before adding the new one
    st.session_state.owner.pets.clear()
    new_pet = Pet(
        name=pet_name.strip(),
        species=species,
        owner=st.session_state.owner,
    )
    st.session_state.owner.pets.append(new_pet)
    st.session_state.pet = new_pet
    st.session_state.tasks = []
    st.session_state.plan = None
    st.success(f"Pet '{pet_name.strip()}' saved.")

if st.session_state.pet is None:
    st.info("Set a pet above to continue.")
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Add Tasks
# ---------------------------------------------------------------------------
st.subheader("Step 3: Add Tasks")

col1, col2 = st.columns(2)
with col1:
    task_name = st.text_input("Task name", value="Morning walk")
with col2:
    category = st.selectbox(
        "Category", ["walk", "feeding", "meds", "enrichment", "grooming", "other"]
    )

col3, col4 = st.columns(2)
with col3:
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20
    )
with col4:
    priority = st.selectbox("Priority", ["high", "medium", "low"])

col5, col6 = st.columns(2)
with col5:
    frequency = st.selectbox(
        "Frequency", ["daily", "twice_daily", "weekly", "as_needed"]
    )
with col6:
    scheduled_time = st.text_input(
        "Scheduled time (HH:MM, optional)", value="", placeholder="e.g. 08:30"
    )

notes = st.text_input("Notes (optional)", value="")

if st.button("Add Task"):
    if not task_name.strip():
        st.error("Task name cannot be blank.")
    else:
        # Basic HH:MM validation
        parsed_time = None
        if scheduled_time.strip():
            import re
            if re.match(r"^\d{2}:\d{2}$", scheduled_time.strip()):
                parsed_time = scheduled_time.strip()
            else:
                st.error("Scheduled time must be in HH:MM format (e.g. 08:30).")
                st.stop()

        task = Task(
            name=task_name.strip(),
            category=category,
            duration=int(duration),
            priority=priority,
            frequency=frequency,
            notes=notes,
            scheduled_time=parsed_time,
        )
        st.session_state.pet.add_task(task)
        st.session_state.tasks.append(task)
        st.session_state.plan = None
        st.success(f"Task '{task_name.strip()}' added.")

if st.session_state.tasks:
    st.markdown("**Current tasks** (sorted by scheduled time):")

    # Use Scheduler.sort_by_time to display tasks in time order
    scheduler_preview = Scheduler(
        owner=st.session_state.owner, pet=st.session_state.pet
    )
    sorted_preview = scheduler_preview.sort_by_time(st.session_state.tasks)

    PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}

    st.dataframe(
        [
            {
                "Time": t.scheduled_time or "—",
                "Name": t.name,
                "Category": t.category,
                "Duration (min)": t.duration,
                "Priority": PRIORITY_ICON.get(t.priority, t.priority),
                "Frequency": t.frequency,
                "Notes": t.notes or "—",
            }
            for t in sorted_preview
        ],
        use_container_width=True,
    )
else:
    st.info("No tasks added yet.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("Step 4: Generate Schedule")

if st.button("Generate Schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        try:
            today = date.today().isoformat()
            scheduler = Scheduler(
                owner=st.session_state.owner, pet=st.session_state.pet
            )
            st.session_state.plan = scheduler.generate(today)
        except ValueError as exc:
            st.error(str(exc))

# ---------------------------------------------------------------------------
# Section 5: Display DailyPlan
# ---------------------------------------------------------------------------
if st.session_state.plan is not None:
    plan = st.session_state.plan
    st.divider()
    st.subheader("Today's Plan")

    # ---- Conflict warnings — shown prominently at the top ----
    if plan.warnings:
        st.error(
            f"⚠️ **{len(plan.warnings)} scheduling conflict(s) detected for "
            f"{plan.pet.name}** — review the warnings below before your day starts."
        )
        for warning in plan.warnings:
            # Parse out the two task names for a friendlier message
            st.warning(
                f"**Schedule conflict:** {warning}\n\n"
                "_Tip: Edit the scheduled times of one of these tasks so they "
                "don't overlap, or reschedule the lower-priority task to another slot._"
            )

    # ---- Summary caption ----
    st.caption(plan.summary())

    # ---- Metrics ----
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Time Used", f"{plan.time_used} min")
    col_b.metric("Time Available", f"{plan.time_available} min")
    col_c.metric("Tasks Scheduled", len(plan.scheduled_tasks))

    time_remaining = plan.time_available - plan.time_used
    if time_remaining == 0:
        st.warning("Your available time is fully used — no room for extra tasks today.")
    elif time_remaining <= 15:
        st.warning(f"Only {time_remaining} minutes remain after scheduling.")
    else:
        st.success(f"{time_remaining} minutes of free time remaining today.")

    # ---- Scheduled tasks table ----
    if plan.scheduled_tasks:
        st.markdown("#### Scheduled Tasks")

        PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
        STATUS_ICON = {
            "pending": "🕐 pending",
            "completed": "✅ completed",
            "skipped": "⏭ skipped",
        }

        st.dataframe(
            [
                {
                    "Order": sched_task.order,
                    "Time": sched_task.scheduled_time or "—",
                    "Task": sched_task.task.name,
                    "Category": sched_task.task.category,
                    "Priority": PRIORITY_ICON.get(
                        sched_task.task.priority, sched_task.task.priority
                    ),
                    "Duration (min)": sched_task.task.duration,
                    "Frequency": sched_task.task.frequency,
                    "Status": STATUS_ICON.get(sched_task.status, sched_task.status),
                }
                for sched_task in plan.scheduled_tasks
            ],
            use_container_width=True,
        )

    # ---- Skipped tasks table ----
    if plan.skipped_tasks:
        st.markdown("#### Skipped Tasks")
        st.info(
            f"{len(plan.skipped_tasks)} task(s) could not be scheduled today — "
            "either due to time limits or frequency constraints (e.g. weekly tasks "
            "only run on Mondays)."
        )
        st.dataframe(
            [
                {
                    "Task": t.name,
                    "Category": t.category,
                    "Priority": t.priority,
                    "Duration (min)": t.duration,
                    "Frequency": t.frequency,
                    "Reason": (
                        "weekly task — not scheduled today"
                        if t.frequency == "weekly"
                        else "insufficient time remaining"
                    ),
                }
                for t in plan.skipped_tasks
            ],
            use_container_width=True,
        )

    # ---- Scheduling reasoning ----
    with st.expander("Scheduling Reasoning", expanded=True):
        st.text(plan.reasoning)
