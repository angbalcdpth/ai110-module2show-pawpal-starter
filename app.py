import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task  # import classes here

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner Profile")
# Streamlit reruns top-to-bottom on every interaction, so keep core objects in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id="owner-session",
        name="Jordan",
        daily_time_available=120,
        preferences=[],
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(max_daily_minutes=120)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

owner_name = st.text_input("Owner name", value=owner.name)
daily_time_available = st.number_input(
    "Daily time available (minutes)",
    min_value=15,
    max_value=1440,
    value=owner.daily_time_available,
)
owner.name = owner_name
owner.daily_time_available = int(daily_time_available)

st.markdown("### Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    new_age = st.number_input("Age", min_value=0, max_value=40, value=1)
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not new_pet_name.strip():
        st.error("Please enter a pet name before submitting.")
    else:
        next_pet_id = f"pet-{len(owner.pets) + 1}"
        try:
            owner.add_pet(
                Pet(
                    pet_id=next_pet_id,
                    name=new_pet_name.strip(),
                    species=new_species,
                    age=int(new_age),
                )
            )
            st.success(f"Added pet {new_pet_name.strip()} to {owner.name}'s profile.")
        except ValueError as exc:
            st.error(f"Could not add pet: {exc}")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "age": pet.age,
                "task_count": len(pet.tasks),
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Use the form above to add one.")

st.markdown("### Schedule a Task")
if not owner.pets:
    st.info("Add a pet first to start scheduling tasks.")
else:
    pet_id_options = [pet.pet_id for pet in owner.pets]
    selected_pet_id = st.selectbox(
        "Pet",
        pet_id_options,
        format_func=lambda pet_id: next(
            pet.name for pet in owner.pets if pet.pet_id == pet_id
        ),
    )
    selected_pet = next(pet for pet in owner.pets if pet.pet_id == selected_pet_id)

    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input("Task title")
        category = st.text_input("Category", value="general")
        duration = st.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=240,
            value=20,
        )
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recurring = st.checkbox("Recurring daily", value=True)
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        if not task_title.strip():
            st.error("Please enter a task title before submitting.")
        else:
            task_count = len(selected_pet.get_tasks()) + 1
            selected_pet.add_task(
                Task(
                    task_id=f"{selected_pet.pet_id}-task-{task_count}",
                    pet_id=selected_pet.pet_id,
                    title=task_title.strip(),
                    category=category.strip() or "general",
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency="daily" if recurring else "once",
                    recurring=recurring,
                )
            )
            st.success(f"Added task '{task_title.strip()}' for {selected_pet.name}.")

    current_tasks = selected_pet.get_tasks()
    if current_tasks:
        st.write("Tasks for selected pet:")
        st.table(
            [
                {
                    "title": task.title,
                    "category": task.category,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                }
                for task in current_tasks
            ]
        )
    else:
        st.info("No tasks yet for this pet.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate today's schedule using your Scheduler class.")

if st.button("Generate schedule"):
    schedule = scheduler.build_daily_schedule(owner, date.today())

    if not schedule.tasks_ordered:
        st.info("No tasks could be scheduled for today.")
    else:
        st.success(schedule.summarize())
        st.table(
            [
                {
                    "task": task.title,
                    "priority": task.priority,
                    "duration_minutes": task.duration_minutes,
                }
                for task in schedule.tasks_ordered
            ]
        )

    if schedule.skipped_tasks:
        st.warning(
            "Skipped tasks: "
            + ", ".join(task.title for task in schedule.skipped_tasks)
        )
