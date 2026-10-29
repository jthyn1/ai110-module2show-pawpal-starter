"""CLI demo for PawPal+: builds an owner with pets and prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(title: str, tasks: list[Task]) -> None:
    """Print tasks as an aligned, readable table."""
    print(f"\n{title}")
    print("-" * 60)
    if not tasks:
        print("  (no tasks)")
    for t in tasks:
        status = "x" if t.completed else " "
        print(
            f"  [{status}] {t.time}  {t.pet_name:<8} {t.description:<22} "
            f"{t.duration_minutes:>3} min  {t.priority}"
        )


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    mochi.add_task(Task("Evening walk", "18:00", 30, "medium", "daily"))
    luna.add_task(Task("Breakfast", "08:00", 5, "high", "daily"))
    luna.add_task(Task("Flea medication", "09:00", 5, "high", "weekly"))

    scheduler = Scheduler(owner)
    print(f"PawPal+ for {owner.name} ({len(owner.pets)} pets)")
    print_schedule("Today's Schedule", scheduler.todays_schedule())


if __name__ == "__main__":
    main()
