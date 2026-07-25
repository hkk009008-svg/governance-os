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
    previous: str = "director",
    proposed: str = "operator",
    acceptance_senders: tuple[str, ...] = ("operator",),
) -> model.OwnershipChange:
    proposal_ref = _event(
        repo,
        sender="director",
        recipient="all",
        kind="proposal",
        timestamp="2026-07-18T07-00-00Z",
        body=_proposal_body(previous=previous, proposed=proposed),
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
            body=_acceptance_body(
                proposal_ref,
                previous=previous,
                proposed=proposed,
            ),
        )
        acceptances.append(protocol_mailbox.load_ownership_acceptance_statement(repo, ref))
    return model.OwnershipChange(
        task_id="task-1",
        parent_contract_ref=PARENT,
        revision=2,
        previous_owners=tuple(part.strip() for part in previous.split(",")),
        new_owners=tuple(part.strip() for part in proposed.split(",")),
        proposal=proposal,
        acceptances=tuple(acceptances),
        finding_refs=(FINDING_A, FINDING_B),
    )


def test_transfer_binds_current_parent_and_recipient_authored_acceptance(event_repo: Path):
    contract = _contract()
    change = _normal_change(event_repo)

    assert model.ownership_change_is_effective(contract, change, root=event_repo)
    updated = model.apply_ownership_change(contract, change, root=event_repo)
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
        _contract(), replace(change, acceptances=(unrelated,)), root=event_repo
    )

    forged = replace(
        unrelated,
        task_id=change.task_id,
        parent_ref=change.parent_contract_ref,
        revision=change.revision,
        previous_owners=change.previous_owners,
        proposed_owners=change.new_owners,
        proposal_ref=change.proposal.event.ref,
        outcome=change.proposal.outcome,
        finding_refs=change.finding_refs,
    )
    assert not model.ownership_change_is_effective(
        _contract(), replace(change, acceptances=(forged,)), root=event_repo
    )


def test_stale_parent_forged_acceptance_and_active_incumbent_self_claim_fail(event_repo: Path):
    contract = _contract()
    change = _normal_change(event_repo)
    assert not model.ownership_change_is_effective(
        contract,
        replace(change, parent_contract_ref=PARENT.replace("c", "d")),
        root=event_repo,
    )
    forged = replace(change.acceptances[0], event=replace(change.acceptances[0].event, sender="director2"))
    assert not model.ownership_change_is_effective(
        contract, replace(change, acceptances=(forged,)), root=event_repo
    )
    wrong_proposal = replace(change.acceptances[0], proposal_ref=FINDING_A)
    assert not model.ownership_change_is_effective(
        contract, replace(change, acceptances=(wrong_proposal,)), root=event_repo
    )
    caller_invented = replace(
        change.acceptances[0],
        event=replace(change.acceptances[0].event, text="forged committed body\n"),
    )
    assert not model.ownership_change_is_effective(
        contract, replace(change, acceptances=(caller_invented,)), root=event_repo
    )
    forged_event_ref = replace(
        change.acceptances[0],
        event=replace(change.acceptances[0].event, ref=FINDING_A),
    )
    assert not model.ownership_change_is_effective(
        contract, replace(change, acceptances=(forged_event_ref,)), root=event_repo
    )
    forged_proposal_event = replace(
        change.proposal,
        event=replace(change.proposal.event, text="forged proposal body\n"),
    )
    assert not model.ownership_change_is_effective(
        contract, replace(change, proposal=forged_proposal_event), root=event_repo
    )
    self_claim = replace(change, proposal=replace(change.proposal, event=replace(change.proposal.event, sender="operator")))
    assert not model.ownership_change_is_effective(contract, self_claim, root=event_repo)


def test_split_exchange_waits_for_every_new_owner(event_repo: Path):
    change = _normal_change(
        event_repo,
        proposed="operator, operator2",
        acceptance_senders=("operator",),
    )
    assert not model.ownership_change_is_effective(_contract(), change, root=event_repo)

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
        _contract(),
        replace(change, acceptances=(*change.acceptances, second)),
        root=event_repo,
    )


