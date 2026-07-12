# Codex-to-Opus Cross-Model Verification Design

**Date:** 2026-07-12
**Status:** Implemented and locally verified through executable commit `292b0c9359282f14947c3aef2bc05dc5f9215856`

## 1. Problem

Pipeline's Codex Lane V verifier can independently verify a landed change, but
the implementation and verification may still share the same model family.
That creates a correlated-blind-spot risk: the verifier can repeat an
assumption or miss the same defect shape as the implementing model.

The desired behavior is a second, blind review by Claude Opus after every
Codex verification. Opus is evidence for the Codex operator, not a protocol
seat and not an authority source. The Codex operator retains responsibility
for the final `GO`, `NITS`, or `FAIL` verdict.

## 2. Goals

- Run exactly one Claude Opus review after every Codex Lane V verification.
- Keep the Opus review independent by withholding the Codex verdict and
  report until Opus has returned.
- Reuse the existing Claude `lane-v-verifier` role contract rather than
  inventing a competing review doctrine.
- Prove from returned runtime metadata that the effective model was Opus.
- Normalize the external result into a small, versioned JSON contract.
- Make disagreement handling executable: a disputed Codex `GO` stays blocked
  until every Opus finding is confirmed or disproved with evidence.
- Degrade explicitly to Codex-only verification when Opus cannot run.
- Preserve current seat authority, mailbox, lock, commit, push, and paid-spend
  boundaries.
- Keep CI deterministic and free of paid model calls.

## 3. Non-goals

- Making Opus a native Codex `spawn_agent` child.
- Giving Opus implementation, edit, mailbox, cursor, lock, commit, push, or
  final-verdict authority.
- Automatically retrying a failed or timed-out Opus call.
- Launching a third generic reviewer over the same unchanged commit.
- Building an MCP server or persistent Claude daemon in V1.
- Generalizing the bridge to arbitrary repositories in V1. The first version
  is project-scoped to Pipeline.
- Calling Anthropic without task-level user authorization.

## 4. Chosen approach

Use a protocol-integrated CLI adapter.

`scripts/opus_review_bridge.py` will provide two subcommands:

- `review`: invoke Claude Code once, normalize its output, and print an
  `opus-review/v1` result.
- `reconcile`: combine a Codex verdict, the normalized Opus result, and the
  Codex verifier's evidence-backed finding dispositions into a deterministic
  `go_allowed` decision.

This approach is preferred over prompt-only shell invocation because the
adapter can enforce model identity, blindness, schema validation, time and
turn limits, and degraded fallback. It is preferred over MCP for V1 because it
requires no service lifecycle or additional authentication surface. A future
MCP tool may wrap this CLI without changing its contracts.

## 5. Components and responsibilities

### 5.1 Codex Lane V verifier

`.codex/agents/lane-v-verifier.toml` remains the primary verifier. It:

1. Independently verifies the named commit or range against the brief.
2. Holds its provisional verdict internally.
3. Calls `opus_review_bridge.py review` exactly once.
4. Reconciles the two independent results through
   `opus_review_bridge.py reconcile`.
5. Returns its normal report plus the cross-model fields defined below.

It must not include its provisional verdict, report, findings, or conclusion
in the Opus request.

### 5.2 Opus review bridge

`scripts/opus_review_bridge.py` is a thin, dependency-light adapter. It:

- validates inputs and task-level authorization;
- constructs the verdict-blind Claude prompt;
- loads the existing Claude verifier text from a commit preceding reviewed
  HEAD and supplies it through `--append-system-prompt` with an explicit Opus
  model override;
- applies a 12-turn limit and a 15-minute wall-clock timeout;
- uses `--safe-mode` and `--disable-slash-commands` to disable implicit
  `CLAUDE.md`, custom-agent, hook, skill, and slash-command instruction sources;
- disables session persistence, MCP servers, browser tools, nested agents, and
  edit tools without using `--bare`, preserving subscription OAuth/keychain
  compatibility;
