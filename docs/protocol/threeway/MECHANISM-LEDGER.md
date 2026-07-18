# Threeway Mechanism Ledger

Generated and checked by:

```bash
.venv/bin/python scripts/threeway_mechanism_ledger.py --check
```

| Kind | Status | Runtime emitters / support | Tests | Note |
|---|---|---|---|---|
| `approver_roster` | `live` | `scripts/overseer_emit.py approver_roster` | (no dedicated test) | overseer roster |
| `assignment` | `live` | `scripts/overseer_emit.py assignment` | (no dedicated test) | overseer assignment |
| `attestation` | `live` | `scripts/seat_emit.py operator attestation`<br>`scripts/seat_emit.py operator2 attestation` | (no dedicated test) | primary verifier attestation |
| `attestation_revoked` | `live` | `scripts/seat_emit.py <seat> attestation_revoked`<br>`scripts/chief_emit.py <chief> attestation_revoked`<br>`scripts/overseer_emit.py attestation_revoked` | `tests/unit/test_chief_emit.py` | principal-safe revocation CLIs (chief path tested; seat/overseer paths untested) |
| `brief` | `live` | `scripts/overseer_emit.py brief` | (no dedicated test) | overseer-authority fact |
| `brief_superseded` | `live` | `scripts/overseer_emit.py brief_superseded` | (no dedicated test) | overseer supersession CLI |
| `candidate` | `live` | `scripts/seat_emit.py coordinator candidate`<br>`scripts/seat_emit.py coordinator2 candidate` | (no dedicated test) | interactive coordinator fact |
| `candidate_aborted` | `live` | `scripts/seat_emit.py coordinator candidate_aborted`<br>`scripts/seat_emit.py coordinator2 candidate_aborted` | (no dedicated test) | interactive coordinator abort fact |
| `ci_result` | `live` | `scripts/sign_ci_result.py` | `tests/unit/test_threeway_activation_scripts.py` | CI attestor fact |
| `co_sign` | `live` | `scripts/seat_emit.py operator2 co_sign` | (no dedicated test) | dynamic mirror-verifier CLI |
| `cycle_go` | `live` | `scripts/overseer_emit.py cycle_go` | (no dedicated test) | overseer cycle authorization |
| `human_approval` | `live` | `scripts/chief_emit.py <chief> human_approval` | `tests/unit/test_chief_emit.py` | rostered chief approval CLI |
| `merge_completed` | `live` | `threeway/gate.py run_gate` | `tests/unit/test_threeway_activation_scripts.py` | merge-gate completion fact |
| `re_verify` | `live` | `scripts/seat_emit.py operator re_verify` | (no dedicated test) | candidate primary-verifier challenge echo CLI |
| `re_verify_challenge` | `live` | `scripts/overseer_emit.py re_verify_challenge` | (no dedicated test) | overseer nonce challenge |
| `release_order` | `live` | `scripts/overseer_emit.py release_order` | (no dedicated test) | manual overseer release order |
| `release_requested` | `live` | `scripts/seat_emit.py coordinator release_requested`<br>`scripts/seat_emit.py coordinator2 release_requested` | (no dedicated test) | interactive coordinator release request |