def test_retained_new_owner_must_publish_its_own_acceptance(event_repo: Path):
    contract = _contract(owners=("director", "director2"))
    change = _normal_change(
        event_repo,
        previous="director, director2",
        proposed="director, operator",
        acceptance_senders=("operator", "director2"),
    )
    assert not model.ownership_change_is_effective(contract, change, root=event_repo)

    director_ref = _event(
        event_repo,
        sender="director",
        recipient="operator",
        kind="proposal-reply",
        timestamp="2026-07-18T07-04-00Z",
        body=_acceptance_body(
            change.proposal.event.ref,
            previous="director, director2",
            proposed="director, operator",
        ),
    )
    director_acceptance = protocol_mailbox.load_ownership_acceptance_statement(
        event_repo, director_ref
    )
    assert model.ownership_change_is_effective(
        contract,
        replace(
            change,
            acceptances=(change.acceptances[0], director_acceptance),
        ),
        root=event_repo,
    )


def _takeover_change(
    repo: Path,
    *,
    task_id: str = "task-1",
    fresh: str = "no fresh work",
    lock: str = "no active lock",
    corroborator: str | None = "operator",
    confirmation_task_id: str | None = None,
    confirmation_claim_ref: str | None = None,
    confirmation_observed: str | None = None,
    confirmation_timestamp: str | None = None,
) -> model.OwnershipChange:
    sequence = int(_git(repo, "rev-list", "--all", "--count"))
    claim_minute = 10 + sequence
    confirmation_minute = claim_minute + 1
    observed = f"2026-07-18T07:{claim_minute:02d}:00Z"
    evidence_ref = _event(
        repo,
        sender="director2",
        recipient="all",
        kind="dispatch-claim",
        timestamp=f"2026-07-18T07-{claim_minute:02d}-00Z",
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
    confirmations = ()
    if corroborator is not None:
        confirmation_ref = _event(
            repo,
            sender=corroborator,
            recipient="director2",
            kind="acknowledgement",
            timestamp=(
                confirmation_timestamp
                or f"2026-07-18T07-{confirmation_minute:02d}-00Z"
            ),
            body="\n".join(
                (
                    f"Task ID: {confirmation_task_id or task_id}",
                    f"Parent contract: {PARENT}",
                    "Contract revision: 2",
                    "Proposed owner: director2",
                    f"Takeover claim ref: {confirmation_claim_ref or evidence_ref}",
                    f"Observed at: {confirmation_observed or observed}",
                    f"Finding refs: {FINDING_A}, {FINDING_B}",
                )
            ),
        )
        confirmations = (
            protocol_mailbox.load_takeover_confirmation_statement(
                repo, confirmation_ref
            ),
        )
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
        takeover_confirmations=confirmations,
    )


def test_peer_corroborated_takeover_is_effective(event_repo: Path):
    change = _takeover_change(event_repo)
    assert model.ownership_change_is_effective(
        _contract(), change, root=event_repo
    )


def test_takeover_requires_exactly_one_distinct_pair_seat_corroborator(event_repo: Path):
    missing = _takeover_change(event_repo, corroborator=None)
    assert not model.ownership_change_is_effective(
        _contract(), missing, root=event_repo
    )
    same_seat = _takeover_change(event_repo, corroborator="director2")
    assert not model.ownership_change_is_effective(
        _contract(), same_seat, root=event_repo
    )
    coordinator = _takeover_change(event_repo, corroborator="coordinator")
    assert not model.ownership_change_is_effective(
        _contract(), coordinator, root=event_repo
    )
    valid = _takeover_change(event_repo)
    assert not model.ownership_change_is_effective(
        _contract(),
        replace(
            valid,
            takeover_confirmations=(
                valid.takeover_confirmations[0],
                valid.takeover_confirmations[0],
            ),
        ),
        root=event_repo,
    )


