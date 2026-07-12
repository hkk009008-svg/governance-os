# ChatGPT Pro Browser Consultation Design

**Date:** 2026-07-13
**Status:** Approved design; implementation pending

## 1. Problem

Pipeline already identifies Gemini Deep Think and ChatGPT Pro as app-based,
human-relayed strategic advisers. Codex can also control a signed-in browser in
the Desktop application and, on suitably configured hosts, from Codex CLI.
Those pieces are not yet connected by a durable Codex behavior contract.

As a result, Codex has no consistent way to decide when to ask ChatGPT Pro for
help while developing an idea, challenging a plan, or synthesizing a
coordinator decision. It also lacks a common safety boundary for selecting
repository context, correlating the answer to current state, preventing
duplicate sends, and reconciling advice without accidentally granting the app
protocol authority.

The desired behavior is an always-invocable, automatically triggered advisory
consultation path. It should work directly through a signed-in browser whenever
that transport is available and retain a safe manual relay path on any CLI
host. The user-principal has approved automatic sending of sanitized packets
and summary-only durable records.

## 2. Goals

- Make ChatGPT Pro consultation explicitly invocable in every Codex mode.
- Automatically attempt consultation when a defined strategic trigger fires.
- Support Codex Desktop and Codex CLI through one transport-independent
  contract.
- Prefer a signed-in in-app browser, with an approved signed-in Chrome bridge
  as a secondary browser transport.
- Preserve a manual packet export and response import path when no authenticated
  browser transport is available.
- Fail closed on secrets, prohibited sources, ambiguous sanitization, stale
  state, malformed responses, and authority confusion.
- Bind every request and response to its purpose and relevant repository state.
- Treat ChatGPT Pro output as untrusted advisory material that Codex must
  verify and disposition.
- Keep raw prompts and responses out of Git, mailbox artifacts, normal logs,
  command arguments, and durable protocol state.
- Persist only a compact sanitized decision record when advice materially
  affects a design, plan, or coordinator synthesis.
- Avoid duplicate consultations and retry storms.
- Keep browser authentication, cookies, and credentials under user control.

## 3. Non-goals

- Guaranteeing a remote response while offline, signed out, blocked by an
  authentication challenge, or during an OpenAI outage.
- Treating a ChatGPT Pro subscription as OpenAI API authorization or budget.
- Adding an API fallback in V1.
- Giving ChatGPT Pro a director, operator, coordinator, overseer, merge-gate,
  mailbox, or signed-bus identity.
- Letting ChatGPT Pro issue `GO`, `NITS`, `FAIL`, route work, consume mail,
  claim locks, authorize spend, commit, push, merge, or execute commands.
- Replacing Lane V, R-INDEPENDENCE, specialist review, capacity validation,
  mailbox-first orientation, or any other existing gate.
- Automatically dumping files, diffs, logs, environment variables, databases,
  workbooks, or whole repository trees into a chat.
- Persisting a local copy of the full app transcript. The ChatGPT application
  remains responsible for its own service-side chat retention settings.
- Building a general browser automation framework. V1 uses the installed
  Browser skill as the transport implementation.

## 4. Chosen approach

Implement a model-backed consultation contract, a dedicated repo skill, and a
small deterministic packet guard.

The executable policy source remains `scripts/codex_protocol_model.py`. It
defines the triggers, authority boundary, transport order, state-binding
requirements, and reconciliation rules. The Codex continuation guide, repo
skills, and relevant role prompts mirror that source and are protected by sync
tests.

`.agents/skills/chatgpt-pro-consultation/SKILL.md` becomes the runtime
procedure. It decides whether a trigger applies, gathers only the minimum
necessary facts, invokes the packet guard, selects an available Browser-skill
transport, reads the response, verifies material claims locally, and records a
sanitized disposition only when useful.

`scripts/chatgpt_pro_consult.py` is a dependency-light local guard. It validates
and renders packets, tracks non-content idempotency metadata, and validates
response envelopes. It never opens a browser, enters credentials, sends a
message, reads arbitrary repository files, or performs protocol writes.

This approach is preferred over coordinator-only instructions because the
feature is also useful during readiness, ideation, and director planning. It is
preferred over a custom browser or API client because the installed Browser
skill already owns authenticated UI interaction and because a Pro subscription
does not authorize API spend.

## 5. Meaning of "always possible"

The consultation capability is always invocable, but remote availability is
not fabricated. The transport resolver uses this ladder:

