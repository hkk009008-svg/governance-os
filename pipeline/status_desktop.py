"""Compact desktop-team readiness collection and rendering."""

from __future__ import annotations

from pathlib import Path

from status_team_store import TEAM_MEMBERS


def _readiness_rows(results: list) -> dict[str, dict]:
    return {
        result.harness: {
            "ready": result.ok,
            "detail": result.detail,
            "remedy": result.remedy or None,
        }
        for result in results
    }


def collect_desktop_readiness(repo_root: Path) -> dict:
    """Inspect installed apps/configs without running an MCP handshake."""

    try:
        import harness_preflight  # type: ignore

        apps = _readiness_rows(harness_preflight.check_apps())
        manifests = _readiness_rows(harness_preflight.check_team_configs(repo_root))
    except Exception as exc:
        return {
            "state": "unavailable",
            "ready": None,
            "apps": {},
            "manifests": {},
            "detail": str(exc),
            "live_handshake": "not-run",
        }
    complete = set(apps) == set(TEAM_MEMBERS) and set(manifests) == set(TEAM_MEMBERS)
    ready = complete and all(
        row["ready"] for row in (*apps.values(), *manifests.values())
    )
    return {
        "state": "ready" if ready else "needs-attention",
        "ready": ready,
        "apps": apps,
        "manifests": manifests,
        "detail": (
            "static app and project-config checks passed"
            if ready
            else "one or more app/config checks failed"
        ),
        "live_handshake": "not-run; use `bin/pipeline preflight`",
    }


def _readiness_labels(rows: dict) -> str:
    return " ".join(
        f"{member}={'ready' if rows.get(member, {}).get('ready') else 'FAIL'}"
        for member in TEAM_MEMBERS
    )


def render_orientation_snapshot(snapshot: dict) -> str:
    """Render the default desktop-team view in at most twenty lines."""

    git = snapshot["git"]
    desktop = snapshot["desktop"]
    transport = snapshot["team_transport"]
    lines = [
        f"Pipeline desktop-team snapshot {snapshot['generated_at']}",
        f"Git: {git['sha']} branch={git['branch']} dirty={git['dirty']}",
    ]
    if desktop["state"] == "unavailable":
        lines.append(f"Desktop readiness: unavailable ({desktop['detail']})")
    else:
        lines.append(f"Apps: {_readiness_labels(desktop['apps'])}")
        lines.append(f"App configs: {_readiness_labels(desktop['manifests'])}")
        failed = [
            row
            for group in (desktop["apps"], desktop["manifests"])
            for row in group.values()
            if not row["ready"]
        ]
        lines.append(
            f"Readiness issue: {failed[0]['detail']}"
            if failed
            else "Live handshakes: not run (use `bin/pipeline preflight`)"
        )
    if transport["state"] == "ready":
        registered = ",".join(sorted(transport["members"])) or "none"
        pending = " ".join(
            f"{member}={transport['pending'][member]}" for member in TEAM_MEMBERS
        )
        lines.extend(
            [
                f"Team transport: ready registered={registered} pending[{pending}]",
                "Messages: "
                f"queued={transport['queued_messages']} "
                f"acknowledgement-receipts={transport['acknowledgement_receipts']} "
                f"reply-messages={transport['reply_messages']}",
            ]
        )
    elif transport["state"] == "absent":
        lines.append("Team transport: not initialized (status did not create it)")
    else:
        lines.append(
            f"Team transport: unavailable ({transport.get('detail', 'unknown error')})"
        )
    review = snapshot.get("formal_review")
    if review is not None:
        current = review.get("current_request")
        failed = review.get("failed_review")
        blocker = review.get("blocker")
        if blocker:
            lines.append(f"Formal review: BLOCKED ({blocker})")
        elif current is not None:
            commit = current.get("commit") or "uncommitted"
            lines.append(
                f"Formal review: pending {current['path']}@{commit} "
                f"assigned={current['assigned_operator']}"
            )
        elif failed is not None:
            lines.append(
                f"Formal review: failed {failed['report_path']}@"
                f"{failed['report_commit']}"
            )
        else:
            lines.append("Formal review: none")
        gate = review["gate"]
        lines.append(
            f"Formal gate: {gate['status']} ({gate['fatal']} fatal, "
            f"{gate['advisory']} advisory, "
            f"{gate.get('failed_review', 0)} failed)"
        )
    rendered = "\n".join(lines) + "\n"
    if len(rendered.splitlines()) > 20:
        raise ValueError("orientation snapshot exceeded the 20-line contract")
    return rendered