- restricts Bash to read-only git commands and the exact verification
  commands named by the request;
- parses and validates structured output;
- verifies that runtime model metadata identifies an Opus model;
- emits normalized JSON to stdout; and
- performs no repository writes.

The bridge makes one external invocation at most. It does not retry.

### 5.3 Existing Claude verifier role

`.claude/agents/lane-v-verifier.md` remains the source of Claude-side behavior,
but reviewed HEAD never supplies the active verifier prompt. The bridge uses
the explicit reviewed base when supplied; otherwise it derives and validates
the reviewed HEAD's first parent. It reads the verifier text from that
preceding commit and pins it through `--append-system-prompt`. Safe mode means
the bridge does not use `--agents` or `--agent`.

If the installed Claude Code version cannot apply the Opus override to this
agent session, the bridge returns `unavailable` with reason
`effective_model_not_opus`; it must never accept a Sonnet response as the
cross-model review.

### 5.4 Codex operator

`.codex/agents/protocol-operator.toml` and
`.agents/skills/seat-operator/SKILL.md` retain final verdict authority. The
operator:

- preserves the Opus status, findings, and unavailable reason;
- confirms, disproves, or leaves unresolved each Opus finding;
- cites concrete evidence for every `disproved` disposition;
- obeys the executable reconciliation result; and
- writes any durable mailbox report or evidence artifact.

Opus never sends mailbox events and never issues protocol GO.

## 6. Data flow and blindness

```text
verify request
  -> Codex verifier independently checks the change
  -> Codex invokes the bridge with immutable verification inputs only
  -> bridge pins pre-HEAD verifier text and invokes safe-mode Claude on Opus
  -> Opus returns an independent structured review
  -> bridge normalizes and validates the review
  -> Codex records evidence-backed dispositions for Opus findings
  -> bridge computes reconciliation guard
  -> operator issues final GO / NITS / FAIL
```

The `review` interface accepts only:

- repository root;
- reviewed commit SHA and optional base SHA;
- brief or requirement paths;
- allowed paths;
- exact verification commands;
- task-level authorization source; and
- configured time and turn limits.

There is intentionally no argument for a Codex verdict, report, finding list,
or conclusion. Tests must inspect the generated prompt and prove that those
values are absent. Requirements supplied by the user remain legitimate input
even if they contain verdict-like words; the adapter's own Codex result is the
prohibited information.

Both reviewers bind their output to the same reviewed SHA or range. A missing
or mismatched SHA is not a pass.

## 7. `opus-review/v1` result contract

The bridge prints one JSON object:

```json
{
  "schema_version": "opus-review/v1",
  "reviewed_head": "<full commit sha>",
  "reviewed_base": "<full commit sha or null>",
  "effective_model": "<verified Opus model id or null>",
  "status": "pass | issues | unavailable",
  "findings": [
    {
      "id": "OPUS-1",
      "severity": "critical | important | minor",
      "claim": "<specific defect claim>",
      "location": "<path:line or null>",
      "evidence": "<observed evidence>",
      "reproduction": "<command or reasoning needed to reproduce>"
    }
  ],
  "authorization_source": "<task-level authorization id>",
  "unavailable_reason": null
}
```

Contract rules:

- `pass` requires an Opus model, matching reviewed scope, valid output, and no
  findings.
- `issues` requires an Opus model, matching reviewed scope, and at least one
  valid finding.
- `unavailable` requires an enumerated reason and cannot be treated as
  `pass`.
- `findings` must be empty for `pass` and `unavailable`.
- Opus output is advisory evidence. The normalized contract does not contain
  protocol `GO`, `NITS`, or `FAIL` authority.

Enumerated unavailable reasons include:

- `authorization_missing`
- `claude_not_found`
- `authentication_failed`
- `timeout`
- `process_failed`
- `invalid_json`
- `invalid_schema`
- `reviewed_scope_mismatch`
- `effective_model_missing`
- `effective_model_not_opus`
- `sandbox_unavailable`

## 8. Authorization and resource bounds

