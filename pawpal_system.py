"""Skeleton backend models for the PawPal+ logic layer.

This module translates the UML design into dataclass-based Python class stubs.
Attributes are defined, but method bodies are intentionally left unimplemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class RecurrenceRule:
    frequency: str
    interval: int = 1
    days_of_week: list[str] = field(default_factory=list)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def generate_occurrences(self, start: date, end: date) -> list[date]:
        raise NotImplementedError

    def is_active_on(self, target_date: date) -> bool:
        raise NotImplementedError


@dataclass
class Task:
    task_id: str
    pet_id: str
    title: str
    category: str
    duration_minutes: int
    priority: str
    due_time: Optional[datetime] = None
    recurring: bool = False
    recurrence_rule: Optional[RecurrenceRule] = None
    status: str = "pending"

    def mark_complete(self) -> None:
        raise NotImplementedError

    def mark_pending(self) -> None:
        raise NotImplementedError

    def reschedule(self, new_due_time: datetime) -> None:
        raise NotImplementedError

    def is_due_today(self, target_date: date) -> bool:
        raise NotImplementedError

    def conflicts_with(self, other_task: Task) -> bool:
        raise NotImplementedError


@dataclass
class Appointment:
    appointment_id: str
    pet_id: str
    title: str
    start_time: datetime
    duration_minutes: int
    location: str = ""
    notes: str = ""
    is_fixed_time: bool = True

    def to_task(self) -> Task:
        raise NotImplementedError

    def overlaps_with(self, task: Task) -> bool:
        raise NotImplementedError


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    weight: float = 0.0
    medical_notes: str = ""
    routine_preferences: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        raise NotImplementedError

    def update_profile(self, **changes: object) -> None:
        raise NotImplementedError

    def get_special_care_flags(self) -> list[str]:
        raise NotImplementedError


@dataclass
class Owner:
    owner_id: str
    name: str
    daily_time_available: int
    preferences: list[str] = field(default_factory=list)
    contact_info: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def update_preferences(self, preferences: list[str]) -> None:
        raise NotImplementedError

    def get_available_time(self) -> int:
        raise NotImplementedError

    def view_todays_plan(self, scheduler: Scheduler, target_date: date) -> Schedule:
        raise NotImplementedError


@dataclass
class Schedule:
    date: date
    tasks_ordered: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    conflicts: list[str] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    explanation_log: list[str] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        raise NotImplementedError

    def sort_by_priority_and_time(self) -> None:
        raise NotImplementedError

    def detect_conflicts(self) -> list[str]:
        raise NotImplementedError

    def summarize(self) -> str:
        raise NotImplementedError


@dataclass
class Scheduler:
    rules: list[str] = field(default_factory=list)
    max_daily_minutes: Optional[int] = None
    prioritization_strategy: str = "priority_then_time"

    def build_daily_schedule(
        self, owner: Owner, pets: list[Pet], tasks: list[Task], target_date: date
    ) -> Schedule:
        raise NotImplementedError

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def resolve_conflicts(self, tasks: list[Task]) -> tuple[list[Task], list[str]]:
        raise NotImplementedError

    def fit_tasks_to_time_budget(
        self, tasks: list[Task], available_minutes: int
    ) -> tuple[list[Task], list[Task]]:
        raise NotImplementedError

    def explain_decisions(self, scheduled: list[Task], skipped: list[Task]) -> list[str]:
        raise NotImplementedError