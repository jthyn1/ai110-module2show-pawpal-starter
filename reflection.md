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
- **Kept `pet_name` on Task** rather than a full back-reference to the Pet object. A plain string avoids a circular reference (Pet → Task → Pet) while still letting a flat list of tasks say which pet each belongs to.

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

I used Claude Code, an AI agent in the terminal, to implement the project. The most useful thing about this workflow is that it significantly reduces implementation complexity and makes the development process much easier and more productive, at the cost of not having eyes on all of the code implemented without backtracking and reading it all. The way I alleviated this was through verification that the program worked as intended while limit testing certain features to determine if they are functional enough for prod.

**b. Judgment and verification**

I removed the optional challenges because I wanted to limit the complexity of the program as much as possible in order to make the path to prod as seamless as possible. The downside to doing that is that it reduces the amount that I am challenged in terms of development skills; however, I feel I make that up through my own personal projects and work that I do outside of the class, so I don't miss much.

---

## 4. Testing and Verification

**a. What you tested**

32 pytest tests in `tests/test_pawpal.py`, grouped by behavior:

- **Sorting** — out-of-order tasks come back chronologically, `"9:00"` sorts before `"10:00"`, and priority sorting breaks ties by time.
- **Filtering** — by pet, by completion status, both together, and by day.
- **Recurrence** — daily → tomorrow (including Oct 31 → Nov 1), overdue tasks restart from tomorrow, weekly → +7 days, one-time tasks don't recur, and completing a task twice doesn't create a duplicate.
- **Conflicts** — same start time, overlapping durations, back-to-back tasks (should *not* conflict), completed tasks ignored, and a three-way overlap.
- **Edge cases** — a pet with no tasks, an empty day, bad input times, and end times past midnight.
- **Planning** — the time budget is respected in priority order and finished tasks are left out.

These matter because they are the rules the owner trusts without checking. If sorting is wrong at 9 vs. 10 o'clock, or a daily medication silently fails to reappear tomorrow, the app is worse than a paper list. The boundary cases (back-to-back vs. overlapping, month rollover) are where off-by-one mistakes tend to hide.

**b. Confidence**

4 out of 5. All 32 tests pass, and the CLI demo output matches what I expect by hand. Next I would test:

- Tasks that run past midnight (e.g., 23:45 for 30 minutes). The end time displays correctly (00:15), but conflict checks don't look into the next day, so it wouldn't clash with a 00:00 task tomorrow.
- Completing a recurring task whose next occurrence lands on a time that already has another task (the new task should show up in that day's conflicts).
- The Streamlit UI flows (add → complete → filter), which are only checked manually right now.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the workflow itself, as everything went very smoothly. Although I did rely on (and tried to abuse) Claude, in the end the parts that mattered most (judgment and reflection) I elected to do myself, which enabled the project to be more personal and a better learning experience.

**b. What you would improve**

Next time I would try to simplify the implementation more to reduce overhead for the user and complexity for debugging. AI tends to overbuild by a significant margin, so taking time to really dig deep and decide what should be implemented and what shouldn't, rather than building first and tearing down later, would be how I would change my approach.

**c. Key takeaway**

I learned how to better prompt AI to accomplish the correct things that the problem requires. The backtracking made me realize that I need to be better about how I go about prompts and to be more specific with what is needed and what is not.
