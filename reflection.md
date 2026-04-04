# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Core Action
- add user and pet
- add tasks
- create scedules
1. User
name, time_available (minutes/day), preferences

2. Pet
name, species, owner

3. Task
name, category, duration, priority, pet, notes

4. ScheduledTask (new)
task, order, status

5. DailyPlan (replaces schedule)
date, user, pet, scheduled_tasks[], skipped_tasks[], time_available, time_used, reasoning
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
-> removed priority from User
-> added priority and category in task
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a **greedy, priority-first packing algorithm** rather than checking for exact time-slot conflicts before scheduling. It fills the day by fitting the highest-priority tasks first until the time budget runs out — it does not try to rearrange lower-priority tasks around a conflict to find a valid combination.

This means conflict detection runs *after* the schedule is built, as a separate warning pass. Two tasks that overlap in time (e.g., "Morning walk" at 08:00 for 30 min and "Training session" at 08:15 for 20 min) will both be scheduled if there is enough total budget, and only then flagged with a warning. The scheduler does not automatically move one task to a different time to resolve the conflict.

This tradeoff is reasonable for a personal pet-care app because:
1. **Simplicity over perfection** — a greedy approach is easy to reason about and debug. Solving the full constraint-satisfaction problem (find a non-overlapping assignment that maximises priority) is NP-hard and unnecessary for a handful of daily tasks.
2. **Owner stays in control** — surfacing a warning and letting the owner decide whether to reschedule is more appropriate than silently reordering their tasks without explanation.
3. **Most tasks lack an exact time** — `scheduled_time` is optional. When tasks have no fixed time, overlap is undefined and the greedy order is the best available heuristic anyway.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
