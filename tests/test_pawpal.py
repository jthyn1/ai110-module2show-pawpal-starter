from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task, to_hhmm

TODAY = date(2026, 10, 29)


@pytest.fixture
def owner():
    """An owner with a dog and a cat and no tasks yet."""
    owner = Owner("Jordan", available_minutes=60)
    owner.add_pet(Pet("Mochi", "dog"))
    owner.add_pet(Pet("Luna", "cat"))
    return owner


def add(owner, pet_name, description, time, duration=15, priority="medium", frequency="once", day=TODAY):
    """Add a task to a pet and return it."""
    task = Task(description, time, duration, priority, frequency, due_date=day)
    owner.get_pet(pet_name).add_task(task)
    return task


# --- Phase 2 basics ---------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning walk", "07:30")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Breakfast", "08:00"))
    assert len(pet.tasks) == 1
    assert pet.tasks[0].pet_name == "Mochi"


def test_owner_collects_tasks_from_all_pets(owner):
    add(owner, "Mochi", "Walk", "07:00")
    add(owner, "Luna", "Breakfast", "08:00")
    assert {t.description for t in owner.get_all_tasks()} == {"Walk", "Breakfast"}


def test_duplicate_pet_name_rejected(owner):
    with pytest.raises(ValueError):
        owner.add_pet(Pet("mochi", "dog"))


@pytest.mark.parametrize("bad_time", ["24:00", "12:60", "noon"])
def test_invalid_time_rejected(bad_time):
    with pytest.raises(ValueError):
        Task("Walk", bad_time)


def test_single_digit_hour_is_zero_padded():
    assert Task("Walk", "7:05").time == "07:05"


def test_end_time_wraps_past_midnight():
    task = Task("Night meds", "23:45", 30)
    assert to_hhmm(task.end_minutes) == "00:15"


# --- Sorting ----------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(owner):
    add(owner, "Mochi", "Evening walk", "18:00")
    add(owner, "Luna", "Breakfast", "08:00")
    add(owner, "Mochi", "Morning walk", "07:30")
    add(owner, "Luna", "Lunch", "12:15")
    times = [t.time for t in Scheduler(owner).todays_schedule(TODAY)]
    assert times == ["07:30", "08:00", "12:15", "18:00"]


def test_sort_by_time_handles_hours_before_ten(owner):
    # "9:00" would sort after "10:00" as text; zero-padding prevents that.
    add(owner, "Mochi", "Late", "10:00")
    add(owner, "Mochi", "Early", "9:00")
    assert [t.description for t in Scheduler(owner).todays_schedule(TODAY)] == ["Early", "Late"]


def test_sort_by_priority_then_time(owner):
    add(owner, "Mochi", "Groom", "07:00", priority="low")
    add(owner, "Luna", "Meds", "09:00", priority="high")
    add(owner, "Mochi", "Walk", "08:00", priority="high")
    add(owner, "Luna", "Play", "06:00", priority="medium")
    scheduler = Scheduler(owner)
    ordered = scheduler.sort_by_priority(scheduler.get_all_tasks())
    assert [t.description for t in ordered] == ["Walk", "Meds", "Play", "Groom"]


def test_schedule_for_pet_with_no_tasks_is_empty(owner):
    scheduler = Scheduler(owner)
    assert scheduler.todays_schedule(TODAY) == []
    assert scheduler.filter_tasks(pet_name="Luna") == []


# --- Filtering --------------------------------------------------------------

def test_filter_by_pet_name_is_case_insensitive(owner):
    add(owner, "Mochi", "Walk", "07:00")
    add(owner, "Luna", "Breakfast", "08:00")
    result = Scheduler(owner).filter_tasks(pet_name="luna")
    assert [t.description for t in result] == ["Breakfast"]


def test_filter_by_completion_status(owner):
    done = add(owner, "Mochi", "Walk", "07:00")
    add(owner, "Luna", "Breakfast", "08:00")
    done.mark_complete()
    scheduler = Scheduler(owner)
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Walk"]
    assert [t.description for t in scheduler.filter_tasks(completed=False)] == ["Breakfast"]


def test_filters_combine(owner):
    walk = add(owner, "Mochi", "Walk", "07:00")
    add(owner, "Mochi", "Dinner", "17:00")
    add(owner, "Luna", "Breakfast", "08:00")
    walk.mark_complete()
    result = Scheduler(owner).filter_tasks(pet_name="Mochi", completed=False)
    assert [t.description for t in result] == ["Dinner"]


def test_tasks_for_day_excludes_other_days(owner):
    add(owner, "Mochi", "Today", "07:00")
    add(owner, "Mochi", "Tomorrow", "07:00", day=TODAY + timedelta(days=1))
    assert [t.description for t in Scheduler(owner).tasks_for_day(TODAY)] == ["Today"]


# --- Recurring tasks --------------------------------------------------------

def test_completing_daily_task_creates_one_for_next_day(owner):
    walk = add(owner, "Mochi", "Walk", "07:30", frequency="daily")
    upcoming = Scheduler(owner).mark_task_complete(walk.id, today=TODAY)

    assert walk.completed is True
    assert upcoming is not None
    assert upcoming.due_date == TODAY + timedelta(days=1)
    assert upcoming.time == "07:30"
    assert upcoming.completed is False
    assert upcoming.id != walk.id
    assert upcoming in owner.get_pet("Mochi").tasks


