# Comments

*From chapter 5 ("Comments").*

> "Comments are the distracting footnotes of code." — Jeff Langr

## The core premise

**Comments are, at best, a necessary evil.** They compensate for a failure to express ourselves in code. Every comment is an admission that the language or the author couldn't make the code say what it means.

- Truth lives in one place: **the code**. Comments lie — not intentionally, but inevitably, because programmers can't maintain them as code moves and mutates.
- Inaccurate comments are worse than no comments. They mislead, set false expectations, and preserve obsolete rules.
- Before writing a comment, try to express the same thing in code (extract a method, rename a variable, introduce a named constant). If you succeed, the comment is unnecessary.

## Good comments

A small number of comment kinds pay their way.

- **Legal comments.** Copyright headers, license declarations. Required by policy, not craft.
- **Informative comments.** Translating an opaque value into intent:
  ```gdscript
  # Matches HTTP date like "Tue, 02 Apr 2003 22:18:49 GMT"
  const HTTP_DATE_REGEX := "[SMTWF][a-z]{2}..."
  ```
- **Explanation of intent.** Why a non-obvious decision was made, especially if it surprises a reader. (Not *what* — the code says what.)
- **Clarification.** When you must use an obscure API or literal you cannot rename, explain what the value means locally.
- **Warning of consequences.** `# Not thread-safe — callers must hold the audio lock.`
- **TODO comments.** Short, targeted, *scheduled*. Grep them regularly and burn them down. A TODO that has lived in the repo for a year is a permanent lie.
- **Amplification.** Drawing the reader's attention to something important that looks trivial. "This trim is significant — without it the parser silently eats the trailing newline."
- **Public API documentation.** Interfaces consumed by strangers (libraries, plugins, mod SDKs) benefit from doc comments that describe contract.

## Bad comments

Most comments are bad. Common modes of failure:

- **Mumbling.** A comment the author wrote quickly and even they don't understand later.
- **Redundant.** `i += 1  # increment i`. Adds characters, zero information.
- **Misleading.** Once true, now false. Every rename or refactor is a chance for a comment to become a lie.
- **Mandated.** Doc comments required on every method by policy, even trivial getters. Noise for the sake of compliance.
- **Journal / changelog comments at the top of files.** Git has a log. Don't duplicate it.
- **Noise.** `/** Default constructor. */` — says nothing the signature didn't.
- **Don't use a comment when you can use a function or variable.**
  - Bad: `# check if the employee is eligible for full benefits` above a convoluted boolean.
  - Good: extract it into `func is_eligible_for_full_benefits() -> bool`.
- **Position markers.** `# ////////// HELPERS //////////` — use structure (classes, files, sections in the style guide), not banners.
- **Closing-brace markers.** `} // while` — your function is too long; shrink it.
- **Attributions and bylines.** `// Added by Mike`. Git blame exists.
- **Commented-out code.** **Delete it.** Version control remembers. Commented-out code rots; readers are afraid to delete it because "it might be important"; it accumulates.
- **HTML / Javadoc decoration in source comments.** If the comment is for an IDE tool, keep it minimal; don't let markup drown the prose.
- **Nonlocal information.** A comment describing something far from where it sits (a system-wide default, another module's behavior). The comment will drift out of sync.
- **Too much information.** Don't embed RFC excerpts or long-form design rationale. Link to the doc; don't quote it.
- **Inobvious connection.** A comment that refers to `magic 0xFFE8` without explaining why the reader should care about that value.
- **Function headers.** If a function's name and signature don't explain it, fix the function. Don't patch it with a header block.

## Rules of thumb

- **If you write a comment, read it.** Paint comments bright red in your IDE — if the comment doesn't help, delete it on the spot; if it's wrong, fix it on the spot.
- **The older a comment, the farther it sits from the code it describes, the more likely it is to be wrong.**
- A comment should be the *last resort* after renaming, extracting, and restructuring have all failed.

## GDScript / RTV notes

- Use `##` doc comments for public APIs that mod consumers will call (in this repo, that's rare — most mod code is for Claude and the author). Use `#` for ordinary inline comments.
- **Project-instruction override:** the repo's `CLAUDE.md` says: default to no comments; only write one when the *why* is non-obvious (hidden constraint, subtle invariant, workaround for a specific bug). That directive supersedes anything here when authoring code in this repo.
- **Specifically don't write:**
  - "// removed X" placeholders after deletion.
  - Comments referencing the current task, PR, or issue number.
  - Comments explaining `super._input(event)` — it's a universal rule in this codebase.
- **Do write** a short comment when overriding a base-game script and the override's behavior depends on a decompiled source line that isn't obvious (e.g., "must run after `Handling.gd:312` sets `current_item`").
