# Headless review dispatch

Pipeline supports a headless Codex capability check. Claude review uses its
normal continuation adapter and host session tools; readiness in either host
never grants launch, publication, commit, push, merge, or spend authority.

## Codex preflight

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/harness_preflight.py codex
```

The preflight checks that the binary exists, that repository configuration
does not grant ambient sandbox/approval capability, and that the invocation
contract is explicit. A live probe is a separately authorized provider launch.

```bash
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
PIPELINE_GIT_DIR="$(git rev-parse --absolute-git-dir)"
codex exec -C "$PIPELINE_ROOT" --sandbox workspace-write \
  -c approval_policy="never" --add-dir "$PIPELINE_GIT_DIR" \
  "<brief>" < /dev/null
```

`< /dev/null` prevents an inherited open pipe from blocking startup.
`--add-dir` is required only when the separately authorized task must write
Git metadata. Pin sandbox and approval policy per invocation, never in the
checked-in project config.

## Review binding

Name the committed request and exact range; never ask a reviewer to inspect an
unbound moving `HEAD`. Ask it to falsify test-quality and abuse-boundary claims.
Formal acceptance still requires the Compact Pair request/report, the assigned
non-author seat, and the risk-class requirements. A high-risk-control change
also requires a recognized different model family and explicit abuse-class
assessment.

For a Codex-authored high-risk-control range, route the review to an explicitly
assigned Claude Operator through the normal Claude continuation path. For a
Claude-authored range, route it to Codex. The host transition does not itself
publish the verdict or authorize any effect.
