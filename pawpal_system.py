"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path

PRIORITIES = ("low", "medium", "high")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = ("once", "daily", "weekly")
RECURRENCE_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _new_id() -> str:
    """Return a short random id for a task."""
    return uuid.uuid4().hex[:8]


def to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes after midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def to_hhmm(minutes: int) -> str:
    """Convert minutes after midnight to an "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


TASK_EMOJI = {
    "walk": "🦮",
    "feed": "🍖",
    "breakfast": "🍖",
    "dinner": "🍖",
    "med": "💊",
    "pill": "💊",
    "vet": "🩺",
    "appointment": "🩺",
    "groom": "🧼",
    "bath": "🛁",
    "play": "🎾",
}
PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}


def task_emoji(description: str) -> str:
    """Pick an emoji for a task from keywords in its description."""
    text = description.lower()
    return next((icon for word, icon in TASK_EMOJI.items() if word in text), "🐾")


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

    @property
    def start_minutes(self) -> int:
        """Minutes after midnight when this task starts."""
        return to_minutes(self.time)

    @property
    def end_minutes(self) -> int:
        """Minutes after midnight when this task ends."""
        return self.start_minutes + self.duration_minutes

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy of this task for its next due date, or None if it doesn't repeat."""
        step = RECURRENCE_STEP.get(self.frequency)
        if step is None:
            return None
        return Task(
            description=self.description,
            time=self.time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=self.due_date + step,
            pet_name=self.pet_name,
        )

    def to_dict(self) -> dict:
        """Return a JSON-safe dict of this task."""
        data = asdict(self)
        data["due_date"] = self.due_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Build a task from a dict produced by to_dict()."""
        data = dict(data)
        data["due_date"] = date.fromisoformat(data["due_date"])
        return cls(**data)


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

    def to_dict(self) -> dict:
        """Return a JSON-safe dict of this pet and its tasks."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Build a pet (and its tasks) from a dict produced by to_dict()."""
        pet = cls(data["name"], data["species"], data.get("age", 0))
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


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

    def to_dict(self) -> dict:
        """Return a JSON-safe dict of this owner, their pets, and tasks."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Build an owner from a dict produced by to_dict()."""
        owner = cls(data["name"], data.get("available_minutes", 120))
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Write this owner, their pets, and all tasks to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> Owner | None:
        """Load an owner from a JSON file; return None if the file doesn't exist."""
        path = Path(path)
        if not path.exists():
            return None
        return cls.from_dict(json.loads(path.read_text()))


@dataclass
class PlanEntry:
    """One task in a daily plan, with the reason it was included or skipped."""

    task: Task
    reason: str