def test_completing_weekly_task_creates_one_for_next_week(owner):
    meds = add(owner, "Luna", "Flea meds", "09:00", frequency="weekly")
    upcoming = Scheduler(owner).mark_task_complete(meds.id, today=TODAY)
    assert upcoming.due_date == TODAY + timedelta(weeks=1)
    assert upcoming.pet_name == "Luna"


def test_daily_recurrence_crosses_month_end(owner):
    walk = add(owner, "Mochi", "Walk", "07:00", frequency="daily", day=date(2026, 10, 31))
    upcoming = Scheduler(owner).mark_task_complete(walk.id, today=date(2026, 10, 31))
    assert upcoming.due_date == date(2026, 11, 1)


def test_overdue_daily_task_recurs_from_today(owner):
    # Finishing a walk that was due 5 days ago should schedule tomorrow, not 4 days ago.
    walk = add(owner, "Mochi", "Walk", "07:00", frequency="daily", day=TODAY - timedelta(days=5))
    upcoming = Scheduler(owner).mark_task_complete(walk.id, today=TODAY)
    assert upcoming.due_date == TODAY + timedelta(days=1)


def test_completing_future_task_early_recurs_from_its_due_date(owner):
    # Ticking off tomorrow's walk today should create the one for the day after, not a duplicate.
    walk = add(owner, "Mochi", "Walk", "07:00", frequency="daily", day=TODAY + timedelta(days=1))
    upcoming = Scheduler(owner).mark_task_complete(walk.id, today=TODAY)
    assert upcoming.due_date == TODAY + timedelta(days=2)


def test_one_time_task_does_not_recur(owner):
    vet = add(owner, "Mochi", "Vet", "10:00")
    assert Scheduler(owner).mark_task_complete(vet.id) is None
    assert len(owner.get_pet("Mochi").tasks) == 1


def test_completing_same_task_twice_does_not_duplicate(owner):
    walk = add(owner, "Mochi", "Walk", "07:30", frequency="daily")
    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(walk.id, today=TODAY)
    assert scheduler.mark_task_complete(walk.id, today=TODAY) is None
    assert len(owner.get_pet("Mochi").tasks) == 2


def test_mark_unknown_task_returns_none(owner):
    assert Scheduler(owner).mark_task_complete("nope") is None


# --- Conflict detection -----------------------------------------------------

def test_exact_same_time_is_flagged(owner):
    add(owner, "Mochi", "Walk", "18:00", 30)
    add(owner, "Luna", "Play", "18:00", 20)
    warnings = Scheduler(owner).detect_conflicts(TODAY)
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Play" in warnings[0]
    assert "Mochi and Luna" in warnings[0]


def test_overlapping_durations_are_flagged_for_same_pet(owner):
    add(owner, "Mochi", "Walk", "07:00", 30)
    add(owner, "Mochi", "Breakfast", "07:20", 10)
    warnings = Scheduler(owner).detect_conflicts(TODAY)
    assert len(warnings) == 1
    assert "both for Mochi" in warnings[0]


def test_back_to_back_tasks_do_not_conflict(owner):
    add(owner, "Mochi", "Walk", "07:00", 30)
    add(owner, "Mochi", "Breakfast", "07:30", 10)
    assert Scheduler(owner).detect_conflicts(TODAY) == []


def test_completed_and_other_day_tasks_ignored_in_conflicts(owner):
    add(owner, "Mochi", "Walk", "07:00", 30).mark_complete()
    add(owner, "Luna", "Breakfast", "07:00", 10)
    add(owner, "Luna", "Tomorrow", "07:00", 10, day=TODAY + timedelta(days=1))
    assert Scheduler(owner).detect_conflicts(TODAY) == []


def test_three_way_overlap_reports_every_pair(owner):
    add(owner, "Mochi", "A", "08:00", 60)
    add(owner, "Luna", "B", "08:10", 10)
    add(owner, "Mochi", "C", "08:30", 10)
    assert len(Scheduler(owner).detect_conflicts(TODAY)) == 2  # A-B and A-C; B ends before C


# --- Daily plan -------------------------------------------------------------

def test_plan_keeps_high_priority_within_budget(owner):
    add(owner, "Mochi", "Groom", "07:00", 40, priority="low")
    add(owner, "Mochi", "Walk", "08:00", 30, priority="high")
    add(owner, "Luna", "Meds", "09:00", 5, priority="high")
    add(owner, "Luna", "Play", "10:00", 20, priority="medium")
    plan = Scheduler(owner).generate_plan(TODAY)  # budget is 60 min

    assert [e.task.description for e in plan.scheduled] == ["Walk", "Meds", "Play"]
    assert [e.task.description for e in plan.skipped] == ["Groom"]
    assert plan.minutes_used == 55


def test_plan_skips_completed_tasks(owner):
    add(owner, "Mochi", "Walk", "08:00", 30).mark_complete()
    plan = Scheduler(owner).generate_plan(TODAY)
    assert plan.scheduled == [] and plan.skipped == []