1. Signed-in in-app browser exposed by the Browser skill.
2. Signed-in Chrome bridge exposed by the Browser skill when allowed by the
   approved project policy and available in the current environment.
3. Manual relay: emit the exact sanitized packet for the user to paste into
   ChatGPT Pro, then accept the correlated response through standard input.
4. Explicit `unavailable` result when even packet preparation or safe response
   correlation cannot complete.

Desktop and CLI share the same packet and response contracts. A CLI host with
the Browser skill and an authenticated backend can complete the whole flow
automatically. A bare CLI can always prepare the packet and resume from a
manually relayed response.

There is no silent API substitution. A future API adapter would require a
separate design, credentials boundary, cost policy, and explicit
user-principal authorization.

## 6. Invocation and trigger policy

### 6.1 Explicit invocation

The user may request consultation at any point with language such as
`consult ChatGPT Pro`, `ask Pro`, or by naming the consultation skill. Explicit
invocation still passes through sanitization, state binding, and authority
checks.

### 6.2 Automatic triggers

Codex automatically attempts one consultation when any of these conditions
holds and the answer could materially change the result:

1. An idea or plan has multiple materially different approaches and durable
   local evidence does not settle the trade-off.
2. A coordinator, after mailbox-first orientation, is about to synthesize a
   consequential cross-lane plan, reroute, or contradiction resolution.
3. A proposed plan changes an authority, security, external-input,
   parseable-context, schema-trust, or side-effect boundary.
4. A completed design or plan needs a genuinely different adversarial
   challenge before user review or implementation.
5. The user explicitly requests ChatGPT Pro consultation.

### 6.3 Skip conditions

Codex does not consult for:

- trivial or self-contained questions;
- routine implementation already determined by an approved plan;
- facts that can be resolved cheaply from current source or executable tools;
- an unchanged question with the same relevant state and an existing result;
- the same question already covered by Lane V or two converged reviewers;
- operator verdict formation, formal verification, or gate evidence;
- packets that cannot be safely minimized and sanitized; or
- activity whose only purpose would be appearance of consultation.

Skipping a routine consultation does not create a status artifact. When an
automatic trigger is material but consultation cannot safely run, Codex reports
the degraded state in the current user-facing result or target design/plan.

## 7. Mode and authority boundaries

### 7.1 Readiness bridge

The bridge may consult during idea development or read-only planning. It still
may not consume cursors, send mailbox events, route seats, claim locks, push,
spend, or author production changes.

### 7.2 Director seats

A director may consult while comparing designs, writing a brief, or challenging
an implementation plan. The director remains responsible for source checks,
R-BRIEF, Rule #12, Rule #13, scope, and the verify request.

### 7.3 Coordinator

The coordinator consults only after reading current all-scope mailbox bodies
and gathering the live route, capacity, lock, gate, and HEAD context needed for
the question. The consultation may help compare strategies, but it cannot be a
route, capacity decision, mailbox event, inventory transition, or correctness
proof.

Immediately before sending and again before accepting the advice, the
coordinator refreshes the relevant live state. If HEAD, relevant mailbox
bodies, route identity, wave, capacity state, or locks changed, the result is
marked stale. The coordinator may create a new consultation for the changed
state only if the question remains material.

### 7.4 Operators

An operator does not use ChatGPT Pro as Lane V or as a substitute for the
required cross-model verifier. Operator consultation is allowed only on an
explicit user request or a distinct, pre-stated strategic question permitted
by R-VERIFY-TIER. It never contributes authority to `GO`, `NITS`, or `FAIL`.

### 7.5 Subagents

Subagents may recommend a question or prepare a bounded read-only context
summary. They may not send the browser message or import a response. The parent
Codex context is the single consultation executor and retains all seat and
side-effect authority.

## 8. Request contract

The guard accepts UTF-8 JSON through standard input. Sensitive content is never
placed in shell arguments. The request contract is:

```json
{
  "schema_version": "chatgpt-pro-consult-request/v1",
  "consultation_id": "<uuid>",
  "phase": "ideation | pre_plan | post_plan | coordinator",
  "purpose": "<one bounded decision>",
  "repo_head": "<full SHA or null>",
  "state_binding": {
    "wave": "<integer or null>",
    "route_id": "<string or null>",
    "relevant_paths_hash": "<sha256 or null>",
    "mailbox_snapshot_hash": "<sha256 or null>"
  },
  "question": "<one explicit question>",
  "facts": [
    {
      "label": "<short label>",
      "source": "<repo-relative path:line, command, or user statement>",
      "trust": "trusted_fact | untrusted_excerpt",
      "text": "<minimal sanitized text>"
    }
  ],
  "options": ["<optional bounded option>"],
  "requested_output": [
    "recommendation",
    "reasoning",
    "assumptions",
    "risks",
    "questions"
  ]
}
```

