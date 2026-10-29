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

Run the suite from the project root:

```bash
python -m pytest
```

`pytest.ini` puts the project root on the import path, so no `PYTHONPATH` setup is needed.

**What the tests cover** (`tests/test_pawpal.py`, 34 tests):

- **Basics** — `mark_complete()` flips status; adding a task grows the pet's list and tags it with the pet's name; owners gather tasks from all pets; duplicate pet names and invalid times are rejected.
- **Sorting** — tasks added out of order come back in chronological order; `"9:00"` is padded so it sorts before `"10:00"`; priority sort puts high before medium before low, then orders by time.
- **Filtering** — by pet (case-insensitive), by completion status, both combined, and by day.
- **Recurrence** — completing a daily task creates a new one for tomorrow (including across a month boundary); weekly tasks move 7 days; one-time tasks don't recur; completing the same task twice doesn't create a duplicate.
- **Conflicts** — identical start times and overlapping durations are flagged (same pet and different pets); back-to-back tasks are *not*; finished tasks and other days are ignored; a three-way overlap reports each overlapping pair.
- **Edge cases** — a pet with no tasks, an empty day, a fully booked day for the free-slot finder, and a missing `data.json`.
- **Planning & persistence** — the daily plan keeps high-priority tasks inside the time budget and skips the rest; saving to JSON and loading back gives identical tasks.

Sample test output:

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0
cachedir: .pytest_cache
rootdir: pawpal-plus
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 34 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  2%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  5%]
tests/test_pawpal.py::test_owner_collects_tasks_from_all_pets PASSED     [  8%]
tests/test_pawpal.py::test_duplicate_pet_name_rejected PASSED            [ 11%]
tests/test_pawpal.py::test_invalid_time_rejected[24:00] PASSED           [ 14%]
tests/test_pawpal.py::test_invalid_time_rejected[12:60] PASSED           [ 17%]
tests/test_pawpal.py::test_invalid_time_rejected[noon] PASSED            [ 20%]
tests/test_pawpal.py::test_single_digit_hour_is_zero_padded PASSED       [ 23%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 26%]
tests/test_pawpal.py::test_sort_by_time_handles_hours_before_ten PASSED  [ 29%]
tests/test_pawpal.py::test_sort_by_priority_then_time PASSED             [ 32%]
tests/test_pawpal.py::test_schedule_for_pet_with_no_tasks_is_empty PASSED [ 35%]
tests/test_pawpal.py::test_filter_by_pet_name_is_case_insensitive PASSED [ 38%]
tests/test_pawpal.py::test_filter_by_completion_status PASSED            [ 41%]
tests/test_pawpal.py::test_filters_combine PASSED                        [ 44%]
tests/test_pawpal.py::test_tasks_for_day_excludes_other_days PASSED      [ 47%]
tests/test_pawpal.py::test_completing_daily_task_creates_one_for_next_day PASSED [ 50%]
tests/test_pawpal.py::test_completing_weekly_task_creates_one_for_next_week PASSED [ 52%]
tests/test_pawpal.py::test_daily_recurrence_crosses_month_end PASSED     [ 55%]
tests/test_pawpal.py::test_one_time_task_does_not_recur PASSED           [ 58%]
tests/test_pawpal.py::test_completing_same_task_twice_does_not_duplicate PASSED [ 61%]
tests/test_pawpal.py::test_mark_unknown_task_returns_none PASSED         [ 64%]
tests/test_pawpal.py::test_exact_same_time_is_flagged PASSED             [ 67%]
tests/test_pawpal.py::test_overlapping_durations_are_flagged_for_same_pet PASSED [ 70%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 73%]
tests/test_pawpal.py::test_completed_and_other_day_tasks_ignored_in_conflicts PASSED [ 76%]
tests/test_pawpal.py::test_three_way_overlap_reports_every_pair PASSED   [ 79%]
tests/test_pawpal.py::test_next_slot_finds_first_gap PASSED              [ 82%]
tests/test_pawpal.py::test_next_slot_on_empty_day_is_earliest PASSED     [ 85%]
tests/test_pawpal.py::test_next_slot_none_when_day_is_full PASSED        [ 88%]
tests/test_pawpal.py::test_plan_keeps_high_priority_within_budget PASSED [ 91%]
tests/test_pawpal.py::test_plan_skips_completed_tasks PASSED             [ 94%]
tests/test_pawpal.py::test_save_and_load_round_trip PASSED               [ 97%]
tests/test_pawpal.py::test_load_missing_file_returns_none PASSED         [100%]

============================== 34 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5).** Every scheduling rule I relied on has a test, including the edge cases most likely to break (padding of times, month rollover, double completion, back-to-back vs. overlapping tasks). I'm holding back one star because the Streamlit UI is only checked by hand, and the scheduler doesn't yet handle tasks that cross midnight or time zones.

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
