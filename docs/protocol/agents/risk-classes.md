# Risk classes

Classify the changed behavior, not the amount of text or number of files. Use
the lowest class that truthfully covers the work. The executable profiles live
in `pipeline/codex_protocol_model.py`.

## `ordinary-local`

Reversible repository-local work whose failure does not change a material
runtime behavior or trust boundary. Examples include explanatory prose,
low-risk refactors with preserved behavior, and local diagnostics.

Required: focused verification and exact diff inspection. No formal role,
event, or independent review.

## `material-behavior`

A user-visible or operational behavior change, meaningful bug fix, data-model
change, or integration change where an unnoticed defect would matter.

Required: focused verification plus a temporary author and a non-author Codex
or Claude reviewer over the exact committed range. Same-family review is
allowed unless the change also meets `high-risk-control`.

## `high-risk-control`

A change to authority, authentication, security, privacy, executable
composition, side-effect gates, formal review admission, identity binding,
model-family trust, or another schema that decides whether work or an effect is
accepted.

Required: everything in `material-behavior`, a reviewer from a different model
family, and an explicit assessment of plausible abuse and evasion classes.
Family difference is diversity evidence, not authority. Unknown families fail
the diversity requirement.

AGY may investigate, challenge, test, and review evidence in every class.
Material AGY findings must be answered, but AGY cannot be the independent
formal reviewer or sole accepting verdict.

## `external-effect`

An action outside ordinary reversible local implementation. Push, merge,
release, paid spend, live-data mutation, and destructive operations are always
in this class even when the code was already reviewed.

Required: exact current user/task authority naming executor, target, effect,
and scope. Review, transport messages, app configuration, prior authorization,
and structural tokens do not grant execution. If any field is missing, stop
before the effect.

## Escalation guide

Ask, in order:

1. Is an external effect requested? Handle its authority separately.
2. Does the change decide trust, authority, security, or effect admission? Use
   `high-risk-control`.
3. Does it materially change behavior or integration? Use
   `material-behavior`.
4. Otherwise use `ordinary-local`.

Do not promote risk because coordination feels complex, and do not demote risk
because tests are green. If the boundary remains genuinely ambiguous, ask the
user or take the safer adjacent class without inventing additional ceremony.