def test_takeover_rejects_forged_stale_or_mutated_corroboration(event_repo: Path):
    stale_task = _takeover_change(event_repo, confirmation_task_id="other-task")
    assert not model.ownership_change_is_effective(
        _contract(), stale_task, root=event_repo
    )
    wrong_ref = _takeover_change(event_repo, confirmation_claim_ref=FINDING_A)
    assert not model.ownership_change_is_effective(
        _contract(), wrong_ref, root=event_repo
    )
    stale_observation = _takeover_change(
        event_repo, confirmation_observed="2026-07-18T07:09:00Z"
    )
    assert not model.ownership_change_is_effective(
        _contract(), stale_observation, root=event_repo
    )

    valid = _takeover_change(event_repo)
    confirmation = valid.takeover_confirmations[0]
    replaced_claim = replace(confirmation, takeover_claim_ref=FINDING_A)
    assert not model.ownership_change_is_effective(
        _contract(),
        replace(valid, takeover_confirmations=(replaced_claim,)),
        root=event_repo,
    )
    replaced_body = replace(
        confirmation,
        event=replace(confirmation.event, text="forged corroboration body\n"),
    )
    assert not model.ownership_change_is_effective(
        _contract(),
        replace(valid, takeover_confirmations=(replaced_body,)),
        root=event_repo,
    )


def test_takeover_rejects_backdated_confirmation_envelope(event_repo: Path):
    backdated = _takeover_change(
        event_repo,
        confirmation_timestamp="2026-07-18T07-00-00Z",
    )
    assert not model.ownership_change_is_effective(
        _contract(), backdated, root=event_repo
    )


def test_takeover_rejects_confirmation_from_unrelated_branch(event_repo: Path):
    _event(
        event_repo,
        sender="operator",
        recipient="all",
        kind="status",
        timestamp="2026-07-18T06-59-00Z",
        body="Seed: unrelated branch base",
    )
    change = _takeover_change(event_repo, corroborator=None)
    claim = change.takeover_evidence
    _git(event_repo, "switch", "-q", "-c", "side", f"{claim.event.commit}^")
    confirmation_ref = _event(
        event_repo,
        sender="operator",
        recipient="director2",
        kind="acknowledgement",
        timestamp="2026-07-18T07-30-00Z",
        body="\n".join(
            (
                "Task ID: task-1",
                f"Parent contract: {PARENT}",
                "Contract revision: 2",
                "Proposed owner: director2",
                f"Takeover claim ref: {claim.event.ref}",
                f"Observed at: {claim.observed_at}",
                f"Finding refs: {FINDING_A}, {FINDING_B}",
            )
        ),
    )
    confirmation = protocol_mailbox.load_takeover_confirmation_statement(
        event_repo, confirmation_ref
    )
    assert not model.ownership_change_is_effective(
        _contract(),
        replace(change, takeover_confirmations=(confirmation,)),
        root=event_repo,
    )


def test_takeover_rejects_forged_claim_ref(event_repo: Path):
    change = _takeover_change(event_repo)
    forged_ref = replace(
        change.takeover_evidence,
        event=replace(change.takeover_evidence.event, ref=FINDING_A),
    )
    assert not model.ownership_change_is_effective(
        _contract(),
        replace(change, takeover_evidence=forged_ref),
        root=event_repo,
    )


def test_stale_or_unrelated_work_and_lock_evidence_is_rejected(event_repo: Path):
    contract = _contract()
    assert not model.ownership_change_is_effective(
        contract,
        _takeover_change(event_repo, task_id="other-task"),
        root=event_repo,
    )
    assert not model.ownership_change_is_effective(
        contract, _takeover_change(event_repo, fresh="present"), root=event_repo
    )
    assert not model.ownership_change_is_effective(
        contract, _takeover_change(event_repo, lock="active"), root=event_repo
    )


def test_ownership_change_cannot_drop_or_reorder_finding_refs(event_repo: Path):
    change = _normal_change(event_repo)
    assert not model.ownership_change_is_effective(
        _contract(), replace(change, finding_refs=(FINDING_A,)), root=event_repo
    )
    assert not model.ownership_change_is_effective(
        _contract(),
        replace(change, finding_refs=(FINDING_B, FINDING_A)),
        root=event_repo,
    )
    reordered_proposal = replace(change.proposal, finding_refs=(FINDING_B, FINDING_A))
    assert not model.ownership_change_is_effective(
        _contract(), replace(change, proposal=reordered_proposal), root=event_repo
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
