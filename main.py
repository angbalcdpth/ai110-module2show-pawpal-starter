from __future__ import annotations

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task


def today_at(hour: int, minute: int = 0) -> datetime:
    return datetime.combine(date.today(), time(hour=hour, minute=minute))


def build_demo_data() -> tuple[Owner, Scheduler]:
    owner = Owner(
        owner_id="owner-1",
        name="Jordan",
        daily_time_available=120,
        preferences=["morning_walks", "evening_feeding"],
    )

    mochi = Pet(
        pet_id="pet-1",
        name="Mochi",
        species="dog",
        age=4,
        weight=24.5,
    )
    luna = Pet(
        pet_id="pet-2",
        name="Luna",
        species="cat",
        age=7,
        weight=9.2,
        medical_notes="Needs medication with food.",
    )

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Intentionally added out of chronological order for sorting demos.
    mochi.add_task(
        Task(
            task_id="task-2",
            pet_id="pet-1",
            title="Dinner feeding",
            category="feeding",
            duration_minutes=15,
            priority="medium",
            description="Serve dry food and refill water bowl.",
            frequency="daily",
            due_time=today_at(18, 0),
            recurring=True,
        )
    )

    luna.add_task(
        Task(
            task_id="task-3",
            pet_id="pet-2",
            title="Medication",
            category="medication",
            duration_minutes=10,
            priority="high",
            description="Give thyroid medication with wet food.",
            frequency="daily",
            due_time=today_at(9, 0),
            scheduled_start=today_at(9, 0),
            recurring=True,
            is_fixed_time=True,
        )
    )

    mochi.add_task(
        Task(
            task_id="task-1",
            pet_id="pet-1",
            title="Morning walk",
            category="walk",
            duration_minutes=30,
            priority="high",
            description="Neighborhood walk before work.",
            frequency="daily",
            due_time=today_at(8, 0),
            scheduled_start=today_at(8, 0),
            recurring=True,
            is_fixed_time=True,
        )
    )

    completed_cleanup = Task(
        task_id="task-4",
        pet_id="pet-1",
        title="Backyard cleanup",
        category="housekeeping",
        duration_minutes=12,
        priority="low",
        description="Pick up and sanitize the yard area.",
        frequency="daily",
        due_time=today_at(7, 15),
        scheduled_start=today_at(7, 15),
        recurring=True,
    )
    completed_cleanup.mark_complete()
    mochi.add_task(completed_cleanup)

    scheduler = Scheduler(max_daily_minutes=120)
    return owner, scheduler


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
    schedule = scheduler.build_daily_schedule(owner, date.today())

    print("Today's Schedule")
    print("=" * 16)
    print(f"Owner: {owner.name}")
    print()

    if not schedule.tasks_ordered:
        print("No tasks scheduled for today.")
        return

    for task in schedule.tasks_ordered:
        time_label = task.scheduled_start or task.due_time
        display_time = time_label.strftime("%I:%M %p") if time_label else "Flexible"
        print(
            f"- {display_time}: {task.title} "
            f"({task.category}, {task.priority} priority, {task.duration_minutes} min)"
        )

    if schedule.skipped_tasks:
        print()
        print("Skipped Tasks")
        print("-" * 13)
        for task in schedule.skipped_tasks:
            print(f"- {task.title}")

    if schedule.conflicts:
        print()
        print("Conflicts")
        print("-" * 9)
        for conflict in schedule.conflicts:
            print(f"- {conflict}")

    print()
    print(schedule.summarize())


def print_algorithm_demo(owner: Owner, scheduler: Scheduler) -> None:
    """Show helper algorithms for sorting, filtering, recurring handling, and conflicts."""
    todays_tasks = [task for task in owner.get_all_tasks() if task.is_due_today(date.today())]
    pending_for_mochi = scheduler.filter_tasks(
        todays_tasks,
        pet_id="pet-1",
        allowed_statuses=["pending"],
    )

    print()
    print("Algorithm Demo")
    print("=" * 14)
    print(f"Today's due tasks: {len(todays_tasks)}")
    print(f"Pending tasks for Mochi: {len(pending_for_mochi)}")

    pet_name_by_id = {pet.pet_id: pet.name for pet in owner.pets}

    print("\nAs added (out of order):")
    for task in todays_tasks:
        task_time = task.scheduled_start or task.due_time
        display_time = task_time.strftime("%I:%M %p") if task_time else "Flexible"
        pet_name = pet_name_by_id.get(task.pet_id, task.pet_id)
        print(f"- {display_time}: {task.title} [{pet_name}] ({task.status})")

    ordered_by_time = scheduler.sort_by_time(todays_tasks)
    print("\nSorted by time:")
    for task in ordered_by_time:
        task_time = task.scheduled_start or task.due_time
        display_time = task_time.strftime("%I:%M %p") if task_time else "Flexible"
        pet_name = pet_name_by_id.get(task.pet_id, task.pet_id)
        print(f"- {display_time}: {task.title} [{pet_name}] ({task.status})")

    complete_or_luna = scheduler.filter_tasks_by_status_or_pet_name(
        ordered_by_time,
        owner,
        completion_status="complete",
        pet_name="Luna",
    )
    print("\nFiltered (status=complete OR pet_name=Luna):")
    for task in complete_or_luna:
        task_time = task.scheduled_start or task.due_time
        display_time = task_time.strftime("%I:%M %p") if task_time else "Flexible"
        pet_name = pet_name_by_id.get(task.pet_id, task.pet_id)
        print(f"- {display_time}: {task.title} [{pet_name}] ({task.status})")

    conflicts = scheduler.detect_basic_conflicts(ordered_by_time)
    if conflicts:
        print("\nBasic conflicts:")
        for conflict in conflicts:
            print(f"- {conflict}")
    else:
        print("\nBasic conflicts: none")


if __name__ == "__main__":
    demo_owner, demo_scheduler = build_demo_data()
    print_schedule(demo_owner, demo_scheduler)
    print_algorithm_demo(demo_owner, demo_scheduler)