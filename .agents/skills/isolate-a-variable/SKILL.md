---
name: isolate-a-variable
description: Diagnose why behavior works in setup X but fails in setup Y, especially when a measurement is zero or unchanged.
---

# Isolate a variable

List plausible differences between X and Y and put one discriminating read next
to each. If one cause has a cheap direct test, run it. If three or more remain
plausible and their reads are cheap, measure them together once.

Run a known-positive through the same instrument first. Interpret the result as:

| X | Y | Meaning |
|---|---|---|
| speaks | speaks | measured difference is not the cause |
| speaks | silent | localized candidate; confirm the mechanism |
| silent | silent | instrument is blind; no conclusion |

After single-factor reads are clean, consider interactions before expanding the
list. Account for flaky observations and instrumentation that changes the
behavior. A zero is not proof of absence unless the same read detects a
known-positive at the same location.

Report what was measured, eliminated, still plausible, and not examined. Do not
claim that the list contains every environmental difference.