@dataclass
class DailyPlan:
    """The result of Scheduler.generate_plan(): what fits today and what doesn't."""

    day: date
    budget_minutes: int
    scheduled: list[PlanEntry] = field(default_factory=list)
    skipped: list[PlanEntry] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    @property
    def minutes_used(self) -> int:
        """Total minutes of the tasks that made it into the plan."""
        return sum(e.task.duration_minutes for e in self.scheduled)


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler that works on the given owner's pets."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return every task the owner's pets have."""
        return self.owner.get_all_tasks()

    def find_task(self, task_id: str) -> Task | None:
        """Return the task with the given id from any pet, or None."""
        return next((t for t in self.get_all_tasks() if t.id == task_id), None)

    def tasks_for_day(self, day: date | None = None) -> list[Task]:
        """Return the tasks due on the given day (default: today)."""
        day = day or date.today()
        return [t for t in self.get_all_tasks() if t.due_date == day]

    # --- Sorting -----------------------------------------------------------

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks in chronological order (by date, then "HH:MM" time).

        Zero-padded "HH:MM" strings sort correctly as plain strings, so the
        time can be used directly as the sort key.
        """
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered high → low priority, breaking ties by time."""
        return sorted(tasks, key=lambda t: (PRIORITY_RANK[t.priority], t.due_date, t.time))

    def todays_schedule(self, day: date | None = None) -> list[Task]:
        """Return the given day's tasks in time order."""
        return self.sort_by_time(self.tasks_for_day(day))

    # --- Filtering ---------------------------------------------------------

    def filter_tasks(
        self,
        tasks: list[Task] | None = None,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks matching a pet name and/or completion status.

        A filter left as None is not applied. With no task list given, all of
        the owner's tasks are filtered.
        """
        tasks = self.get_all_tasks() if tasks is None else tasks
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    # --- Recurring tasks ---------------------------------------------------

    def mark_task_complete(self, task_id: str) -> Task | None:
        """Mark a task complete; for daily/weekly tasks, add and return the next occurrence.

        Returns None when the task doesn't exist, doesn't repeat, or was
        already complete (so double-clicking "done" can't create duplicates).
        """
        task = self.find_task(task_id)
        if task is None or task.completed:
            return None
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            pet = self.owner.get_pet(task.pet_name)
            pet.add_task(upcoming)
        return upcoming

    # --- Conflict detection ------------------------------------------------

    def detect_conflicts(self, day: date | None = None) -> list[str]:
        """Return a warning for each pair of unfinished tasks whose times overlap on a day.

        Two tasks conflict when one starts before the other ends. Tasks are
        sorted by start time so each task is only compared against the ones
        that start before it finishes. Never raises; an empty list means no
        conflicts.
        """
        tasks = [t for t in self.todays_schedule(day) if not t.completed]
        warnings = []
        for i, first in enumerate(tasks):
            for second in tasks[i + 1:]:
                if second.start_minutes >= first.end_minutes:
                    break
                who = (
                    f"both for {first.pet_name}"
                    if first.pet_name == second.pet_name
                    else f"{first.pet_name} and {second.pet_name}"
                )
                warnings.append(
                    f"⚠ Conflict at {second.time}: '{first.description}' "
                    f"({first.time}–{to_hhmm(first.end_minutes)}) overlaps "
                    f"'{second.description}' ({second.time}–{to_hhmm(second.end_minutes)}), {who}"
                )
        return warnings

    # --- Next available slot -----------------------------------------------

    def next_available_slot(
        self,
        duration_minutes: int,
        day: date | None = None,
        earliest: str = "07:00",
        latest: str = "22:00",
    ) -> str | None:
        """Return the earliest "HH:MM" start where a task of this length fits without overlap.

        Searches the gaps between the day's unfinished tasks inside the
        earliest–latest window; returns None if nothing fits.
        """
        cursor = to_minutes(earliest)
        end_of_day = to_minutes(latest)
        busy = [t for t in self.todays_schedule(day) if not t.completed]
        for task in busy:
            if task.start_minutes - cursor >= duration_minutes:
                break
            cursor = max(cursor, task.end_minutes)
        if cursor + duration_minutes <= end_of_day:
            return to_hhmm(cursor)
        return None

    # --- Daily plan --------------------------------------------------------

    def generate_plan(self, day: date | None = None) -> DailyPlan:
        """Choose which of a day's tasks fit in the owner's time budget and explain why.

        Unfinished tasks are considered highest priority first (earlier time
        breaks ties) and added while they fit in owner.available_minutes. The
        chosen tasks are returned in time order; the rest are listed as skipped.
        """
        day = day or date.today()
        plan = DailyPlan(day=day, budget_minutes=self.owner.available_minutes)
        remaining = self.owner.available_minutes
        pending = self.filter_tasks(self.tasks_for_day(day), completed=False)
        for task in self.sort_by_priority(pending):
            if task.duration_minutes <= remaining:
                remaining -= task.duration_minutes
                plan.scheduled.append(
                    PlanEntry(task, f"{task.priority} priority, fits ({remaining} min left after)")
                )
            else:
                plan.skipped.append(
                    PlanEntry(
                        task,
                        f"needs {task.duration_minutes} min but only {remaining} min left; "
                        f"higher-priority tasks came first",
                    )
                )
        plan.scheduled.sort(key=lambda e: e.task.time)
        plan.conflicts = self.detect_conflicts(day)
        return plan
