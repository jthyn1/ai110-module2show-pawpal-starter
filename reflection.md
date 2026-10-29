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

<!-- TODO: These answers are drafted from what happened in the Claude Code session. Rewrite them in your own words and add your own judgment calls. -->

**a. How you used AI**

I used Claude Code (an agent in the terminal) for the whole build. I gave it the full assignment and it worked through each phase in order: the UML draft and class skeletons, the core classes and CLI demo, the algorithms, the test suite, the Streamlit UI, and the docs. After each phase it ran `main.py` and `pytest` and made a commit, so the history shows the project growing in steps.

The most helpful requests were specific about *behavior* rather than code: "completing a daily task should create tomorrow's copy", "conflicts should be a warning, not a crash", "a time budget decides what fits in the day". Asking it to say which method does what (for the Smarter Scheduling table) also made it easy to check the code against the docs.

**b. Judgment and verification**

Changes made after looking at actual output instead of trusting the first version:

- The first "Still to do" list in the demo printed tasks in whatever order they were stored, which was hard to read. It now runs through `sort_by_time()` before printing.
- The first version of the project also included the optional challenges (a next-free-slot finder, JSON saving, and emoji/table formatting). I removed them to keep the submission focused on the required features.
- Recurrence: completing an already-complete task is a no-op. Otherwise a double-click on "done" in Streamlit would create two copies of tomorrow's task. There is a test for this.

How it was verified: 29 pytest tests, the `main.py` output checked by hand against expected times, and the Streamlit app driven with Streamlit's `AppTest` (add pets → add overlapping tasks → see the warning → mark done → confirm the next occurrence was created).

<!-- TODO: Add a moment where *you* disagreed with or changed something the AI produced, and why. -->

**Algorithm simplification (Phase 4, Step 5).** For `detect_conflicts()`, a shorter version is possible with `itertools.combinations(tasks, 2)` and an overlap check on every pair. It's one line shorter but compares every pair even when tasks are hours apart, and it hides the "sorted, so we can stop early" idea. I kept the sorted loop with `break` because it's still easy to read and the early exit is explained in the docstring.

---

## 4. Testing and Verification

**a. What you tested**

29 pytest tests in `tests/test_pawpal.py`, grouped by behavior:

- **Sorting** — out-of-order tasks come back chronologically, `"9:00"` sorts before `"10:00"`, and priority sorting breaks ties by time.
- **Filtering** — by pet, by completion status, both together, and by day.
- **Recurrence** — daily → tomorrow (including Oct 31 → Nov 1), weekly → +7 days, one-time tasks don't recur, and completing a task twice doesn't create a duplicate.
- **Conflicts** — same start time, overlapping durations, back-to-back tasks (should *not* conflict), completed tasks ignored, and a three-way overlap.
- **Edge cases** — a pet with no tasks, an empty day, and bad input times.
- **Planning** — the time budget is respected in priority order and finished tasks are left out.

These matter because they are the rules the owner trusts without checking. If sorting is wrong at 9 vs. 10 o'clock, or a daily medication silently fails to reappear tomorrow, the app is worse than a paper list. The boundary cases (back-to-back vs. overlapping, month rollover) are where off-by-one mistakes tend to hide.

**b. Confidence**

4 out of 5. All 29 tests pass, and the CLI demo output matches what I expect by hand. Next I would test:

- Tasks that run past midnight (e.g., 23:45 for 30 minutes). Right now the end time just goes past 24:00 and isn't checked against the next day.
- Completing a recurring task whose next occurrence lands on a time that already has another task (the new task should show up in that day's conflicts).
- The Streamlit UI flows (add → complete → filter), which are only checked manually right now.

---

## 5. Reflection

<!-- TODO: Personal section — edit to reflect your own view. -->

**a. What went well**

Keeping the Scheduler separate from the data. Because `Scheduler` only reads from `Owner`, the same methods drive the CLI demo, the tests, and the Streamlit app with no duplicate logic. Adding the UI at the end mostly meant calling methods that were already tested.

**b. What you would improve**

- Save pets and tasks to a file so they survive restarting the app (right now they live only in the Streamlit session).
- Let the daily plan *move* tasks into free slots when they conflict, instead of only warning.
- Make the "available time" a window (e.g. 07:00–09:00 and 17:00–20:00) rather than a single number of minutes.
- Handle tasks that cross midnight.

**c. Key takeaway**

Designing the classes and their responsibilities first made the AI's output much easier to check. With a UML diagram and a skeleton in place, each generated method had a clear job, and tests could pin down exactly what "correct" meant. The AI is fast at writing code. Deciding what the code should do, and checking that it does, is still my job.
