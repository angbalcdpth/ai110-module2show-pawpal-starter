"""Automated tests for core PawPal+ behaviors."""

import pytest
from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task


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