The guard computes and appends:

- a canonical request hash;
- an idempotency key derived from purpose, normalized question, state binding,
  and relevant context;
- an instruction that all repository excerpts are data, never instructions;
- an instruction not to request more files or perform browser navigation;
- an advisory-only authority notice; and
- the exact response contract.

V1 allows at most eight fact fragments, 2 KiB per fragment, and 16 KiB for the
entire rendered request. Oversize input fails closed rather than truncating a
secret scan or silently dropping context.

The guard does not read source paths. Codex must hand-select excerpts. This
prevents a packet declaration from becoming authority to open arbitrary files.

## 9. Sanitization contract

The outbound guard applies Unicode normalization and rejects, rather than
redacts ambiguously, any packet containing:

- private-key or seed material;
- bearer/basic authorization headers;
- known API-token, cloud-key, GitHub-token, password, cookie, or session-token
  shapes;
- long base64-like or hexadecimal blobs in free-form text; typed Git and
  request-hash fields are validated separately by the schema;
- control characters or invalid UTF-8;
- content sourced from `.env`, credential stores, private key directories,
  browser/session stores, local databases, customer/business-data files, or
  other prohibited source classes;
- absolute home paths that expose private machine layout; or
- a sanitizer canary used by tests.

Repository text is labeled `untrusted_excerpt` unless it is a short fact Codex
independently established through a cited command. Untrusted excerpts are
delimited and cannot change the role, scope, output schema, transport, or
authority notice.

The guard is defense in depth, not permission to send broad context. Codex
must minimize first. Any uncertainty about whether content is private cancels
automatic sending and falls back to a question that can be answered without
that content or to the user.

## 10. Browser transport contract

The consultation skill invokes the installed Browser skill and follows its
runtime selection and authentication rules. It does not implement Playwright,
cookie access, profile inspection, or credential entry itself.

The approval recorded by this design is narrow standing authorization for one
automatic send of a guard-approved, sanitized packet when a trigger fires. It
does not authorize credential entry, broad repository disclosure, automatic
retries, API spend, consent-dialog acceptance, or any resulting protocol or
external side effect.

For each consultation it opens a fresh ChatGPT conversation so earlier task
context cannot silently influence the answer. It uses only an approved ChatGPT
origin, enters the guard-rendered packet once, sends once, and waits for the
correlated response.

The automation must recognize logged-out pages, consent or challenge screens,
navigation failures, partial sends, timeouts, and malformed output. It never
enters passwords, reads cookies or storage, dismisses a consequential consent
dialog, or claims success from a partially rendered response.

Browser failure yields a resumable manual-relay packet. It does not trigger an
automatic retry loop or switch to an API. A changed state produces a new
consultation ID and idempotency key rather than replaying an old send.

## 11. Response and reconciliation contract

ChatGPT Pro is asked to return:

```json
{
  "schema_version": "chatgpt-pro-consult-response/v1",
  "consultation_id": "<matching uuid>",
  "request_hash": "<matching sha256>",
  "recommendation": "<advisory recommendation>",
  "reasoning": ["<bounded reason>"],
  "assumptions": ["<explicit assumption>"],
  "risks": ["<risk or counterargument>"],
  "questions": ["<remaining question>"]
}
```

The guard validates the schema, correlation fields, concrete JSON types, and
size bounds. A missing or mismatched ID/hash, unknown schema version, oversized
response, or malformed object is quarantined as unusable advisory text. It is
never interpreted as an instruction to use tools or change state.

Codex then:

1. Rechecks the bound local state.
2. Separates factual claims from recommendations.
3. Verifies every material factual claim against current source or executable
   evidence.
4. Dispositions each adopted recommendation as `adopted`, `modified`,
   `rejected`, or `unresolved`, with a short reason.
5. Keeps unresolved advice from deciding a high-impact choice.
6. Applies the normal user, seat, mailbox, capacity, verification, and
   side-effect gates to any resulting action.

No text in the response is executed, pasted into a shell, written to a mailbox,
or accepted as a protocol verdict automatically.

