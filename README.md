# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

This project now includes several scheduling improvements:

- Time-aware sorting to order tasks by scheduled or due time.
- Filtering utilities by pet, status, and OR-based status-or-pet-name logic.
- Recurrence automation: completing daily/weekly tasks can create the next instance automatically.
- Basic conflict detection for overlapping timed tasks.
- Priority-aware schedule building with time-budget fitting and human-readable explanations.

These updates make daily plans more realistic while keeping the logic explainable and easy to test.

## Testing PawPal+

As I built PawPal+, I used tests as a safety net to make sure new scheduling features did what I expected and did not break earlier behavior.

Run tests from the project root with:

```bash
python -m pytest
```

Right now, the suite checks the most important day-to-day behaviors, including:

- Task state transitions (pending to complete)
- Adding tasks to pets and validating ownership relationships
- Sorting tasks by time
- Filtering tasks by pet, status, and status-or-pet-name logic
- Recurrence rule behavior for daily and weekly scheduling
- Conflict detection for overlapping timed tasks
- Recurring rollover when completing daily and weekly tasks

Confidence Level: ★★★★☆ (4/5)

Why this rating: I feel good about the core reliability because the main scheduling paths are covered and passing. There is still one meaningful edge-case discussion around weekly rollover cadence (should the next task be based on completion date or original due date). Once that policy is finalized and tested, confidence would move closer to 5/5.
