PawPal+ Scheduling App — Improvement Opportunities
Context
The user wants a curated list of small, actionable algorithm and logic improvements across the four core files (pawpal_system.py, uml.js, main.py, app.py). No implementation yet — this is a planning/discovery document.

Critical Files Scanned
pawpal_system.py — core data models + Scheduler logic
app.py — Streamlit UI
main.py — demo/CLI entry point
uml.js — class diagram (comment-only)
Improvements List
1. Scheduling Logic
#	Issue	File	Line(s)	Fix
S1	Weekly tasks hardcoded to Monday only	pawpal_system.py	145	Let Task or Scheduler accept a preferred_weekday instead of always using weekday() == 0
S2	twice_daily tasks scheduled once, not twice	pawpal_system.py	44, 154–158	Generate two ScheduledTask entries per twice_daily task (e.g., morning + evening instance)
S3	as_needed tasks have no urgency / recency logic	pawpal_system.py	144–148	Track last-completed date; bump priority if overdue by > N days
S4	No time-of-day sequencing (e.g., breakfast before walk)	pawpal_system.py	98–108	Add a secondary sort key based on category order: feeding → meds → walk → enrichment → grooming
S5	enumerate index in generate() is discarded	pawpal_system.py	154, 157	Remove the unused order from enumerate; ScheduledTask.order already set correctly via len(scheduled) + 1
2. Data Model
#	Issue	File	Line(s)	Fix
D1	Task has no time-of-day preference	pawpal_system.py	39–46	Add optional preferred_time: Literal["morning", "afternoon", "evening", "flexible"] = "flexible"
D2	Owner.preferences is unstructured dict, never read	pawpal_system.py	15	Replace with typed fields or read it in Scheduler (e.g., preferred_walk_time)
D3	Pet has no age or health info	pawpal_system.py	19–25	Add optional age_years: int = 0 and health_notes: str = "" to enable future smart recommendations
D4	Pet.add_task deduplication checks identity, not value	pawpal_system.py	26–29	Add __eq__ override to Task (by name + category), or check name uniqueness in add_task
D5	Time split across pets is always equal (main.py)	main.py	85	Allocate time proportionally if pets have different care_level
3. UI / App Logic (app.py)
#	Issue	File	Line(s)	Fix
U1	"Set Owner" silently resets all pets + tasks	app.py	30–37	Show a st.warning confirmation before resetting session state
U2	"Set Pet" clears all pets (owner.pets.clear())	app.py	53–54	Change to "Add Pet" model; let user pick active pet via st.selectbox
U3	Skipped-task "Reason" is hardcoded and often wrong	app.py	199–202	Store skip reason in DailyPlan.skipped_tasks as (Task, reason: str) tuples; display actual reason
U4	No visual time-utilization feedback	app.py	166–169	Add st.progress(plan.time_used / plan.time_available) below the metrics
U5	No way to remove or edit a task after adding	app.py	118–133	Add a delete button per row in task list (use st.session_state.pet.remove_task)
U6	Task list shows st.session_state.tasks, not pet.tasks	app.py	118–121	Use st.session_state.pet.tasks so display stays accurate if pet is changed
U7	No duplicate task name check in UI	app.py	101–116	Before creating new Task, check if same name + category already in pet.tasks; warn user
U8	mark_complete() exists but is never wired to UI	pawpal_system.py / app.py	55–57 / 171–187	Add a checkbox or button per scheduled task row to call mark_complete() and rerender status
4. Edge Cases
#	Issue	File	Line(s)	Fix
E1	No guard for time_available == 0	pawpal_system.py	92–95	Add assertion: if owner.time_available <= 0: raise ValueError(...)
E2	Single task duration > total available time gives no warning	pawpal_system.py	154–159	After scheduling, flag any skipped high-priority task whose duration alone exceeds available
E3	Date.fromisoformat() has no error handling	pawpal_system.py	139	Wrap in try/except ValueError with a descriptive message
Highest Impact (Top 5 to implement first)
S1 — Weekly task day flexibility (currently breaks for any non-Monday date)
S2 — twice_daily split into two scheduled instances
U2 — Multi-pet support in app (currently .clear() destroys all pets)
U3 — Accurate skip reasons (currently misleading to owner)
S4 — Category-based task ordering (biological logic: feed before walk)
Verification
Run python main.py to check scheduling output for Mochi and Luna
Run streamlit run app.py to visually verify UI changes
Write/run unit tests for Scheduler.generate() covering: Monday weekly, non-Monday weekly, twice_daily, as_needed, zero time