## 12. Idempotency and local runtime state

The guard maintains only non-content runtime metadata in an ignored local
state file:

```text
idempotency key
consultation ID
request hash
state-binding hashes
status: prepared | sending | sent | received | reconciled | failed | stale
timestamps
transport class
```

The state file contains no prompt, fact text, response, cookies, credentials,
or chat URL. There may be only one active send per idempotency key. The same
unchanged request is not sent twice.

Timeouts and failures terminate the attempt. A user may explicitly resume a
manual relay with the same consultation ID, but automated retries remain
bounded to zero in V1.

## 13. Durable record policy

Raw prompts and responses are not committed, placed in mailbox events, written
to normal logs, or saved as repository files. Browser screenshots are not used
for consultation capture.

When advice materially changes a durable design, plan, brief, or coordinator
strategy, the target artifact may include one compact record:

```markdown
## ChatGPT Pro consultation

- Consultation ID: <uuid>
- Phase: <phase>
- Bound HEAD/route: <sha and route, or not applicable>
- Question: <sanitized one-line question>
- Advice summary: <sanitized summary>
- Codex dispositions: <adopted/modified/rejected/unresolved with reasons>
- Resulting change: <what changed in this artifact>
```

The record must not contain verbatim transcript passages, hidden reasoning,
private context, or unverified factual claims. If the advice did not change the
artifact, no consultation record is required.

## 14. Failure behavior

| Failure | Required behavior |
|---|---|
| No Browser skill/backend | Emit manual-relay packet |
| Signed out or challenged | Ask the user to sign in; never enter credentials |
| Network/service failure | Return explicit `unavailable`; no invented answer |
| Sanitizer rejection | Do not send; minimize again or ask the user |
| Partial/duplicate send uncertainty | Mark failed and do not resend automatically |
| Malformed/mismatched response | Quarantine as unusable advisory text |
| HEAD/mailbox/route drift | Mark response stale and refresh local evidence |
| Consultation is advisory | Continue with local evidence and report degradation |
| Consultation is necessary for an unresolved high-impact choice | Stop and ask the user |

## 15. Independent adversarial enumeration

This design touches external input, parseable prompt composition, data
disclosure, and authority boundaries, so R-INDEPENDENCE applies. An independent
same-model, fresh-context review identified the following required abuse cases.
The implementation plan must turn each row into an enforced test or explicit
manual acceptance check.

| Abuse case | Enforced acceptance target |
|---|---|
| Secret or private-data leakage | Canary secrets, split-line tokens, private keys, `.env` values, credentials, cookies, encoded blobs, customer data, and prohibited paths never reach rendered output or durable artifacts. |
| Prompt injection in repository text | Malicious comments cannot alter role, scope, response schema, browser behavior, or authority notice. |
| Authority confusion | Advice cannot authorize protocol or external side effects and never becomes a verdict or mailbox event automatically. |
| Stale or replayed advice | ID, request hash, HEAD, relevant-path, route, wave, and mailbox bindings must match before reconciliation. |
| Duplicate sends and retry storms | One active send per idempotency key; ambiguous failure causes no automatic resend. |
| Authentication, browser, or network failure | No result is fabricated; a resumable manual packet remains available. |
| Malformed or adversarial response | Unknown schema, bad types, missing correlation, oversized content, and embedded action directives remain inert. |
| Transcript leakage | Repo-wide scans after success and failure find no prompt, response, canary, or transcript markers outside approved sanitized summaries. |
| Desktop/CLI divergence | Both environments render the same canonical packet; CLI without browser support still exports and imports safely. |
| Cross-task contamination | Fresh chats and per-request IDs prevent one task from inheriting another task's context. |
| Redirect or profile misuse | Unapproved origins, popups, cross-origin frames, login challenges, and profile ambiguity fail closed. |
| Coordinator hot-tree drift | HEAD, mailbox bodies, route, wave, capacity, and lock state are refreshed before send and before use. |

This review is advisory design-time evidence. It does not satisfy later
cross-model diff verification.

## 16. Files and responsibilities

