# Formatting

*From chapter 6 ("Formatting").*

Code formatting is communication, and communication is the professional developer's first-order business. Functionality may change; formatting discipline is what lets a team keep the code *readable* across years.

## The newspaper metaphor

A well-written newspaper article is read vertically. The headline tells you the topic. The first paragraph gives you the synopsis. Subsequent paragraphs give increasing detail. A source file should be organized the same way:

- File name → clear, unambiguous.
- Top of file → high-level concepts and algorithms.
- Moving down → increasing detail, until the lowest-level functions are at the bottom.

This matches the **stepdown rule** (see [`functions.md`](functions.md)).

## Vertical formatting

### Openness between concepts

Blank lines separate concepts. Each blank line is a visual cue that says "new thought." Put blank lines between:

- `extends` / `class_name` / import block and the first declaration.
- Declarations and `_ready` / lifecycle methods.
- Functions.
- Logical sections within a long function (though if you need internal section breaks, the function is probably too big).

### Vertical density

Lines of code that are tightly related should appear **densely**, without blank lines between them. Don't break up a group of three assignments that form one logical operation.

### Vertical distance

Concepts that are closely related should be close to each other vertically. Specifically:

- **Variable declarations:** as close to their usage as possible. For locals, right at the top of the function. For instance vars, at the top of the class.
- **Dependent functions:** if one calls another, the caller should be **above** the callee when possible. Reader scrolls down as they dig into detail.
- **Conceptual affinity:** functions that do similar things (`is_valid`, `is_complete`, `is_ready`) should cluster even if they don't call each other.

### Vertical ordering

Top-down newspaper style: public / high-level first, private / low-level last. The reader gets the overview early and only needs to scroll down when they need detail.

## Horizontal formatting

- **Line width:** aim for ~100 characters. Scrolling horizontally is worse than wrapping.
- **Openness:** one space around assignment (`a = b`), no space around tight operators (`a*b`), one space after commas.
- **Indentation:** a visual hierarchy of scope. Don't break it to save a line (no one-line `if` statements that hide bodies).
- **Dummy scopes:** avoid empty `while (...) ;` — if you must have one, make it obvious with visible braces or a comment.
- **Alignment:** don't hand-align variable declarations or assignment operators. It rots the moment something is renamed, and it distracts the eye from the names themselves.

## Team rules

A team should decide on one style and **every member should follow it**. A source file should look like it was written by one person. Rules include:

- Indentation width.
- Placement of braces / blocks.
- Naming conventions (handled in [`names.md`](names.md)).
- Where comments go.
- Line width.

Inconsistency adds cognitive load even when each file is individually well-formatted.

## GDScript / RTV conventions

Authoritative style: [`../godot/gdscript-style-guide.md`](../godot/gdscript-style-guide.md). Key points:

- **Indentation:** tabs (Godot default).
- **Line width:** ~100 characters is the Godot convention.
- **File order (canonical):**
  1. `@tool` / `@icon` annotations
  2. `class_name`
  3. `extends`
  4. Doc comment (`##`) for the class
  5. Signals
  6. Enums
  7. Constants
  8. `@export` vars
  9. Public vars
  10. Private vars (`_leading_underscore`)
  11. `@onready` vars
  12. `_init`
  13. `_ready`
  14. Lifecycle methods (`_process`, `_physics_process`, `_input`, ...)
  15. Public methods
  16. Private methods (`_leading_underscore`)
  17. Subclasses / inner types
- **Blank lines:** two blank lines between top-level functions and classes, one between methods within a class (Godot style guide).
- **Override scripts:** keep the `extends "res://..."` line right after `class_name` (if any) so the target is obvious at a glance.
- **No trailing whitespace; no tabs mixed with spaces.** Let the Godot editor format on save.
