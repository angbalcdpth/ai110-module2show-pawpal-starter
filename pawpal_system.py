"""Core backend models and scheduling logic for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional


PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class RecurrenceRule:
    frequency: str
    interval: int = 1
    days_of_week: list[str] = field(default_factory=list)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def generate_occurrences(self, start: date, end: date) -> list[date]:
        """Return all dates this rule fires between start and end (inclusive)."""
        raise NotImplementedError

    def is_active_on(self, target_date: date) -> bool:
        """Return True if this recurrence rule applies on target_date."""
        raise NotImplementedError


@dataclass
class Task:
    task_id: str
    pet_id: str
    title: str
    category: str
    duration_minutes: int
    priority: str
    description: str = ""
    frequency: str = "once"
    due_time: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    recurring: bool = False
    recurrence_rule: Optional[RecurrenceRule] = None
    is_fixed_time: bool = False
    status: str = "pending"

    def __post_init__(self) -> None:
        """Validate and normalize priority, frequency, and status after construction."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

        normalized_priority = self.priority.lower()
        if normalized_priority not in PRIORITY_RANK:
            raise ValueError("priority must be high, medium, or low")

        self.priority = normalized_priority
        self.frequency = self.frequency.lower()
        self.status = self.status.lower()

    def mark_complete(self) -> None:
        """Set task status to complete."""
        self.status = "complete"

    def mark_pending(self) -> None:
        """Reset task status to pending."""
        self.status = "pending"

    def reschedule(self, new_due_time: datetime) -> None:
        """Update due time and, if fixed, also update the scheduled start."""
        self.due_time = new_due_time
        if self.is_fixed_time:
            self.scheduled_start = new_due_time

    def is_due_today(self, target_date: date) -> bool:
        """Return True if this task should appear on the given date."""
        reference_time = self.scheduled_start or self.due_time
        if reference_time is not None:
            return reference_time.date() == target_date

        if self.recurring:
            if self.frequency == "daily":
                return True
            if self.frequency == "weekly" and self.due_time is not None:
                return self.due_time.weekday() == target_date.weekday()

        return False

    def conflicts_with(self, other_task: Task) -> bool:
        """Return True if this task's time window overlaps with other_task's."""
        start_time = self.scheduled_start or self.due_time
        other_start = other_task.scheduled_start or other_task.due_time

        if start_time is None or other_start is None:
            return False

        end_time = start_time + timedelta(minutes=self.duration_minutes)
        other_end = other_start + timedelta(minutes=other_task.duration_minutes)
        return start_time < other_end and other_start < end_time


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
        """Convert this appointment into a fixed-time Task for scheduling."""
        raise NotImplementedError

    def overlaps_with(self, task: Task) -> bool:
        """Return True if this appointment's time window overlaps with task."""
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
    appointments: list[Appointment] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet, enforcing pet_id ownership."""
        if task.pet_id != self.pet_id:
            raise ValueError("task.pet_id must match the pet receiving the task")

        self.tasks.append(task)

    def add_appointment(self, appointment: Appointment) -> None:
        """Append an appointment to this pet, enforcing pet_id ownership."""
        if appointment.pet_id != self.pet_id:
            raise ValueError("appointment.pet_id must match the pet receiving the appointment")

        self.appointments.append(appointment)

    def get_tasks(self) -> list[Task]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)

    def get_appointments(self) -> list[Appointment]:
        """Return a shallow copy of this pet's appointment list."""
        return list(self.appointments)

    def update_profile(self, **changes: object) -> None:
        """Update any writable pet attribute by keyword argument."""
        for field_name, value in changes.items():
            if hasattr(self, field_name):
                setattr(self, field_name, value)

    def get_special_care_flags(self) -> list[str]:
        """Return labels for age, medical, or custom-routine care needs."""
        flags: list[str] = []

        if self.age <= 1:
            flags.append("young_pet")
        elif self.age >= 10:
            flags.append("senior_pet")

        if self.medical_notes.strip():
            flags.append("medical_care")

        if self.routine_preferences:
            flags.append("custom_routine")

        return flags


@dataclass
class Owner:
    owner_id: str
    name: str
    daily_time_available: int
    preferences: list[str] = field(default_factory=list)
    contact_info: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner, rejecting duplicate pet_ids."""
        if any(existing_pet.pet_id == pet.pet_id for existing_pet in self.pets):
            raise ValueError("pet_id must be unique per owner")

        self.pets.append(pet)

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's preference list with a new one."""
        self.preferences = list(preferences)

    def get_available_time(self) -> int:
        """Return the owner's total available minutes for the day."""
        return self.daily_time_available

    def get_all_tasks(self) -> list[Task]:
        """Aggregate and return tasks from all pets owned by this owner."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_all_appointments(self) -> list[Appointment]:
        """Aggregate and return appointments from all pets owned by this owner."""
        appointments: list[Appointment] = []
        for pet in self.pets:
            appointments.extend(pet.get_appointments())
        return appointments

    def view_todays_plan(self, scheduler: Scheduler, target_date: date) -> Schedule:
        """Delegate to the scheduler to build and return today's schedule."""
        return scheduler.build_daily_schedule(self, target_date)


