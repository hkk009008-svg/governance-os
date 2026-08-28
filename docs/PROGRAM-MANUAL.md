# Pipeline program manual

## Mission

Pipeline is the proportional governance and communication layer for a
three-member desktop-app engineering team: Codex, Claude, and AGY. It maximizes
their combined capability by enabling direct collaboration while keeping task
scope, review independence, and external effects explicit.

ARCHITECTURE.md records verified governance-kernel truth. Executable code,
fresh Git state, and executed evidence outrank prose if they diverge.

## Program invariants

1. The three desktop apps are the only interactive members. All may direct,
   reason, implement, test, and challenge.
2. Pipeline does not launch a model provider from the terminal and does not run
   one app as a headless child of another.
3. Routine communication uses the three MCP tools: `team_status`, `team_send`,
   and `team_wait`.
4. Queued, returned, acknowledged, replied, and substantively answered are different facts.
5. Transport never grants task, review, permission, or effect authority.
6. Ordinary work is direct. There are no standing seats or coordinator role.
7. Read-only and file-disjoint work may run in parallel; shared-file and shared
   resource writes are serialized.
8. Formal author/reviewer responsibilities exist only for a risk-triggered
   exact range and end with that review.
9. AGY is fully heard as an engineering member but cannot be the sole
   independent formal verdict or an authority source.
10. Push, merge, release, paid spend, live mutation, and destructive operations
    need exact current task/user authority.
11. Git, tests, and app task history are normal state. One checkpoint is used
    only for a real transfer or continuation boundary.
12. Legacy mailbox conversation, cursors, seats, capacity, and peer receipts
    are compatibility history; the fixed writer remains only for three
    narrowly governed uses: a required formal review artifact, a real
    transfer/checkpoint `findings` event, or the governed
    learning-candidate/disposition lifecycle.

## Control flow

```text
accepted task
  -> inspect current repository and team state
  -> direct work or bounded parallel split
  -> focused evidence and exact diff
  -> risk classification
       ordinary-local    -> finish
       material-behavior -> temporary non-author exact-range review
       high-risk-control -> different-family review + abuse assessment
  -> exact external-effect authority, only if an effect is requested
  -> result or one real-transfer checkpoint
```

The program deliberately has no mandatory brainstorming stage, readiness role,
role board, mailbox event, capacity packet, or review artifact for ordinary
work. Add structure only when it answers a real ambiguity or enforces a real
risk boundary.

## Communication plane

The checked-in project bindings supply one normal member label per app. AGY's
binding is a workspace plugin with a `plugin.json` manifest and
`mcp_config.json`; the other apps use their native project MCP config. The
shared MCP server validates labels, recipients, message size, idempotency,
replies, cursors, and bounded waits. Labels are not app or model attestation.
Its SQLite store lives under the Git common directory so linked worktrees share
state without committing messages.

`team_status` is orientation and sent-state inspection. `team_send` queues a
message. `team_wait` returns messages after an explicit caller cursor; a later
call that advances the cursor acknowledges addressed messages through it. A
reply link records relationship, not quality.
Every response states that it grants no authority.

Routine in-task messages are allowed without separate provider or spend
approval because the desktop sessions already exist; the transport launches no
provider. A communication failure is reported or retried through the app, not
worked around with a CLI provider launcher or human relay.

## Capability strategy

The program routes rather than partitions capability:

- Codex commonly supplies workspace execution, integration, orchestration, and
  long-running follow-through.
- Claude commonly supplies large-context synthesis, architecture, independent
  diff review, and visual evaluation.
- AGY commonly supplies rapid mapping/debugging, browser and artifact work,
  premise/evasion challenge, isolated experiments, and multi-model advice.

Any member may lead and implement. Weakness reduction is evidence-based:
analysis must meet current code, rapid advice must survive local reproduction,
parallel contributions must meet an integrator, and high-risk authored work
must meet a different model family. AGY findings are judged by evidence and
explicitly dispositioned when material.

## Governance plane

The closed classes in `pipeline/codex_protocol_model.py` are:

| Class | Required control |
|---|---|
| `ordinary-local` | focused verification |
| `material-behavior` | focused verification plus non-author exact-range review |
| `high-risk-control` | material controls plus different-family review and abuse-class assessment |
| `external-effect` | exact live authority for executor, target, effect, and scope |

Formal review is implemented by `pipeline/compact_pair_loop.py`. Temporary
`author` owns the candidate; temporary `reviewer` is a non-author Codex or
Claude member and owns the formal result. AGY may supply first-class evidence
but is not accepted as the only formal verdict. Review does not grant an
external effect.

## State plane

The current user task defines scope. Git records the candidate. Tests record
executed behavior. Desktop task history records the working conversation. A
formal report, when required, binds the exact range. These are sufficient for
normal work.

A checkpoint is exceptional: use one only when another member must resume
after transfer, interruption, compaction, or wrap. It contains objective,
scope, owner, base/head, evidence, verification state, blockers, and next
action. It is not a replacement for Git or task history.

Historical mailbox conversation, cursors, seat names, capacity packets,
handoffs, and peer receipts remain readable for audit and backwards-compatible
validation. The fixed mailbox writer persists only three narrowly governed
uses: a risk-required exact-range formal review artifact, a real
transfer/checkpoint `findings` event, or the governed
learning-candidate/disposition lifecycle. It is not routine transport and
cannot create a live role or authority.

## Executable seams

| Concern | Code |
|---|---|
| Command dispatch | `bin/pipeline`, `pipeline/cli.py` |
| App MCP server | `pipeline/team.py`, `pipeline/team_mcp.py` |
| Message semantics | `pipeline/team_messages.py` |
| Secure store | `pipeline/team_store.py` |
| App/config handshake | `pipeline/harness_preflight.py` |
| Native config/workspace checks and AGY permission | `pipeline/native_app_readiness.py` |
| Risk, model family, effects | `pipeline/codex_protocol_model.py` |
| Exact-range formal review | `pipeline/compact_pair_loop.py` |
| Target selection | `pipeline/target_binding.py` |
| Verification | `pipeline/`, `tests/`, `bin/pipeline check` |

Controls establish only what their call path observes. Preflight does not prove
an app is open. A green test does not prove user intent. Model-family diversity
does not create authority. Documentation cannot claim a gate that code does not
enforce.

## Change policy

Prefer deleting or simplifying duplicate doctrine to adding another layer.
Keep app adapters thin and universal rules centralized. A new transport, role,
provider launcher, or durable state surface needs demonstrated necessity and
high-risk review; convenience alone is not sufficient.
