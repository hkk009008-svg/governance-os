"""Semantic tests for provenance-backed autonomous seat outcomes."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import subprocess

import pytest

import codex_protocol_model as model
import protocol_mailbox


FINDING_A = (
    "coordination/mailbox/sent/"
    "2026-07-18T06-05-32Z-operator-to-director-findings.md@" + "a" * 40
)
FINDING_B = "sha256:" + "b" * 64
PARENT = (
    "coordination/mailbox/sent/"
    "2026-07-18T04-37-59Z-coordinator-to-all-coordination.md@" + "c" * 40
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture
def event_repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Outcome Test")
    _git(tmp_path, "config", "user.email", "outcome@example.test")
    return tmp_path


def _event(
    repo: Path,
    *,
    sender: str,
    recipient: str,
    kind: str,
    timestamp: str,
    body: str,
) -> str:
    sent = repo / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / f"{timestamp}-{sender}-to-{recipient}-{kind}.md"
    iso_timestamp = timestamp[:11] + timestamp[11:19].replace("-", ":") + "Z"
    path.write_text(
        f"# {sender} → {recipient}: contract event\n\n"
        f"**When:** {iso_timestamp} · **From:** {sender} (online)\n\n"
        f"{body.rstrip()}\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    rel = path.relative_to(repo).as_posix()
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-q", "-m", f"{kind} from {sender}")
    return f"{rel}@{_git(repo, 'rev-parse', 'HEAD')}"


def _proposal_body(
    *,
    task_id: str = "task-1",
    parent: str = PARENT,
    revision: int = 2,
    previous: str = "director",
    proposed: str = "operator",
    outcome: str = "deliver tested behavior",
    findings: str = f"{FINDING_A}, {FINDING_B}",
) -> str:
    return "\n".join(
        (
            f"Task ID: {task_id}",
            f"Parent contract: {parent}",
            f"Contract revision: {revision}",
            f"Previous owners: {previous}",
            f"Proposed owners: {proposed}",
            f"Outcome: {outcome}",
            f"Finding refs: {findings}",
        )
    )


def _acceptance_body(
    proposal_ref: str,
    *,
    task_id: str = "task-1",
    parent: str = PARENT,
    revision: int = 2,
    previous: str = "director",
    proposed: str = "operator",
    outcome: str = "deliver tested behavior",
    findings: str = f"{FINDING_A}, {FINDING_B}",
) -> str:
    return _proposal_body(
        task_id=task_id,
        parent=parent,
        revision=revision,
        previous=previous,
        proposed=proposed,
        outcome=outcome,
        findings=findings,
    ) + f"\nProposal ref: {proposal_ref}"


def _contract(*, owners: tuple[str, ...] = ("director",)) -> model.OutcomeContract:
    return model.claim_outcome(
        task_id="task-1",
        contract_ref=PARENT,
        parent_ref=None,
        revision=1,
        outcome="deliver tested behavior",
        owners=owners,
        evidence_bar=("actual diff evidence",),
        hard_boundaries=("no self approval",),
        finding_refs=(FINDING_A, FINDING_B),
    )


def _normal_change(
    repo: Path,
    *,
    proposed: str = "operator",
    acceptance_senders: tuple[str, ...] = ("operator",),
) -> model.OwnershipChange:
    proposal_ref = _event(
        repo,
        sender="director",
        recipient="all",
        kind="proposal",
        timestamp="2026-07-18T07-00-00Z",
        body=_proposal_body(proposed=proposed),
    )
    proposal = protocol_mailbox.load_ownership_proposal_statement(repo, proposal_ref)
    acceptances = []
    for offset, sender in enumerate(acceptance_senders, start=1):
        ref = _event(
            repo,
            sender=sender,
            recipient="director",
            kind="proposal-reply",
            timestamp=f"2026-07-18T07-0{offset}-00Z",
            body=_acceptance_body(proposal_ref, proposed=proposed),
        )
        acceptances.append(protocol_mailbox.load_ownership_acceptance_statement(repo, ref))
    return model.OwnershipChange(
        task_id="task-1",
        parent_contract_ref=PARENT,
        revision=2,
        previous_owners=("director",),
        new_owners=tuple(part.strip() for part in proposed.split(",")),
        proposal=proposal,
        acceptances=tuple(acceptances),
        finding_refs=(FINDING_A, FINDING_B),
    )


def test_transfer_binds_current_parent_and_recipient_authored_acceptance(event_repo: Path):
    contract = _contract()
    change = _normal_change(event_repo)

    assert model.ownership_change_is_effective(contract, change)
    updated = model.apply_ownership_change(contract, change)
    assert updated.owners == ("operator",)
    assert updated.revision == 2
    assert updated.parent_ref == PARENT
    assert updated.contract_ref == change.proposal.event.ref


def test_unrelated_old_correct_sender_event_is_not_acceptance(event_repo: Path):
    change = _normal_change(event_repo)
    unrelated_ref = _event(
        event_repo,
        sender="operator",
        recipient="director",
        kind="proposal-reply",
        timestamp="2026-07-18T07-02-00Z",
        body=_acceptance_body(change.proposal.event.ref, task_id="other-task"),
    )
    unrelated = protocol_mailbox.load_ownership_acceptance_statement(
        event_repo, unrelated_ref
    )

    assert not model.ownership_change_is_effective(
        _contract(), replace(change, acceptances=(unrelated,))
    )


def test_stale_parent_forged_acceptance_and_active_incumbent_self_claim_fail(event_repo: Path):
    contract = _contract()
    change = _normal_change(event_repo)
    assert not model.ownership_change_is_effective(
        contract, replace(change, parent_contract_ref=PARENT.replace("c", "d"))
    )
    forged = replace(change.acceptances[0], event=replace(change.acceptances[0].event, sender="director2"))
    assert not model.ownership_change_is_effective(
        contract, replace(change, acceptances=(forged,))
    )
    wrong_proposal = replace(change.acceptances[0], proposal_ref=FINDING_A)
    assert not model.ownership_change_is_effective(
        contract, replace(change, acceptances=(wrong_proposal,))
    )
    caller_invented = replace(change.acceptances[0], _validated=None)
    assert not model.ownership_change_is_effective(
        contract, replace(change, acceptances=(caller_invented,))
    )
    self_claim = replace(change, proposal=replace(change.proposal, event=replace(change.proposal.event, sender="operator")))
    assert not model.ownership_change_is_effective(contract, self_claim)


def test_split_exchange_waits_for_every_new_owner(event_repo: Path):
    change = _normal_change(
        event_repo,
        proposed="operator, operator2",
        acceptance_senders=("operator",),
    )
    assert not model.ownership_change_is_effective(_contract(), change)

    second_ref = _event(
        event_repo,
        sender="operator2",
        recipient="director",
        kind="proposal-reply",
        timestamp="2026-07-18T07-03-00Z",
        body=_acceptance_body(change.proposal.event.ref, proposed="operator, operator2"),
    )
    second = protocol_mailbox.load_ownership_acceptance_statement(event_repo, second_ref)
    assert model.ownership_change_is_effective(
        _contract(), replace(change, acceptances=(*change.acceptances, second))
    )


def _takeover_change(repo: Path, *, task_id: str = "task-1", fresh: str = "none", lock: str = "none") -> model.OwnershipChange:
    observed = "2026-07-18T07:10:00Z"
    evidence_ref = _event(
        repo,
        sender="director2",
        recipient="all",
        kind="dispatch-claim",
        timestamp="2026-07-18T07-10-00Z",
        body="\n".join(
            (
                f"Task ID: {task_id}",
                f"Parent contract: {PARENT}",
                "Contract revision: 2",
                f"Observed at: {observed}",
                f"Fresh work state: {fresh}",
                f"Lock state: {lock}",
                f"Finding refs: {FINDING_A}, {FINDING_B}",
            )
        ),
    )
    evidence = protocol_mailbox.load_takeover_evidence_statement(repo, evidence_ref)
    return model.OwnershipChange(
        task_id="task-1",
        parent_contract_ref=PARENT,
        revision=2,
        previous_owners=("director",),
        new_owners=("director2",),
        proposal=None,
        acceptances=(),
        finding_refs=(FINDING_A, FINDING_B),
        abandoned_takeover=True,
        takeover_evidence=evidence,
    )


def test_abandoned_takeover_needs_fresh_work_and_lock_event_refs(event_repo: Path):
    assert model.ownership_change_is_effective(_contract(), _takeover_change(event_repo))


def test_stale_or_unrelated_work_and_lock_evidence_is_rejected(event_repo: Path):
    contract = _contract()
    assert not model.ownership_change_is_effective(
        contract, _takeover_change(event_repo, task_id="other-task")
    )
    assert not model.ownership_change_is_effective(
        contract, _takeover_change(event_repo, fresh="present")
    )
    assert not model.ownership_change_is_effective(
        contract, _takeover_change(event_repo, lock="active")
    )


def test_ownership_change_cannot_drop_or_reorder_finding_refs(event_repo: Path):
    change = _normal_change(event_repo)
    assert not model.ownership_change_is_effective(
        _contract(), replace(change, finding_refs=(FINDING_A,))
    )
    assert not model.ownership_change_is_effective(
        _contract(), replace(change, finding_refs=(FINDING_B, FINDING_A))
    )
    reordered_proposal = replace(change.proposal, finding_refs=(FINDING_B, FINDING_A))
    assert not model.ownership_change_is_effective(
        _contract(), replace(change, proposal=reordered_proposal)
    )


def test_finding_is_advisory_unless_hard_boundary_is_unresolved():
    assert model.finding_state(hard_boundary_unresolved=False) == "FINDING"
    assert model.finding_state(hard_boundary_unresolved=True) == "BLOCKED"


def _review(**changes: object) -> model.ReviewDecision:
    values = {
        "task_id": "task-1",
        "author_seat": "director",
        "author_model": "gpt-author",
        "reviewer_seat": "operator",
        "reviewer_model": "gpt-reviewer",
        "reviewed_base": "1" * 40,
        "reviewed_head": "2" * 40,
        "verdict": "GO",
        "finding_refs": (FINDING_A, FINDING_B),
        "finding_dispositions": ((FINDING_A, "addressed"), (FINDING_B, "accepted risk")),
    }
    values.update(changes)
    return model.ReviewDecision(**values)


def test_review_rejects_equal_seat_or_equal_model():
    contract = _contract()
    assert model.review_accepts_outcome(contract, _review())
    assert not model.review_accepts_outcome(
        contract, _review(author_seat="operator")
    )
    assert not model.review_accepts_outcome(
        contract, _review(reviewer_model=" GPT-AUTHOR ")
    )


def test_operator_to_operator2_same_model_is_rejected():
    contract = _contract(owners=("operator",))
    decision = _review(
        author_seat="operator",
        reviewer_seat="operator2",
        author_model="same-model",
        reviewer_model="SAME-MODEL",
    )
    assert not model.review_accepts_outcome(contract, decision)


def test_review_requires_exact_range_and_every_finding_disposition():
    contract = _contract()
    assert not model.review_accepts_outcome(
        contract, _review(reviewed_base="1" * 39)
    )
    assert not model.review_accepts_outcome(
        contract,
        _review(finding_dispositions=((FINDING_A, "addressed"),)),
    )
    assert not model.review_accepts_outcome(
        contract,
        _review(finding_dispositions=((FINDING_B, "accepted"), (FINDING_A, "addressed"))),
    )


def test_external_token_completeness_does_not_create_authority():
    result = model.external_effect_token_is_complete(
        model.ExternalEffectToken(
            effect="push",
            executor="director",
            target="origin/main",
            scope=("commit:abc",),
        )
    )
    assert result.complete
    assert result.explicit_external_user_authorization_required
    assert not result.execution_authorized


def test_structurally_complete_seat_token_still_requires_external_user_authority():
    result = model.external_effect_token_is_complete(
        model.ExternalEffectToken(
            effect="ledger-resume",
            executor="operator",
            target="evidence-ledger/main",
            scope=("resume-checkpoint",),
        )
    )
    assert result.complete
    assert result.explicit_external_user_authorization_required is True
    assert result.execution_authorized is False


@pytest.mark.parametrize(
    "token",
    [
        model.ExternalEffectToken("", "director", "origin/main", ("one",)),
        model.ExternalEffectToken("push", "unknown", "origin/main", ("one",)),
        model.ExternalEffectToken("push", "director", "*", ("one",)),
        model.ExternalEffectToken("push", "director", "origin/main", ()),
    ],
)
def test_external_token_rejects_incomplete_or_broadened_shape(token: model.ExternalEffectToken):
    result = model.external_effect_token_is_complete(token)
    assert not result.complete
    assert result.explicit_external_user_authorization_required
    assert not result.execution_authorized
