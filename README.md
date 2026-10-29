# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py`:

```
PawPal+ for Jordan (2 pets)

Today's Schedule
------------------------------------------------------------
  [ ] 07:30  Mochi    Morning walk            30 min  high
  [ ] 08:00  Luna     Breakfast                5 min  high
  [ ] 09:00  Luna     Flea medication          5 min  high
  [ ] 18:00  Mochi    Evening walk            30 min  medium
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in the `Scheduler` class in `pawpal_system.py`. The Scheduler stores no tasks itself; it asks the `Owner` for every pet's tasks (`Owner.get_all_tasks()`) and works on that list.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.todays_schedule()` | `sorted()` with `key=lambda t: (t.due_date, t.time)`. Zero-padded `"HH:MM"` strings sort correctly as text, so no time parsing is needed. |
| Priority sorting | `Scheduler.sort_by_priority()` | High → medium → low, then by time to break ties (Challenge 3). |
| Filtering | `Scheduler.filter_tasks(pet_name=..., completed=...)`, `Scheduler.tasks_for_day()` | Filters can be combined; any filter left as `None` is skipped. Pet names match case-insensitively. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags any two unfinished tasks on the same day whose time ranges *overlap* (start + duration), for the same pet or different pets. Returns a list of warning strings instead of raising, so the app keeps running. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Completing a `daily` or `weekly` task adds a copy due `due_date + timedelta(days=1)` or `timedelta(weeks=1)` to the same pet. Completing an already-done task does nothing, so a double-click can't create duplicates. |
| Next free slot | `Scheduler.next_available_slot(duration)` | Walks the day's tasks in time order and returns the first gap (between 07:00 and 22:00) long enough for the new task (Challenge 1). |
| Daily plan | `Scheduler.generate_plan()` → `DailyPlan` | Greedy: takes unfinished tasks highest-priority first while they fit in `Owner.available_minutes`, then shows the chosen ones in time order with a reason for each, plus what was skipped and why. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
