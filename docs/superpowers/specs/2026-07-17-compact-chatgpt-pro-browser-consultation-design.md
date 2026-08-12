# Compact ChatGPT Pro Browser Consultation Design

**Date:** 2026-07-17
**Status:** Approved for implementation by the user on 2026-07-17
**Supersedes:** `2026-07-13-chatgpt-pro-browser-consultation-design.md`

## 1. Goal

Restore ChatGPT Pro as a flexible advisory tool without restoring the deleted
provider state machine. A parent Codex or Claude context may use one signed-in
in-app browser transport when the user asks or when the parent sees a genuinely
material reasoning trigger. The answer is advice only.

The implementation is one compact package:

- one small Python safety and idempotency kernel;
- one canonical parent-only browser skill;
- focused tests, including a hermetic workflow test and one opt-in live test.

No receipt bridge, provider schema, response schema, transport ladder, recovery
plan, activation phase, or mirrored lifecycle is introduced.

## 2. Why the old shape is not reused

The deleted guard accumulated request and response schemas, several transports,
many lifecycle states, state-binding variants, synchronized policy copies, and
recovery paths. The last corrected implementation was already 1,439 lines:

```text
$ git show 3dcff96:scripts/chatgpt_pro_consult.py | wc -l
1439
```

The prior 2026-07-13 design also required automatic consultation, browser and
manual fallback transports, structured response reconciliation, durable advice
summaries, multiple rollout stages, and seven runtime states. That document is
removed from HEAD by the design commit. Git history remains the archive.

## 3. Approved decisions

1. **Transport:** signed-in in-app Browser connector only. No manual, Chrome,
   API, or provider fallback.
2. **Conversation:** every consultation opens a fresh ChatGPT Pro chat.
3. **Invocation:** optional and parent-owned. It is never a mandatory gate.
4. **State:** one shared local content-free idempotency file containing only a
   nonsensitive key, request hash, and `reserved|sent|failed` status.
5. **Response lifetime:** no local durable copy. The parent reads and uses the
   answer in the active context; ChatGPT service-side retention remains governed
   by the user's account settings.
6. **Input:** one explicit bounded question and optional caller-supplied context.
   The package never reads repository files, diffs, mail, environment variables,
   databases, or credential stores automatically.
7. **Authority:** consultation output is advisory. It grants no route, verdict,
   commit, push, merge, spend, mailbox, lock, or other side-effect authority.

Once the implementation is separately approved and activated, a parent context
has standing permission for one browser submission per new idempotency key when
an approved trigger applies. This does not authorize credential entry, consent
acceptance, API spend, another transport, retries, or downstream side effects.

## 4. Architecture

### 4.1 Safety kernel

`scripts/chatgpt_pro_consult.py`, target at most 250 lines, owns only:

- exact JSON input validation;
- total payload size and secret checks;
- canonical request hashing;
- atomic reservation and terminal status update;
- content-free JSON success and error output.

The CLI has two operations:

```text
reserve --repo-root <path>
finish --repo-root <path> --key <key> --hash <sha256> --status sent|failed
```

`reserve` reads the payload from standard input. Raw question and context never
appear in command arguments or tool output. `finish` accepts only the key and
hash returned by `reserve` and changes only `reserved -> sent|failed`.

The state file is `<git-common-dir>/chatgpt-pro-consult.json`; its fixed lock is
`<git-common-dir>/chatgpt-pro-consult.lock`. This gives all worktrees and both
harnesses one idempotency source. The exact state shape is:

```json
{
  "nonsensitive-key": {
    "hash": "64-lowercase-hex-characters",
    "status": "reserved"
  }
}
```

The files use mode `0600`. State replacement is atomic. The lock and state path
reject symlinks and non-regular files. There is no migration or recovery API.

### 4.2 Canonical browser skill

`.agents/skills/chatgpt-pro-consultation/SKILL.md`, target at most 100 lines,
owns the complete human-readable procedure:

