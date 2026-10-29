# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Add a pet** — enter the owner's name and register one or more pets (name, species, age).
2. **Schedule a care task** — give a pet a task such as a walk, feeding, medication, or vet appointment, with a time, duration, priority, and how often it repeats.
3. **See today's plan** — view today's tasks across all pets in time order, with warnings when two tasks clash, and mark tasks done as the day goes.

**a. Initial design**

My first UML draft (`diagrams/uml_draft.mmd`) had four classes:

- **Task** (dataclass) — one care activity: description, time (`"HH:MM"`), duration, priority, frequency (once/daily/weekly), due date, and whether it is done.
- **Pet** (dataclass) — a pet's details plus the list of tasks that belong to it.
- **Owner** — the person using the app; holds a list of pets and the minutes they have available per day, and can hand back every task across all pets.
- **Scheduler** — the "brain". It holds no data of its own; it asks the Owner for tasks and then sorts, filters, checks conflicts, and builds a daily plan.

Relationships: an Owner *has* many Pets (aggregation), a Pet *owns* many Tasks (composition — a task doesn't make sense without its pet), and the Scheduler *uses* an Owner.

**b. Design changes**

After reviewing the skeleton I made these changes before implementing:

- **Added an `id` to Task.** The draft had `Pet.remove_task(task_id)` but Task had no id, so there was no reliable way to identify one task (two "Feed" tasks at different times look the same by description). The Streamlit UI also needs a stable key for "mark done" buttons.
- **Moved "mark complete" up to the Scheduler** (`Scheduler.mark_task_complete`) in addition to `Task.mark_complete()`. A Task can flip its own flag, but it can't add the *next* occurrence of a recurring task to its pet's list — that requires knowing the pet, which the Scheduler does.
- **Kept `pet_name` on Task** rather than a full back-reference to the Pet object. A plain string avoids a circular reference (which would complicate JSON saving later) while still letting a flat list of tasks say which pet each belongs to.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:

- **Time of day** — every task has a start time and a duration, used for ordering and for spotting overlaps.
- **Priority** — high / medium / low. When the owner can't do everything, high-priority tasks are kept first.
- **The owner's time budget** — `Owner.available_minutes` caps how much care fits into one day's plan.
- **Completion status and due date** — finished tasks and tasks due on other days are left out of today's plan and conflict checks.

Priority comes first because it covers the things that actually matter for a pet's health: medication and feeding can't be skipped, but grooming can wait a day. Time of day comes second, as the tie-breaker and the order the plan is shown in, because that's how an owner actually works through the day.

**b. Tradeoffs**

- **Greedy plan instead of an optimal one.** `generate_plan()` takes tasks highest-priority first and adds each one if it still fits in the budget. It never tries combinations, so it can leave time unused. For example, if 25 minutes are left and the next task needs 45, it skips that task even if dropping a 20-minute medium task earlier would have let a more useful mix fit. A true "best fit" is a knapsack problem; for a handful of daily pet tasks the greedy result is easy to explain ("high priority first, until time runs out"), which matters more to an owner than squeezing out the last few minutes.
- **Conflicts treat the owner as able to do only one thing at a time.** `detect_conflicts()` flags *overlapping* durations (not just identical start times), across all pets. That catches real problems like a 30-minute walk at 18:00 clashing with a play session at 18:10. But it also flags things one person can do together (feeding two cats at once). I chose to over-warn: a warning is cheap to ignore, while a missed medication isn't. Conflicts are warnings, not errors, so the owner stays in control.
- **Simple pairwise check.** Conflict detection sorts by start time and compares each task only with the ones that start before it ends. That is O(n log n) plus the number of overlaps, which is plenty for a day's worth of pet tasks; I kept the nested loop instead of an interval tree because it's much easier to read.

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
