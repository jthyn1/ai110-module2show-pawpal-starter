"""CLI demo for PawPal+: exercises sorting, filtering, recurrence, conflicts, and planning."""

from datetime import date, timedelta

from tabulate import tabulate

from pawpal_system import PRIORITY_BADGE, Owner, Pet, Scheduler, Task, task_emoji, to_hhmm


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print tasks as a table with status, emoji, and priority badges."""
    print(f"\n{title}")
    if not tasks:
        print("  (no tasks)")
        return
    rows = [
        [
            "✅" if t.completed else "⬜",
            f"{t.time}–{to_hhmm(t.end_minutes)}",
            t.pet_name,
            f"{task_emoji(t.description)} {t.description}",
            PRIORITY_BADGE[t.priority],
            t.frequency,
            t.due_date.isoformat(),
        ]
        for t in tasks
    ]
    headers = ["", "Time", "Pet", "Task", "Priority", "Repeats", "Due"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def build_demo_owner() -> Owner:
    """Create an owner with two pets and tasks added deliberately out of time order."""
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Evening walk", "18:00", 30, "medium", "daily"))
    luna.add_task(Task("Flea medication", "09:00", 5, "high", "weekly"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Breakfast", "08:00", 10, "high", "daily"))
    mochi.add_task(Task("Grooming", "08:15", 45, "low"))
    luna.add_task(Task("Play session", "18:00", 20, "medium"))  # same time as Mochi's walk
    mochi.add_task(Task("Vet appointment", "10:00", 60, "high", due_date=date.today() + timedelta(days=3)))
    return owner


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    today = date.today()
    print(f"🐾 PawPal+ for {owner.name} — {len(owner.pets)} pets, {owner.available_minutes} min available today")

    print_tasks("Tasks in the order they were added (unsorted)", scheduler.tasks_for_day())
    print_tasks("Today's Schedule — Scheduler.sort_by_time()", scheduler.todays_schedule())
    print_tasks(
        "By priority, then time — Scheduler.sort_by_priority()",
        scheduler.sort_by_priority(scheduler.tasks_for_day()),
    )
    print_tasks("Only Luna's tasks — Scheduler.filter_tasks(pet_name='Luna')", scheduler.filter_tasks(pet_name="Luna"))

    print("\nConflict check — Scheduler.detect_conflicts()")
    for warning in scheduler.detect_conflicts() or ["No conflicts."]:
        print(f"  {warning}")

    morning_walk = next(t for t in scheduler.tasks_for_day() if t.description == "Morning walk")
    upcoming = scheduler.mark_task_complete(morning_walk.id)
    print(f"\nMarked 'Morning walk' done — Scheduler.mark_task_complete()")
    print(f"  Next occurrence created for {upcoming.due_date.isoformat()} at {upcoming.time}")
    print_tasks("Still to do — Scheduler.filter_tasks(completed=False)", scheduler.sort_by_time(scheduler.filter_tasks(completed=False)))

    slot = scheduler.next_available_slot(75)
    print(f"\nNext free 75-minute slot today — Scheduler.next_available_slot(): {slot}")

    plan = scheduler.generate_plan(today)
    print(f"\nDaily plan — Scheduler.generate_plan() ({plan.minutes_used}/{plan.budget_minutes} min used)")
    for entry in plan.scheduled:
        t = entry.task
        print(f"  {t.time}  {task_emoji(t.description)} {t.pet_name}: {t.description} ({t.duration_minutes} min) — {entry.reason}")
    for entry in plan.skipped:
        t = entry.task
        print(f"  SKIPPED  {t.pet_name}: {t.description} — {entry.reason}")


if __name__ == "__main__":
    main()
