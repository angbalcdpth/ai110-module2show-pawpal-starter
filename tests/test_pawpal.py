"""Automated tests for core PawPal+ behaviors."""

import pytest
from datetime import date, datetime, time, timedelta

from pawpal_system import Owner, Pet, RecurrenceRule, Scheduler, Task


def make_task(task_id: str = "task-1", pet_id: str = "pet-1", priority: str = "medium") -> Task:
    return Task(
        task_id=task_id,
        pet_id=pet_id,
        title="Test task",
        category="walk",
        duration_minutes=20,
        priority=priority,
        frequency="daily",
        due_time=datetime.combine(date.today(), time(8, 0)),
        recurring=True,
    )


def make_pet(pet_id: str = "pet-1") -> Pet:
    return Pet(pet_id=pet_id, name="Mochi", species="dog", age=4)


# ---------------------------------------------------------------------------
# Test 1: Task completion changes status
# ---------------------------------------------------------------------------

def test_mark_complete_sets_status():
    task = make_task()
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "complete"


# ---------------------------------------------------------------------------
# Test 2: Adding a task to a Pet increases the pet's task count
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


def test_sort_tasks_by_time_orders_chronologically():
    scheduler = Scheduler()
    early = make_task(task_id="task-early")
    late = make_task(task_id="task-late")

    early.scheduled_start = datetime.combine(date.today(), time(7, 30))
    late.scheduled_start = datetime.combine(date.today(), time(8, 30))

    ordered = scheduler.sort_tasks_by_time([late, early])
    assert [task.task_id for task in ordered] == ["task-early", "task-late"]


def test_filter_tasks_by_pet_and_status():
    scheduler = Scheduler()
    pending_task = make_task(task_id="task-pending", pet_id="pet-1")
    complete_task = make_task(task_id="task-complete", pet_id="pet-1")
    complete_task.mark_complete()
    other_pet_task = make_task(task_id="task-other-pet", pet_id="pet-2")

    filtered = scheduler.filter_tasks(
        [pending_task, complete_task, other_pet_task],
        pet_id="pet-1",
        allowed_statuses=["pending"],
    )
    assert [task.task_id for task in filtered] == ["task-pending"]


def test_recurrence_rule_weekly_active_day():
    today = date.today()
    rule = RecurrenceRule(
        frequency="weekly",
        interval=1,
        days_of_week=[today.strftime("%A")],
        start_date=today,
    )
    recurring_task = Task(
        task_id="task-weekly",
        pet_id="pet-1",
        title="Weekly grooming",
        category="grooming",
        duration_minutes=25,
        priority="medium",
        recurring=True,
        recurrence_rule=rule,
    )

    assert recurring_task.is_due_today(today)


def test_detect_basic_conflicts_finds_overlap():
    scheduler = Scheduler()
    walk = make_task(task_id="task-walk", priority="high")
    meds = make_task(task_id="task-meds", priority="high")

    walk.scheduled_start = datetime.combine(date.today(), time(8, 0))
    walk.duration_minutes = 30
    meds.scheduled_start = datetime.combine(date.today(), time(8, 15))
    meds.duration_minutes = 10

    conflicts = scheduler.detect_basic_conflicts([walk, meds])
    assert len(conflicts) == 1
    assert "conflicts with" in conflicts[0]


def test_filter_tasks_by_status_or_pet_name_uses_or_logic():
    scheduler = Scheduler()
    owner = Owner(owner_id="owner-1", name="Jordan", daily_time_available=90)
    mochi = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
    luna = Pet(pet_id="pet-2", name="Luna", species="cat", age=7)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    completed_mochi_task = make_task(task_id="task-complete", pet_id="pet-1")
    completed_mochi_task.mark_complete()
    pending_luna_task = make_task(task_id="task-luna", pet_id="pet-2")
    pending_mochi_task = make_task(task_id="task-other", pet_id="pet-1")

    filtered = scheduler.filter_tasks_by_status_or_pet_name(
        [completed_mochi_task, pending_luna_task, pending_mochi_task],
        owner,
        completion_status="complete",
        pet_name="Luna",
    )

    assert {task.task_id for task in filtered} == {"task-complete", "task-luna"}


def test_complete_daily_task_creates_next_day_instance():
    scheduler = Scheduler()
    owner = Owner(owner_id="owner-1", name="Jordan", daily_time_available=120)
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    daily_task = Task(
        task_id="daily-walk",
        pet_id="pet-1",
        title="Daily walk",
        category="walk",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        due_time=datetime.combine(date.today(), time(8, 0)),
        recurring=True,
        is_fixed_time=True,
        scheduled_start=datetime.combine(date.today(), time(8, 0)),
    )
    pet.add_task(daily_task)

    completed_at = datetime.combine(date.today(), time(9, 30))
    next_task = scheduler.complete_task_and_generate_next(owner, daily_task, completed_at)

    assert daily_task.status == "complete"
    assert next_task is not None
    assert next_task.due_time is not None
    assert next_task.due_time.date() == completed_at.date() + timedelta(days=1)
    assert next_task.status == "pending"
    assert next_task in pet.get_tasks()


def test_complete_weekly_task_creates_next_week_instance():
    scheduler = Scheduler()
    owner = Owner(owner_id="owner-1", name="Jordan", daily_time_available=120)
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", age=4)
    owner.add_pet(pet)

    weekly_task = Task(
        task_id="weekly-grooming",
        pet_id="pet-1",
        title="Weekly grooming",
        category="grooming",
        duration_minutes=25,
        priority="medium",
        frequency="weekly",
        due_time=datetime.combine(date.today(), time(10, 0)),
        recurring=True,
    )
    pet.add_task(weekly_task)

    completed_at = datetime.combine(date.today(), time(10, 45))
    next_task = scheduler.complete_task_and_generate_next(owner, weekly_task, completed_at)

    assert weekly_task.status == "complete"
    assert next_task is not None
    assert next_task.due_time is not None
    assert next_task.due_time.date() == completed_at.date() + timedelta(days=7)