| Path | Responsibility |
|---|---|
| `scripts/codex_protocol_model.py` | Canonical triggers, authority, transport, persistence, and reconciliation rules |
| `scripts/chatgpt_pro_consult.py` | Packet/response validation, rendering, hashes, idempotency metadata, and CLI manual relay |
| `.agents/skills/chatgpt-pro-consultation/SKILL.md` | Runtime decision and Browser-skill procedure |
| `AGENTS.md` | Concise project-level trigger and standing authorization boundary |
| `docs/protocol/codex/continuation.md` | Codex mode mapping and Desktop/CLI behavior |
| `.agents/skills/four-seat-protocol/SKILL.md` | Live protocol checklist integration |
| `.agents/skills/seat-director/SKILL.md` | Director planning trigger and authority boundary |
| `.agents/skills/seat-coordinator/SKILL.md` | Mailbox-first consultation and post-response refresh |
| `.agents/skills/seat-operator/SKILL.md` | Explicit non-substitution rule for Lane V |
| `.codex/agents/readiness-bridge.toml` | Readiness/idea-development behavior |
| `.codex/agents/protocol-director.toml` | Director trigger behavior |
| `.codex/agents/protocol-coordinator.toml` | Coordinator trigger and hot-tree checks |
| `.codex/agents/protocol-operator.toml` | Operator exclusion and distinct-question exception |
| `tests/unit/test_chatgpt_pro_consult.py` | Guard, schema, sanitizer, idempotency, stale-state, and CLI tests |
| `tests/unit/test_protocol_prompt_sync.py` | Canonical-to-mirror synchronization tests |
| `.gitignore` | Exclude non-content consultation runtime metadata |

The Browser plugin is an environment capability and is not copied into this
repository.

## 17. Test strategy

### 17.1 Packet guard tests

- Valid minimal request renders a deterministic prompt.
- Every field has exact type, enum, count, and byte limits.
- Canonical hashes are stable under JSON key ordering.
- Every secret/prohibited-source fixture fails closed.
- Unicode, split-line, encoded, and truncation bypass attempts fail closed.
- Untrusted excerpts cannot remove or override fixed instructions.
- No sensitive input appears in process arguments or state metadata.

### 17.2 Response tests

- Matching response validates.
- Mismatched ID/hash, stale binding, malformed JSON, unknown fields, bad types,
  and oversized output are rejected.
- Tool instructions, verdict language, and authorization claims remain inert
  strings and cannot trigger an action.

### 17.3 Idempotency and failure tests

- A second active send for the same key is rejected.
- Failed or timed-out sends do not retry automatically.
- A changed state binding produces a new key and stales the old result.
- Manual export/import works without a Browser skill.
- Runtime metadata contains no request or response content.

### 17.4 Protocol synchronization tests

- Canonical consultation phrases render from the executable model.
- Required phrases are present in the root rules, continuation guide, repo
  skills, and relevant Codex role prompts.
- Operator prompts explicitly deny Lane V substitution.
- Coordinator prompts require mailbox-first orientation and post-consultation
  refresh.

### 17.5 Browser acceptance checks

Browser UI behavior is verified manually against a test consultation because
CI has no authenticated browser session. Acceptance checks cover in-app send,
CLI-connected send, signed-out detection, partial response handling, fresh-chat
isolation, malformed output, and manual fallback. No production secrets or
private business data are used.

### 17.6 Completion verification

Implementation completion requires focused unit tests, the full Codex protocol
verification command named by the executable model, `scripts/ci_smoke.py`, a
repo-wide transcript/canary scan, and independent actual-diff review against
Section 15.

## 18. Rollout

1. Land the guard and its adversarial unit tests without enabling automatic
   browser sends.
2. Land the model-backed policy, skill, prompt mirrors, and sync tests.
3. Verify manual export/import from a bare CLI.
4. Verify one sanitized in-app-browser consultation and one configured CLI
   browser consultation.
5. Enable automatic attempts only after the guard, mirror checks, failure
   paths, and browser acceptance checks pass.

Rollback disables the automatic trigger while retaining explicit/manual
consultation. It does not remove decision records already incorporated into
approved artifacts.

## 19. Success criteria

The feature is complete when:

- consultation is explicitly invocable from every Codex mode;
- automatic triggers are model-backed and mirrored;
- Desktop and configured CLI use the same guarded packet contract;
- bare CLI can always export and import a correlated manual consultation;
- secret, injection, stale-state, duplicate-send, transcript, and authority
  tests pass;
- coordinator advice cannot bypass mailbox, capacity, hot-tree, or route gates;
- operator verification cannot claim ChatGPT Pro as Lane V evidence;
- raw transcripts do not appear in Git or protocol artifacts;
- material advice is recorded only as a sanitized disposition summary; and
- failure is explicit, bounded, and never represented as successful
  consultation.
