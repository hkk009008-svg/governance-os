---
name: formal-review
description: Use only for an independent GO, NITS, or FAIL review of one exact committed range.
---

# Formal review

Routine work needs no role or mailbox artifact. Use this skill only when the
risk class requires formal review and the desktop task directly assigns
reviewer responsibility for the exact range.

Read the bound request from its committed path. Inspect the actual diff,
reproduce material evidence, and attack the request's abuse classes when the
risk is high. Do not edit the reviewed range.

Publish exactly one GO, NITS, or FAIL with `bin/pipeline mail send`. Bind the
request path and commit, the actual reviewer model, findings, and executed
evidence. High-risk reports use `Abuse Class Assessment: bound-to-request`.

A verdict grants no push, merge, release, spend, destructive, or live-data
authority.