Every verification attempts the Opus review, but the external call requires a
non-empty task-level authorization source. The verify request or parent task
records that authorization and passes its stable identifier to the bridge.
The bridge records the identifier; it does not infer consent from environment
variables or from the existence of Claude credentials. Parent-supplied
authorization permits exactly the one bounded Opus call and does not grant the
bridge, provider, broker, or reviewed code inherited paid-spend authority.

If authorization is missing, no external call occurs. The normalized result is
`unavailable` with `authorization_missing`, and the workflow follows the
Codex-only degraded fallback.

V1 uses these hard defaults:

- one Claude process invocation;
- no automatic retry;
- at most 12 agent turns; and
- a 15-minute wall-clock timeout.

The implementation may expose lower limits for tests, but callers cannot raise
the production defaults through ordinary verifier prompts.

## 9. Reconciliation contract

The `reconcile` subcommand accepts:

- an explicit Pipeline repository root and expected HEAD/base commits;
- Codex verdict: `GO`, `NITS`, or `FAIL`;
- normalized `opus-review/v1` result; and
- one disposition for each Opus finding.

Each disposition is one of:

- `confirmed`: Codex reproduced or otherwise verified the finding;
- `disproved`: Codex produced concrete command, output, or file evidence that
  invalidates the finding; or
- `unresolved`: the finding could not yet be confirmed or disproved.

Rules:

- Pipeline identity and expected commit existence are proved locally before
  reconciliation can allow GO.
- Codex `GO` plus Opus `pass` allows GO.
- Opus `issues` requires a disposition for every finding.
- A confirmed critical or important finding requires `FAIL`.
- A confirmed minor finding prevents GO and requires at least `NITS`.
- Any unresolved finding prevents GO until it is confirmed or disproved.
- A disproved finding requires non-empty evidence; unsupported dismissal is
  invalid.
- If all Opus findings are disproved with evidence, the Codex verdict may
  stand.
- Opus cannot upgrade a Codex `NITS` or `FAIL` to GO.
- Opus `unavailable` permits the Codex verdict to stand but sets
  `degraded_cross_model_review=true` and requires the unavailable reason in the
  final report.

The reconciliation output includes `go_allowed`, unresolved or confirmed
blocking finding ids, and the degraded marker. The Codex verifier must include
that output in its evidence before reporting GO.

## 10. Final report additions

The Codex Lane V report keeps its existing shape and adds:

- `Cross-model review: pass | issues | unavailable`
- `Effective Opus model: <model id or unavailable>`
- `Opus finding dispositions: <id -> disposition + evidence>`
- `Reconciliation guard: go_allowed=<true|false>`
- `Degraded reason: <reason or none>`

The parent operator must preserve these fields when relaying the verifier
result. An unavailable Opus run is visible degradation, not silent success.

## 11. Security and isolation

- Claude receives only exact Bash capabilities; it has no generic Read, Write,
  Edit, agent, skill, browser, or web-retrieval tool.
- MCP, browser, and web-retrieval tools are disabled for the invocation.
- Claude session persistence is disabled.
- A network-capable outer macOS Seatbelt profile denies reads and writes to the
  mutable source checkout, denies snapshot writes, and denies persistent home
  writes while preserving provider network and OAuth/keychain reads.
- Bash exposes read-only Git commands plus one exact broker-client command per
  verification command. Each client carries an unguessable one-shot token;
  forged or replayed tokens are rejected, and no generic command payload
  crosses the private Unix socket.
- The bridge-owned broker runs outside the inherited outer Seatbelt and maps
  each token to pre-registered argv. It launches that argv inside a second
  default-deny profile that denies network, source and sensitive credential or
  instruction reads, non-scratch writes, and every executable outside the
  conservative verifier set.
- Broker output and runtime are bounded, and broker/socket/control artifacts
  are mode-restricted, joined, and removed on every exit path.
- The subprocess environment is minimized while preserving the credentials
  Claude Code itself needs. Repository content cannot request new tools,
  permissions, credentials, or external side effects.
