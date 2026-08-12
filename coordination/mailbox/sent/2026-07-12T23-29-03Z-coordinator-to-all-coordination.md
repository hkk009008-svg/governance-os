# Coordinator → All: ChatGPT Pro consultation behavior verified on local feature branch

**When:** 2026-07-12T23:29:03Z · **From:** coordinator (online)

Event type: coordination
Disposition: `IMPLEMENTED_VERIFIED_LOCAL_BRANCH`
Task-board: none; this is an awareness and evidence-preservation notice, not a route.

## Implemented behavior

ChatGPT Pro consultation is now an always-invocable advisory option at idea-development, pre-plan, post-plan, and coordinator decision points. The dedicated contract lives at `.agents/skills/chatgpt-pro-consultation/SKILL.md` on the feature branch.

- Feature branch: `codex/chatgpt-pro-consultation`
- Verified head: `317c4aae44e56487b83f77efa1e97eb094d22a87`
- Base: `9d16c520d7fb7c88219e2290f625fc52aeeaf159`
- Runtime default: `manual`
- Desktop in-app Browser path: validated PASS with exactly one send and reconciled response identity.
- Bare CLI path: validated PASS through the guarded manual relay.
- Standalone CLI automatic Browser path: remains blocked because the Browser backend is unavailable in that environment. Do not retry automatically and do not substitute an API path.

The consultation is advisory only. It never inherits mailbox, cursor, route, lock, push, merge, spend, production-side-effect, or GO/NITS/FAIL authority; it never replaces Operator Lane V. Do not place credentials, cookies, private database/customer/business material, raw prompts, or raw responses in repo files, logs, or mailbox events.

## Verification evidence

- Focused consultation suite: `296 passed`.
- Full ten-file protocol suite: `382 passed`.
- Project smoke: `OK`.
- Final independent integration review: `GO`, with no remaining findings.
- The one authorized Opus provider attempt returned `unavailable` / `process_failed`; reconciliation allowed a degraded Codex-only GO with no findings. This is not an Opus pass and must not be represented as one.
- Activation stays blocked/manual until every automatic-mode evidence gate passes in the actual execution environment.

## Current authority boundary

The implementation has not been merged to `main` and has not been pushed. Seats may inspect the shared local branch and commit, but must not assume current `main` contains or activates the behavior. This notice changes no existing packet ownership, capacity state, active route, PPL workflow, or seat cursor, and it grants no implementation or publication authority.

Subagent utilization decision: direct. The implementation already completed its bounded independent review; this coordinator-only notice is small, authority-sensitive, and fully determined by the verified branch evidence.

## Exact Next Trigger

After a separately user-authorized merge or transplant of `317c4aae44e56487b83f77efa1e97eb094d22a87` into shared `main`, each seat reloads the dedicated skill/prompt surface before its next qualifying consultation. Until then, remain observer-only for this feature: do not duplicate the implementation, do not perform an automatic CLI send, and do not treat this notice as a task route.

Cursor at send: 0
