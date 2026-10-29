"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date

PRIORITIES = ("low", "medium", "high")
FREQUENCIES = ("once", "daily", "weekly")


def _new_id() -> str:
    """Return a short random id for a task."""
    return uuid.uuid4().hex[:8]


@dataclass
class Task:
    """A single pet care activity scheduled at a time on a given day."""

    description: str
    time: str  # "HH:MM", 24-hour
    duration_minutes: int = 15
    priority: str = "medium"  # low | medium | high
    frequency: str = "once"  # once | daily | weekly
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""
    id: str = field(default_factory=_new_id)

    def __post_init__(self) -> None:
        """Validate the time, priority, and frequency fields."""
        hours, minutes = self.time.split(":")
        if not (0 <= int(hours) < 24 and 0 <= int(minutes) < 60):
            raise ValueError(f"Invalid time {self.time!r}; expected HH:MM")
        self.time = f"{int(hours):02d}:{int(minutes):02d}"
        if self.priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"Frequency must be one of {FREQUENCIES}")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove the task with the given id; return True if one was removed."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        return len(self.tasks) < before

    def get_task(self, task_id: str) -> Task | None:
        """Return this pet's task with the given id, or None."""
        return next((t for t in self.tasks if t.id == task_id), None)


class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str, available_minutes: int = 120):
        """Create an owner with a daily time budget for pet care."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet; pet names must be unique for this owner."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name}")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return the pet with the given name (case-insensitive), or None."""
        return next((p for p in self.pets if p.name.lower() == name.lower()), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler that works on the given owner's pets."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return every task the owner's pets have."""
        return self.owner.get_all_tasks()

    def tasks_for_day(self, day: date | None = None) -> list[Task]:
        """Return the tasks due on the given day (default: today)."""
        day = day or date.today()
        return [t for t in self.get_all_tasks() if t.due_date == day]

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks ordered by their time of day."""
        return sorted(tasks, key=lambda t: t.time)

    def todays_schedule(self, day: date | None = None) -> list[Task]:
        """Return the given day's tasks in time order."""
        return self.sort_by_time(self.tasks_for_day(day))

    def mark_task_complete(self, task_id: str) -> Task | None:
        """Mark the task with the given id complete and return it."""
        task = next((t for t in self.get_all_tasks() if t.id == task_id), None)
        if task is not None:
            task.mark_complete()
        return task
