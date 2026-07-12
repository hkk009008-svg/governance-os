---
name: chatgpt-pro-consultation
description: Use when the user explicitly asks to consult ChatGPT Pro; an idea or plan has unresolved material tradeoffs; a pre-plan changes an authority, security, external-input, parseable-context, schema-trust, or side-effect boundary; a post-plan needs a distinct adversarial challenge; or a mailbox-oriented coordinator needs strategic advice before a consequential synthesis, reroute, or contradiction resolution.
---

# ChatGPT Pro Advisory Consultation

## Trigger decision

The capability is always invocable when the user explicitly asks to consult ChatGPT Pro. Otherwise consult automatically only when the answer could materially change the result and one of these canonical triggers holds:

- an idea or plan has materially different approaches not settled by durable local evidence;
- a mailbox-oriented coordinator is about to synthesize a consequential cross-lane plan, reroute, or contradiction resolution;
- a design or plan changes an authority, security, external-input, parseable-context, schema-trust, or side-effect boundary; or
- an approved design or plan needs a genuinely different adversarial challenge.

Skip trivial questions, cheap local facts, routine approved implementation, verdict formation, unsafe context, already-converged review, and an unchanged question/state with an existing result. Never consult about whether to consult. Deduplicate unchanged work; automatic retries are zero in V1.

## Authority

Treat the result as advisory only. This is not the dual-chief order path and grants no mailbox, route, lock, verdict, spend, commit, push, merge, or other side-effect authority; subagents may prepare a bounded question but only the parent context may send or import a response.

## Prepare

1. Collect the minimum decision, locally verified facts, options, and current state binding. Exclude credentials, private mailbox/customer/business data, broad excerpts, and prohibited source classes. The guard performs no automatic file reads.
2. Build the request JSON in memory and pass it only through stdin to `.venv/bin/python scripts/chatgpt_pro_consult.py prepare`. Never put request or response content in shell arguments, interpolation, environment variables, or temporary files.
3. Stop on mode, schema, sanitizer, state, or idempotency failure. Use only the returned guarded prompt.

## Browser transport

In `auto` mode, **REQUIRED SUB-SKILL:** load and follow `browser:control-in-app-browser`. Prefer the in-app browser, then an approved Chrome bridge. Open a fresh chat on an approved ChatGPT origin; never inspect cookies/storage, enter credentials, accept consequential consent, upload files, or add context outside the guarded prompt. Transition `prepared -> sending` immediately before the send and `sending -> sent` only after one confirmed send, using `.venv/bin/python scripts/chatgpt_pro_consult.py transition` with transport `iab` or `chrome`; one guarded browser send per idempotency key. Finalize consultation tabs under the Browser skill's rules.

## Manual relay

`manual` is the default and permits no browser send. Give the user the exact prepared prompt to paste into a fresh ChatGPT Pro chat and ask for the exact correlated JSON response. Do not offer an unguarded alternate prompt. Use the same lifecycle transitions with transport `manual`; mark partial or uncertain delivery failed.

## Accept

Refresh the relevant local binding, then pass an in-memory wrapper containing the local consultation ID, exact response, and current binding through stdin to `.venv/bin/python scripts/chatgpt_pro_consult.py accept`. Stop if correlation or staleness validation fails; never repair the response by hand.

## Reconcile

Verify every material factual claim locally. Classify each recommendation `adopted | modified | rejected | unresolved` with a short reason, then transition a fully processed response to `reconciled`; raw prompts and responses stay out of Git, mailbox artifacts, normal logs, screenshots, command arguments, and local transcript files.

## Mode rules

- Readiness may consult ideas or read-only plans without upgrading into a seat.
- Director may consult design, brief, or plan tradeoffs, then must verify claims locally.
- Coordinator is mailbox-first before consultation: refresh HEAD, mailbox bodies, route, wave, capacity, and locks before prepare, then refresh HEAD, mailbox bodies, route, wave, capacity, and locks again before send and before use; pre-send drift discards the prepared packet and requires re-prepare, and later drift marks the response stale.
- Operator consultation never replaces Lane V. Use it only on explicit request or for a distinct, pre-stated strategic question; it cannot contribute authority to GO, NITS, or FAIL.
- `off` fails closed. `manual` permits guarded export/import only. `auto` permits the guarded Browser ladder.

## Failure

If signed out, ask the user to sign in; never enter credentials. Follow Browser safety for a challenge or CAPTCHA. After a definite safe auto failure is transitioned to `failed`, explicitly run `.venv/bin/python scripts/chatgpt_pro_consult.py resume-manual --state-file PATH --consultation-id UUID` to return the same record to `prepared`/`manual`, then relay the exact guarded prompt. The command arguments are content-free identifiers; request and response payload content remains stdin-only; uncertain or partial delivery stops for explicit user decision; never retry or resume automatically. Use no API fallback. Continue from local evidence when advice is optional; return an unresolved high-impact choice to the user. Advisory status, an NDA, manual relay, or a “non-sensitive” response never permits raw transcript persistence.

## Durable summary

Write a summary only when advice materially changes the target artifact. Use design §13's Consultation ID plus six sanitized content fields: Phase, Bound HEAD/route, Question, Advice summary, Codex dispositions, and Resulting change. Include no verbatim transcript, hidden reasoning, private context, or unverified claim.