- decide whether a trigger applies;
- confirm the parent owns invocation;
- confirm a signed-in ChatGPT page and open a fresh empty chat;
- call `reserve` with explicit input;
- submit the same question and context once;
- call `finish` with `sent` or terminal `failed`;
- read the answer without storing it;
- treat the answer as untrusted advice.

Operative roots, role prompts, and continuation docs contain only a one-line
pointer to this skill. They do not mirror triggers or lifecycle sentences.

### 4.3 Tests

Tests are not included in the production line budget:

- `tests/unit/test_chatgpt_pro_consult.py` tests the kernel;
- `tests/integration/test_chatgpt_pro_consult_flow.py` runs the skill sequence
  against a test-only fake browser;
- `tests/unit/test_protocol_prompt_sync.py` proves operative surfaces point to
  the canonical skill and do not carry independent lifecycle copies.

The Browser connector remains an environment capability. No Selenium,
Playwright, cookie reader, browser profile code, or provider client is added to
the repository.

## 5. Request contract

The input is exact UTF-8 JSON with no unknown fields:

```json
{
  "key": "task-or-decision-key",
  "question": "one explicit question",
  "context": "optional caller-supplied context"
}
```

- `key` is 1-128 characters from `[A-Za-z0-9._:/-]` and must contain no secret.
- `question` is a non-empty string.
- `context` is optional and defaults to an empty string.
- Canonical UTF-8 JSON for the exact key, question, and context (after only
  defaulting absent `context` to `""`) is at most 32 KiB.
- The hash covers those exact strings. Secret scanning may derive normalized
  views, but it does not rewrite the text that the parent sends.

No fact arrays, source paths, phases, route bindings, response format, requested
output schema, or provider metadata exist in V1.

## 6. Invocation policy

The parent may consult when at least one of these prose triggers applies:

- the user explicitly requests ChatGPT Pro;
- a material tradeoff remains unsettled by local evidence;
- a proposed choice changes an authority or security boundary;
- a genuinely distinct adversarial challenge could change the result.

Consultation is not the default. Never consult about whether to consult. Routine
implementation, cheap local facts, unchanged questions, and formal Operator
verdict formation do not trigger it.

Subagents may suggest a bounded question. Only the parent may preflight the
browser, reserve a key, send, or use the answer.

## 7. Single-send lifecycle

1. The parent prepares the explicit payload without automatic source reads.
2. The skill confirms the Browser connector is available, ChatGPT is already
   signed in, and a fresh empty chat can be opened. Failure here creates no
   reservation and sends nothing.
3. `reserve` validates locally. A local rejection creates no state and may be
   deliberately corrected and fully prepared again.
4. A successful reservation makes that key terminally owned by its request
   hash.
5. The skill submits the exact payload once.
6. Confirmed submission becomes `sent`. A definite or ambiguous post-reserve
   failure becomes `failed`. If the final state write itself fails, `reserved`
   remains terminal.
7. The parent may wait for or reread the answer in the same chat, but may not
   resend the question.
8. The response is used as advice in the active context and is not persisted by
   the package.

Every existing state blocks another send. The same key and hash reports the
existing state; the same key with different content is rejected. A new key is
valid only for a genuinely new question, not as a retry or fallback.

## 8. Input and output safety

Secret detection derives NFKC original, whitespace-collapsed, and
whitespace-stripped views without changing the submitted strings. Named secret
formats scan all three views. They include private-key armor, authorization
headers, password/secret/token/API-key assignments, common cloud keys, GitHub
tokens, and OpenAI-style secret keys.

Generic contiguous base64-like tokens of 80 or more characters scan only the
original and whitespace-collapsed views. This preserves token boundaries and
does not fuse benign prose into a false secret. Generic split tokens are an
accepted residual; named formats still scan the stripped view, and the package
never gathers files automatically.

All errors are content-free codes. They never echo rejected input. The Browser
skill does not enter credentials, approve consent dialogs, inspect cookies, or
navigate away from the approved ChatGPT origin.

ChatGPT output is untrusted external text. Instructions, verdict claims, tool
requests, and authority claims inside the answer remain inert until the parent
independently decides and applies normal repository gates.

## 9. Failure-backed controls