@dataclass
class Schedule:
    date: date
    owner_id: str
    tasks_ordered: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    conflicts: list[str] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    explanation_log: list[str] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to the schedule and accumulate its duration."""
        self.tasks_ordered.append(task)
        self.total_minutes += task.duration_minutes

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule and deduct its duration."""
        if task in self.tasks_ordered:
            self.tasks_ordered.remove(task)
            self.total_minutes -= task.duration_minutes

    def sort_by_priority_and_time(self) -> None:
        """Sort tasks in-place: fixed-time first, then priority rank, then start time."""
        self.tasks_ordered.sort(
            key=lambda task: (
                not task.is_fixed_time,
                PRIORITY_RANK.get(task.priority, len(PRIORITY_RANK)),
                task.scheduled_start or task.due_time or datetime.max,
                task.duration_minutes,
            )
        )

    def detect_conflicts(self) -> list[str]:
        """Check all task pairs for time overlaps and update self.conflicts."""
        conflicts: list[str] = []
        for index, current_task in enumerate(self.tasks_ordered):
            for comparison_task in self.tasks_ordered[index + 1 :]:
                if current_task.conflicts_with(comparison_task):
                    conflicts.append(
                        f"{current_task.title} conflicts with {comparison_task.title}"
                    )

        self.conflicts = conflicts
        return conflicts

    def summarize(self) -> str:
        """Return a one-line human-readable summary of the scheduled tasks."""
        if not self.tasks_ordered:
            return "No tasks scheduled for today."

        task_titles = ", ".join(task.title for task in self.tasks_ordered)
        return (
            f"Scheduled {len(self.tasks_ordered)} task(s) totaling "
            f"{self.total_minutes} minutes: {task_titles}."
        )


@dataclass
class Scheduler:
    rules: list[str] = field(default_factory=list)
    max_daily_minutes: Optional[int] = None
    prioritization_strategy: str = "priority_then_time"

    def build_daily_schedule(self, owner: Owner, target_date: date) -> Schedule:
        """Collect, prioritize, de-conflict, and fit tasks into a daily Schedule."""
        available_minutes = self.max_daily_minutes or owner.get_available_time()
        candidate_tasks = [
            task
            for task in owner.get_all_tasks()
            if task.status != "complete" and task.is_due_today(target_date)
        ]

        candidate_tasks.extend(
            Task(
                task_id=f"appointment-{appointment.appointment_id}",
                pet_id=appointment.pet_id,
                title=appointment.title,
                category="appointment",
                duration_minutes=appointment.duration_minutes,
                priority="high",
                description=appointment.notes,
                frequency="once",
                due_time=appointment.start_time,
                scheduled_start=appointment.start_time,
                is_fixed_time=appointment.is_fixed_time,
            )
            for appointment in owner.get_all_appointments()
            if appointment.start_time.date() == target_date
        )

        prioritized_tasks = self.prioritize_tasks(candidate_tasks)
        conflict_free_tasks, conflicts = self.resolve_conflicts(prioritized_tasks)
        scheduled_tasks, skipped_tasks = self.fit_tasks_to_time_budget(
            conflict_free_tasks, available_minutes
        )

        schedule = Schedule(date=target_date, owner_id=owner.owner_id)
        for task in scheduled_tasks:
            schedule.add_task(task)

        schedule.skipped_tasks = skipped_tasks
        schedule.explanation_log = self.explain_decisions(scheduled_tasks, skipped_tasks)
        schedule.detect_conflicts()
        schedule.conflicts.extend(
            message for message in conflicts if message not in schedule.conflicts
        )
        schedule.sort_by_priority_and_time()
        return schedule

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by fixed-time flag, priority, start time, then duration."""
        return sorted(
            tasks,
            key=lambda task: (
                not task.is_fixed_time,
                PRIORITY_RANK.get(task.priority, len(PRIORITY_RANK)),
                task.scheduled_start or task.due_time or datetime.max,
                task.duration_minutes,
            ),
        )

    def resolve_conflicts(self, tasks: list[Task]) -> tuple[list[Task], list[str]]:
        """Drop tasks that overlap an already-accepted task; return accepted list and conflict messages."""
        accepted_tasks: list[Task] = []
        conflicts: list[str] = []

        for task in tasks:
            conflicting_task = next(
                (scheduled_task for scheduled_task in accepted_tasks if task.conflicts_with(scheduled_task)),
                None,
            )
            if conflicting_task is None:
                accepted_tasks.append(task)
                continue

            conflicts.append(
                f"Skipped {task.title} because it overlaps with {conflicting_task.title}."
            )

        return accepted_tasks, conflicts

    def fit_tasks_to_time_budget(
        self, tasks: list[Task], available_minutes: int
    ) -> tuple[list[Task], list[Task]]:
        """Greedily fill the time budget; overflow tasks go to the skipped list."""
        scheduled_tasks: list[Task] = []
        skipped_tasks: list[Task] = []
        used_minutes = 0

        for task in tasks:
            if used_minutes + task.duration_minutes <= available_minutes:
                scheduled_tasks.append(task)
                used_minutes += task.duration_minutes
            else:
                skipped_tasks.append(task)

        return scheduled_tasks, skipped_tasks

    def explain_decisions(self, scheduled: list[Task], skipped: list[Task]) -> list[str]:
        """Return plain-English explanations for why each task was scheduled or skipped."""
        explanations = [
            f"Scheduled {task.title} because it matched today's plan and fit the priority order."
            for task in scheduled
        ]

        explanations.extend(
            f"Skipped {task.title} because there was not enough time remaining in the day."
            for task in skipped
        )
        return explanations