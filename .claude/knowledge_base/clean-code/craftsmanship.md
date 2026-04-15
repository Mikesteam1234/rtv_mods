# Craftsmanship

*From chapters 28–37 — the final part of the book, framed around "The Programmer's Oath."*

The book ends with a professional-ethics framing: what it means to be a software professional, not just a productive coder. The chapters are short and each centers on one commitment.

## 1. Harm (Ch 28)

**You must KNOW that your code won't harm.**

Two real examples from the book:
- **Knight Capital, 2012.** A repurposed feature flag activated 8-year-old dead code that made trades in an infinite loop. $460M loss in 45 minutes; the firm was bankrupt. The root cause: programmers didn't KNOW what their system would do, because they left defunct code in the system.
- **Toyota unintended acceleration.** As many as 89 people killed. Contributing factors included thousands of global variables — structural rot so severe that no one could know what the software would do.

Two forms of harm:

- **Harm to function.** Code that does the wrong thing. Perfect knowledge is impossible, but when stakes are high you drive as close as you can. Don't assume your app is too small to do harm — a dropped chat message in a medical emergency, a leaked password, lost customer confidence, all count.
- **Harm to structure.** Code that can't be safely changed. Messy structure is *why* people can't know what the code does. **Messy software is harmful software.**

Quick-and-dirty patches to save a production outage are fine — *but leaving them in* causes ongoing harm. Remove the patch and replace it with the proper fix.

## 2. No Defect in Behavior or Structure (Ch 29)

> "First, make it work. Then, make it right."

Too many programmers think they're done once the tests pass. They leave tangled, unreadable code behind and move on. This is the single biggest cause of long-term team slowdown.

- Finishing means: works *and* is clean.
- Your value is not in speed. Speed without cleanliness *destroys* future speed.
- "Not knowingly allowing code that is defective either in behavior or in structure to accumulate."

## 3. Repeatable Proof (Ch 30)

You must be able to *prove* — automatically, repeatably — that your code works. A manual demonstration is not proof; it is anecdote.

- A trustworthy test suite is the proof.
- Tests must be fast, independent, repeatable, self-validating, timely (F.I.R.S.T., see [`testing.md`](testing.md)).
- "Works on my machine" is not proof.

## 4. Small Cycles (Ch 31)

Work in cycles measured in *minutes*, not days.

- Small commits, often. `git reset` should never lose more than a few minutes of work.
- Continuous integration means every developer integrates with the main branch many times per day.
- Feature branches that live for weeks are a process smell.

The smaller the cycle, the smaller the blast radius when something goes wrong.

## 5. Relentless Improvement (Ch 32)

Leave the code better than you found it (**Boy Scout Rule**, reprised).

- Every commit: one small kindness.
- Refactoring is not a phase; it's continuous, in every commit.
- Don't wait for a "rewrite from scratch" — it never arrives, and if it does, it fails (Xeno's Paradox: the rewrite team never catches up to the maintenance team).

## 6. Maintain High Productivity (Ch 33)

Productivity is a function of **going well**, not of **going fast**. The two correlate negatively in the medium term: rushing creates mess; mess destroys productivity.

- Watch for the "Tiger Team" anti-pattern (the best developers pulled into a new greenfield redesign while the rest maintain the old pile).
- Refuse the false urgency that managers project onto every deadline. Defend the code with the same passion they defend the schedule.

## 7. Work as a Team (Ch 34)

Software is a team sport. Individual hero-coding is an anti-pattern.

- Pair programming / mob programming / code review — pick at least one, practice it relentlessly.
- Shared ownership: anyone on the team can change any file. No code-by-divine-right territories.
- The team's cleanliness is bounded by the weakest member's discipline. Teach.

## 8. Estimate Honestly and Fairly (Ch 35)

- Estimates are guesses. Label them honestly.
- A range is more honest than a point. "Between 3 and 8 days" respects reality; "5 days" implies certainty you don't have.
- Don't succumb to schedule pressure to give the number management wants. Be honest about uncertainty; let them make informed decisions.
- When the estimate and the deadline don't line up, the deadline is not bent by wishful thinking.

## 9. Respect for Fellow Programmers (Ch 36)

Judge colleagues by their **ethics, standards, disciplines, and skill** — and nothing else.

- Not by politics, personality, seniority, nationality, or gender.
- A culture of respect is what allows honest code review, pair programming, and shared ownership to work.

## 10. Never Stop Learning (Ch 37)

> "I will never stop learning and improving my craft."

- The languages, frameworks, and practices change constantly. What was best practice 10 years ago is baggage now.
- Read other people's code. Read books. Try new languages off-project. Keep the "beginner's mind" alive.
- Teach. Teaching forces you to understand.

---

## The Programmer's Oath (summarized)

1. I will not produce harmful code.
2. The code I produce will always be my best work, with no defect in behavior or structure.
3. I will produce, with each release, a quick, sure, and repeatable proof that every element of the code works as it should.
4. I will make frequent, small releases that do not impede the progress of others.
5. I will fearlessly and relentlessly improve my creations at every opportunity; I will never degrade them.
6. I will do all that I can to keep the productivity of myself, and others, as high as possible.
7. I will continuously ensure that others can cover for me, and that I can cover for them.
8. I will produce estimates that are honest both in magnitude and precision.
9. I will respect my fellow programmers for their ethics, standards, disciplines, and skill.
10. I will never stop learning and improving my craft.

## GDScript / RTV notes

- **Harm** in an RTV mod context is mostly structural (poor overrides break the game for other mod users) or economic (the time mod consumers lose when your mod breaks on a game update). Keep in mind the audience isn't just you.
- **Repeatable proof** in this repo means: a short manual deploy-and-play checklist (see [`testing.md`](testing.md)). If your mod can't be verified in under a minute, invest in the verification loop.
- **Small cycles** maps directly to: commit often, deploy often, play often. `Scripts/deploy_mod.py` exists precisely to keep the cycle tight.
- **Relentless improvement** on base-game scripts you override: when the game updates and your override starts lagging, that's the moment to re-examine the whole override — not patch-on-patch.
- **Team** in this repo is small; still, CLAUDE.md codifies shared conventions, and pre-commit hooks + CI enforce them. Don't bypass them.
- **Estimates.** For mod work, "one evening" or "a weekend" is honest — committing to a shippable date for a hobby-scale mod over-promises.