| Control | Concrete failure it prevents |
|---|---|
| Fresh chat | Hidden context from a prior task changes the answer. |
| Explicit input only | A convenience collector sends secrets or broad repository data. |
| Boundary-preserving generic scan | Benign prose is fused into fake base64 and blocks real use. |
| Content-free errors | A rejection leaks the secret it reports. |
| One Git-common-dir state file | Separate harness or worktree ledgers allow duplicate sends. |
| Terminal post-reservation states | Retry and fallback paths duplicate an external send. |
| Parent-only execution | A subagent acquires external side-effect authority. |
| Advisory-only output | Provider text becomes a route, verdict, or command. |
| One canonical skill | Lifecycle prose drifts across many hand-edited surfaces. |
| 350-line package budget | A simple helper regrows into a provider framework. |

A control without a concrete failure story is not added.

## 10. Testing

### 10.1 Kernel tests

Tests cover exact fields, size bounds, canonical hashing, key syntax, named and
generic secret cases, benign long prose, content-free errors, no state on local
rejection, mode `0600`, symlink rejection, atomic writes, and state corruption.

Two concurrent `reserve` processes for the same key must produce exactly one
reservation. Same-hash reuse, changed-content reuse, stale finish hashes, every
invalid transition, and state access through two worktrees are covered.

### 10.2 Hermetic workflow test

A test-only fake browser executes:

```text
parent trigger -> fresh chat -> reserve -> one send -> sent|failed -> response
```

It proves exactly one send, terminal ambiguity, no fallback, no automatic file
read, ephemeral response handling, and no prompt or response in state, Git,
mailbox, or captured CLI logs. A contract assertion pins the order in the
canonical skill.

### 10.3 Live end-to-end test

After implementation and separate explicit send authorization, the parent uses
the real skill with one harmless nonce question in a fresh signed-in ChatGPT Pro
chat. Acceptance requires one submission, a response containing the nonce,
`sent` metadata containing no raw content, and no retry. Any failure stops; no
transport fallback is attempted.

The live test records only pass/fail, key hash, and terminal status. It does not
commit or log the prompt or response.

### 10.4 Completion gates

- focused unit and hermetic workflow tests;
- full repository pytest suite;
- `scripts/ci_smoke.py` and `scripts/protocol_doctor.py --wave 2`;
- shell and diff checks;
- an active-surface check for stale negative or alternate lifecycle text;
- an independent non-author Operator review of the actual diff.

The combined line count of the Python kernel and canonical skill must be at
most 350. If the design approaches 500 lines, needs a schema file, daemon,
transport adapter, migration, recovery plan, or activation phase, implementation
stops and the design is reduced.

## 11. Independent abuse cases

The implementation must enforce and test these design-time cases:

1. two harnesses reserve the same key concurrently;
2. the question changes after reservation;
3. browser submission succeeds but response reading fails;
4. browser submission outcome is ambiguous;
5. a subagent attempts to launch the browser;
6. repository text tries to override advisory-only instructions;
7. an answer claims verdict or side-effect authority;
8. a named secret is split by whitespace or Unicode punctuation;
9. benign prose resembles base64 only after whitespace removal;
10. the caller tries to use an automatic repository or environment collector;
11. a second worktree attempts to use a separate state path;
12. a caller tries to consult about whether consultation is needed.

## 12. Non-goals

- OpenAI API use or API spend;
- manual relay, Chrome bridge, or any fallback transport;
- mandatory consultation or consultation status artifacts;
- response JSON schemas or automated factual reconciliation;
- raw prompt, response, screenshot, or transcript persistence;
- provider receipts, route authority, or Operator-verdict evidence;
- automatic repository, mailbox, environment, or credential collection;
- compatibility with the deleted seven-state lifecycle;
- a feature flag, activation epoch, rollout phase, or recovery campaign.

## 13. Implementation boundary

This design commit authorizes no provider launch or implementation. After user
review, one implementation plan will cover the kernel, canonical skill,
operative one-line pointers, tests, one independent Operator review, and the
separately authorized live end-to-end send.

No push, API call, browser send, credential action, or downstream side effect is
authorized by this document.