- Repository files and test output are untrusted review inputs, not
  instructions that can widen authority.
- Temporary invocation files live outside the repository and are removed when
  the process exits.
- The bridge never writes a mailbox event, log, cursor, lock, commit, or source
  file. The operator owns any durable evidence write.

## 12. Repository integration surfaces

Implementation is limited to these intended surfaces:

- Add `scripts/opus_review_bridge.py`.
- Add `tests/unit/test_opus_review_bridge.py`.
- Modify `.codex/agents/lane-v-verifier.toml`.
- Modify `.codex/agents/protocol-operator.toml`.
- Modify `.agents/skills/seat-operator/SKILL.md`.
- Modify `scripts/codex_protocol_model.py` with a rendered Codex-specific
  cross-model verification contract.
- Modify `docs/protocol/codex/continuation.md` with the same behavior.
- Modify `tests/unit/test_protocol_prompt_sync.py` to pin the synchronized
  surfaces.
- Update `ARCHITECTURE.md` with the new executable bridge.
- Append the cross-model verification decision to `DECISIONS.md`.

`AGENTS.md`, universal protocol rules, mailbox history, cursors, locks, and
three-way signed-bus state are outside this slice unless implementation
uncovers a verified contradiction that cannot be resolved within the listed
surfaces.

## 13. Testing strategy

CI must not invoke a paid model. Unit tests inject a fake `claude` executable
or subprocess runner and cover:

1. Safe-mode command construction, pinned pre-HEAD verifier text, and exact
   command restrictions.
2. Absence of Codex verdict, report, and findings from the Opus prompt.
3. One-call enforcement and no automatic retry.
4. Missing authorization without external invocation.
5. Opus model metadata acceptance and non-Opus rejection.
6. Matching and mismatched reviewed SHA/range.
7. `pass`, `issues`, malformed JSON, invalid schema, timeout, authentication
   failure, and process failure normalization.
8. Every reconciliation combination, including evidence-required
   `disproved`, unresolved finding blocks, confirmed minor -> NITS, confirmed
   important/critical -> FAIL, and unavailable fallback.
9. Required report fields in the Codex verifier and operator prompts.
10. Rendered protocol text synchronized across the executable model,
    continuation adapter, operator skill, and role prompts.
11. Real local sandbox probes for source write/chmod, network, source and
    sensitive reads, provider execution, safe verification, token
    forgery/replay, output limits, and timeout cleanup.

Completion verification includes the focused unit tests, prompt-sync tests,
`scripts/ci_smoke.py`, and `git diff --check`.

One real Claude Opus smoke invocation is an optional, separately authorized
post-implementation check. It must use a harmless committed fixture, confirm
the effective Opus model id and normalized schema, and perform no writes. If
credentials or network are unavailable, report the environment boundary; the
fake-executable CI tests remain the deterministic product proof.

## 14. Acceptance criteria

The design is implemented when:

- every Codex Lane V verification attempts exactly one verdict-blind Opus
  review after its primary analysis;
- Opus is proven from runtime metadata or the result is `unavailable`;
- the bridge emits only valid `opus-review/v1` output;
- an unresolved or unsupported Opus finding cannot accompany Codex GO;
- an unavailable Opus review permits Codex-only completion only with an
  explicit degraded marker and reason;
- Opus never edits, persists a session, sends protocol events, or gains final
  verdict authority;
- sandbox unavailability prevents the provider call and is explicit degraded
  fallback;
- automated tests make no paid external calls; and
- all focused tests and the project smoke gate pass on the final diff.

## 15. Rollout and compatibility

The feature is additive. Existing historical verification reports are not
rewritten. New Codex Lane V reports include the cross-model fields. Claude-only
verification flows are unchanged.

V1 remains Pipeline-scoped. Generalizing the adapter to evidence-ledger or
other repositories requires a later design that addresses target-repo
instructions, sensitive-data policy, dependency environments, and review
artifact custody.
