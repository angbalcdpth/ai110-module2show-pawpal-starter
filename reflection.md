# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

1. Add and manage a pet profile so care tasks are tied to the right pet.
2. Create and schedule care tasks (walks, feeding, medication, appointments) with duration and priority.
3. View today’s prioritized task list to see what to do now and what comes next.

**b. Design changes**

Yes. After reviewing the class skeleton, I made three design changes. I connected `Appointment` more clearly to `Pet` by adding appointment-related attributes and method stubs, because appointments were originally defined as a separate object without a strong relationship to the rest of the model. I also added a `scheduled_start` field to `Task` so conflict detection has a clear time to compare, instead of relying only on a due time. Finally, I simplified the scheduler interface so it builds a daily schedule from the `Owner` object instead of taking separate owner, pet, and task inputs, which reduces duplicate data flow and makes the design easier to maintain.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
