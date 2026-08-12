# HANDOFF owner — compact root WIP preservation

When: 2026-07-16T06:29:06Z
Owner: `director2`
Disposition: `commit-and-handoff`
Authority: `coordination/mailbox/sent/2026-07-16T05-48-49Z-coordinator-to-all-coordination.md`
Side-effect ID: `recovery-root-compact-release-2026-07-16`

## Findings First

- Director2 corrected the stale Task 3 checkpoint model on `main` in
  `b3fdd66ddc1ed19654af0172b1da56585bd40a4f`, then created the
  preservation-only branch `codex/recovery-compact-root-wip-2026-07-16`
  from that exact post-plan source base.
- Preservation commit
  `9654ad5c6d9ff8cc6ed8e71fa2863dc6b9174c96` changes exactly 103 paths:
  the live composite `ARCHITECTURE.md` blob plus the 102 then-untracked
  files beneath `logs/capability-first/`.
- All four checkpoint-match paths and all three contained-`main` advance
  paths remained clean comparison evidence. None appears in the preservation
  commit.
- The shared root returned to `main` at
  `b3fdd66ddc1ed19654af0172b1da56585bd40a4f`. Every compact target is clean
  there because the dirty bytes remain reachable from the preservation
  branch.
- The 35 route-excluded ambient files beneath `.agents/`, `.codex/runtime/`,
  `ORIGINAL_REQUEST.md`, and `PROJECT.md` retained the identical sorted
  blob/path manifest before and after both branch switches.
- This is byte preservation and provenance only. It is not implementation
  acceptance, measurement acceptance, integration, activation, publication,
  or cleanup authority.

## Frozen Source And Preservation Head

- Source branch: `main`
- Source base and plan-correction commit:
  `b3fdd66ddc1ed19654af0172b1da56585bd40a4f`
- Plan-correction subject: `docs(recovery): correct compact root checkpoint`
- Preservation branch: `codex/recovery-compact-root-wip-2026-07-16`
- Preservation head:
  `9654ad5c6d9ff8cc6ed8e71fa2863dc6b9174c96`
- Preservation parent:
  `b3fdd66ddc1ed19654af0172b1da56585bd40a4f`
- Preservation subject: `chore(recovery): preserve compact root WIP`
- Preservation commit tree:
  `338a2ddd2669ad6611efdac77cbeeb158b08049d`
- Resulting `logs/capability-first/` tree:
  `8b83fbea22eabd46a80301dfd55686ca22f8df68`
  (includes source-base history as well as the 102 newly preserved files; the
  exact changed-path manifest below is authoritative for this preservation
  unit).
- Source-base `logs/capability-first/` tree:
  `f351fcfc8851071944011a4cf9d2fc28a373fc10` with 95 inherited entries.
  The preservation head has 197 log-tree entries: those 95 inherited entries
  unchanged plus the exact 102 additions below.
- Changed paths: 103 total = one `ARCHITECTURE.md` plus 102
  `logs/capability-first/` files.
- Raw diff manifest SHA-256:
  `b1c64367a54ece7dd13461b5b552d32fbd946904e207468c937b3f95253a8a1b`
- Normalized new-blob/path manifest SHA-256:
  `c552d2cb3ce59257c06aedbcb477debb4e33411939d3444fd8d30a20ae12e82b`
  from `git diff-tree --no-commit-id --raw -r 9654ad5... | awk
  '{print $4 " " $6}' | shasum -a 256`.

## Exact Preserved Path And Blob Manifest

The following is the exact output of
`env -u GIT_INDEX_FILE git diff-tree --no-commit-id --raw -r 9654ad5c6d9ff8cc6ed8e71fa2863dc6b9174c96`.
The fourth object column is the preserved blob at the preservation head.

```text
:100644 100644 da0bdbb7ec4445ace8b64ca1acd727f8a2dc72ac f790828b5492f3284a9933a1c6c16e401eb6a433 M	ARCHITECTURE.md
:000000 100644 0000000000000000000000000000000000000000 dd16abf76a18f05eb46a7bee2a379c5d37818c55 A	logs/capability-first/.canaries/phase1-06c406f-gpt56sol-max-20260715/records/canary-phase1-06c406f-gpt56sol-max-20260715-none-1/record.json
:000000 100644 0000000000000000000000000000000000000000 1067079ee54c9dd7d5f3b40722cf1e2fd9408521 A	logs/capability-first/.canaries/phase1-06c406f-gpt56sol-max-20260715/records/canary-phase1-06c406f-gpt56sol-max-20260715-none-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 9827bf78dfbbc57442ce5bfa67543b407c1527ac A	logs/capability-first/.canaries/phase1-569b8d9-gpt56sol-max-20260715/records/canary-phase1-569b8d9-gpt56sol-max-20260715-none-1/record.json
:000000 100644 0000000000000000000000000000000000000000 1e7c211860e4298f732e36281ca5d8dbb0e7ae4a A	logs/capability-first/.canaries/phase1-569b8d9-gpt56sol-max-20260715/records/canary-phase1-569b8d9-gpt56sol-max-20260715-none-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 a63443d1d06614b111d65a11eed714b08d17d542 A	logs/capability-first/.canaries/phase1-872aa67-gpt56sol-max-20260715/records/canary-phase1-872aa67-gpt56sol-max-20260715-none-1/record.json
:000000 100644 0000000000000000000000000000000000000000 bd022ece6dc77cd65e3a0cce008c6e9ca426f2e9 A	logs/capability-first/.canaries/phase1-872aa67-gpt56sol-max-20260715/records/canary-phase1-872aa67-gpt56sol-max-20260715-none-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 f7ba3d55365e2afb45577699f003d72e311d8c02 A	logs/capability-first/.canaries/phase1-b94b7e3-gpt56sol-max-20260715/records/canary-phase1-b94b7e3-gpt56sol-max-20260715-none-1/record.json
:000000 100644 0000000000000000000000000000000000000000 5d57bc56a3ff1f0da7f40cfb5596c9de05bf4e29 A	logs/capability-first/.canaries/phase1-b94b7e3-gpt56sol-max-20260715/records/canary-phase1-b94b7e3-gpt56sol-max-20260715-none-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 e5011b842d871422598d7c03a16e6b2a395dd52b A	logs/capability-first/.canaries/phase1-dcc1711-gpt56sol-max-20260715/records/canary-phase1-dcc1711-gpt56sol-max-20260715-none-1/record.json
:000000 100644 0000000000000000000000000000000000000000 86e9a4ac43d4902dadcfb73b579c08ba020978be A	logs/capability-first/.canaries/phase1-dcc1711-gpt56sol-max-20260715/records/canary-phase1-dcc1711-gpt56sol-max-20260715-none-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 500324dbc4f187a895819c7456b5f6a953a07681 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/baseline.json
:000000 100644 0000000000000000000000000000000000000000 26a73c40f126d68c536d6a0fa7b4438f72f4dcba A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-combined-1.json
:000000 100644 0000000000000000000000000000000000000000 346b7ff7ccb680eb71a778dc6cee5c008b1fbddd A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-combined-2.json
:000000 100644 0000000000000000000000000000000000000000 7df805c87ea63c226c6edbf8c19d0e14df0d3ccb A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-combined-3.json
:000000 100644 0000000000000000000000000000000000000000 0b50c21a12ab51d6528e53f4e117d46819337b93 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-combined-4.json
:000000 100644 0000000000000000000000000000000000000000 f1f3013a90c6861312cab5def287f13a88c9476d A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-combined-5.json
:000000 100644 0000000000000000000000000000000000000000 c3807503385785a2178d915b02521af0718e8035 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-effect_only-1.json
:000000 100644 0000000000000000000000000000000000000000 ba92d030a55797ffe2722910870ccc358d172836 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-effect_only-2.json
:000000 100644 0000000000000000000000000000000000000000 5a42283f02b21c0b397abb4c876a0be76b9cc02d A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-effect_only-3.json
:000000 100644 0000000000000000000000000000000000000000 2fd75a4b865495c771b6dab82f58b13a21a7c864 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-effect_only-4.json
:000000 100644 0000000000000000000000000000000000000000 258c660752b06965a96b75945d3f60862f8a5d11 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.capability-state/effects/phase1-872aa67-gpt56sol-max-20260715-effect_only-5.json
:000000 100644 0000000000000000000000000000000000000000 40ad590812da325fc795228489d6b2733b813d66 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-1/marker.json
:000000 100644 0000000000000000000000000000000000000000 c74e238c7a2b239ee06973641e0f49011b23d735 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-2/marker.json
:000000 100644 0000000000000000000000000000000000000000 06b0cb007391dc47f07975c90ecc7a91f6c8987e A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-3/marker.json
:000000 100644 0000000000000000000000000000000000000000 0603054aec344e55444fd0b8aa2900bebc847bc6 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-4/marker.json
:000000 100644 0000000000000000000000000000000000000000 4647a2ac72e4e555932e3f060a2b593273026435 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-5/marker.json
:000000 100644 0000000000000000000000000000000000000000 89ff28bceb38a49e17de380dfc18e829996d03a3 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-effect_only-1/marker.json
:000000 100644 0000000000000000000000000000000000000000 2e0a508f03876120a8d23c355cdd58bfa6ea7604 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-effect_only-2/marker.json
:000000 100644 0000000000000000000000000000000000000000 424fa1ef12828633ab16c8b46293673601226362 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-effect_only-3/marker.json
:000000 100644 0000000000000000000000000000000000000000 6aaece7fd93c7b17cc73c0bc4ba6e86431952554 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-effect_only-4/marker.json
:000000 100644 0000000000000000000000000000000000000000 852509ff8acc1e76e055ead082c21a325bab6965 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/.codex/runtime/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-effect_only-5/marker.json
:000000 100644 0000000000000000000000000000000000000000 e4ce7934ae8eb98398782ee36646799e9b32da47 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-1/route.json
:000000 100644 0000000000000000000000000000000000000000 159b8ed1f45097e189282f41e238c1a02d7c9662 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-2/route.json
:000000 100644 0000000000000000000000000000000000000000 9446def6aa82744e0b87fa7785081ee03aeb33b9 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-3/route.json
:000000 100644 0000000000000000000000000000000000000000 51c15c15cd1f555af021e8dcb86f6b293fa94744 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-4/route.json
:000000 100644 0000000000000000000000000000000000000000 8de9d62c2784f56e2495916560e74e61ef30b41f A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-5/route.json
:000000 100644 0000000000000000000000000000000000000000 97e76652b34be32dae43656c1ac0292896aaa7a3 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-coordination_only-1/route.json
:000000 100644 0000000000000000000000000000000000000000 f5e4481ae5b0c1ae5ba88b6581dcf5b66845a4ab A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-coordination_only-2/route.json
:000000 100644 0000000000000000000000000000000000000000 cddb42effdb2444557ea96a8c7ada9fe3be48a96 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-coordination_only-3/route.json
:000000 100644 0000000000000000000000000000000000000000 76c6633cd38f7c91eb21da1af5da11c1c7a4f948 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-coordination_only-4/route.json
:000000 100644 0000000000000000000000000000000000000000 6d5f60a877897ea17eebf8632b07c0d2fc6158bf A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-coordination_only-5/route.json
:000000 100644 0000000000000000000000000000000000000000 1267e875bee4a5800cd98dc7fad8afe147b35778 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-1/review.json
:000000 100644 0000000000000000000000000000000000000000 04ff48b8c953e4eb8cf8a98dd81a7b87b57969c6 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-2/review.json
:000000 100644 0000000000000000000000000000000000000000 0a9c6d1db99d91999f769dc332589be33903f50a A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-3/review.json
:000000 100644 0000000000000000000000000000000000000000 2145f633247032f4a26239e3372c9599b73ca12a A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-4/review.json
:000000 100644 0000000000000000000000000000000000000000 f13d987a8e3a73b4f5da8a7c1a5ef2f455e32a6d A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-combined-5/review.json
:000000 100644 0000000000000000000000000000000000000000 f263bf895514b43a925ab750122cf8ffe1baa199 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-verification_only-1/review.json
:000000 100644 0000000000000000000000000000000000000000 dfd43c8991a7ea84223ae5d7a136b59fba3bd7b3 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-verification_only-2/review.json
:000000 100644 0000000000000000000000000000000000000000 ec909c37817c7581b6fea76d4d5abf89e19bfb09 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-verification_only-3/review.json
:000000 100644 0000000000000000000000000000000000000000 1970f6a1bcc4273b94eacb5a6cc23129b0b3a65e A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-verification_only-4/review.json
:000000 100644 0000000000000000000000000000000000000000 4960b0f298dc6ffb7e7965586b6e27bec35aa115 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/evidence/coordination/verification/capability-baseline/phase1-872aa67-gpt56sol-max-20260715-verification_only-5/review.json
:000000 100644 0000000000000000000000000000000000000000 d911e26ce7737930270890ad2e247fc4f7a0989b A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/observations.json
:000000 100644 0000000000000000000000000000000000000000 2b008435c9cf0c45b0c551e0a8975ab670fe8382 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-1/record.json
:000000 100644 0000000000000000000000000000000000000000 c8c23148fe2ee160e48e78fee2747ea93abb86cd A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 0565a92c48e14e83b1aba0dd9777f181f33ae99e A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-2/record.json
:000000 100644 0000000000000000000000000000000000000000 85316c874c8bd91fa79058550a040db861aebaa8 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-2/reservation.json
:000000 100644 0000000000000000000000000000000000000000 6617f8ddede08c48787ee5253a3b07bbb6d96b11 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-3/record.json
:000000 100644 0000000000000000000000000000000000000000 550bdfb38240385c1aea6d9a9bd2ebe9201149b7 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-3/reservation.json
:000000 100644 0000000000000000000000000000000000000000 7fd54968cd53a98d3616a5aebd358a1d6b541cd9 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-4/record.json
:000000 100644 0000000000000000000000000000000000000000 3ec6be9d87b6144a324b2779d6bfa3e0dd626d54 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-4/reservation.json
:000000 100644 0000000000000000000000000000000000000000 26071b7c923125685422408d3aaeba059ed16588 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-5/record.json
:000000 100644 0000000000000000000000000000000000000000 c102c5ed45083fb2a076507b8c0f4342ecd1cb34 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-combined-5/reservation.json
:000000 100644 0000000000000000000000000000000000000000 516f05ab4c78367594789d9774ed0e114b624a37 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-1/record.json
:000000 100644 0000000000000000000000000000000000000000 321c0f5095ba4dacadff55cba39193ddfb20abdf A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 854a16a6e51930bba0a590ff55a16cc75781a1c1 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-2/record.json
:000000 100644 0000000000000000000000000000000000000000 80ab139d92bec1a4591f46ec768a36d183ba0d6f A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-2/reservation.json
:000000 100644 0000000000000000000000000000000000000000 658efb3e8aa6f6d791ae98da19aad0c1321f3a56 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-3/record.json
:000000 100644 0000000000000000000000000000000000000000 d04031636bdf1de45fc6913e5439c41936ab11f3 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-3/reservation.json
:000000 100644 0000000000000000000000000000000000000000 28eca501fbaa08f2529651cebdcc531b9a1ddfde A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-4/record.json
:000000 100644 0000000000000000000000000000000000000000 0fefb048c0c208bdd859fb15eb5fe62cb009c20c A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-4/reservation.json
:000000 100644 0000000000000000000000000000000000000000 5762b95a18e9a805976aec6085cda775b4768728 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-5/record.json
:000000 100644 0000000000000000000000000000000000000000 387a7fff44c08dfde520459f5d31741c806e61c7 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-coordination_only-5/reservation.json
:000000 100644 0000000000000000000000000000000000000000 a7235a7656fd3d9467604f383281b2a8d71e20d2 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-1/record.json
:000000 100644 0000000000000000000000000000000000000000 fce9f77a19ce12e40fac3e41199f58bc5b7f678f A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 0d63705df13aff47da5d7be444a0a8945629a7c4 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-2/record.json
:000000 100644 0000000000000000000000000000000000000000 960640ec5bd67fa182ffb5f83fb66caf0a3eb67c A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-2/reservation.json
:000000 100644 0000000000000000000000000000000000000000 43ba2d3f653baeca5bf4a7e491f5a70183734301 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-3/record.json
:000000 100644 0000000000000000000000000000000000000000 25f8d8582d91cde4e789bfeb9ea259f7d5bad622 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-3/reservation.json
:000000 100644 0000000000000000000000000000000000000000 53cb295b7292b24413443a0723222bd02077826c A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-4/record.json
:000000 100644 0000000000000000000000000000000000000000 87815436d417a93721125757c90559771a765f9b A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-4/reservation.json
:000000 100644 0000000000000000000000000000000000000000 fa13134638b63569f9996e72ee352e76ae9a45c4 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-5/record.json
:000000 100644 0000000000000000000000000000000000000000 bd9eea76b358ae9edc9d06b0fb9d0c5091259d7b A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-effect_only-5/reservation.json
:000000 100644 0000000000000000000000000000000000000000 e197838b1e4c5b2ff599058acf2c784e7cb872a6 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-1/record.json
:000000 100644 0000000000000000000000000000000000000000 dca641bbda72b718d19225623633c5c33fc0bbad A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 8c2cc2f35b087557c077cc71fedc0314c90253a7 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-2/record.json
:000000 100644 0000000000000000000000000000000000000000 7845c42ca3f9c491b455f3cb0f1262cda403ea6f A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-2/reservation.json
:000000 100644 0000000000000000000000000000000000000000 47f13e4918ccabd19516fe6bb26e4ecc4196c7b3 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-3/record.json
:000000 100644 0000000000000000000000000000000000000000 2c4185f9761d336c31d36c8a3f27f3b74cca54a0 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-3/reservation.json
:000000 100644 0000000000000000000000000000000000000000 00f903b6ef917ea04704daf9242a420afb61a5e0 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-4/record.json
:000000 100644 0000000000000000000000000000000000000000 4507b1ccc155603b465576721ef2218c14859e47 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-4/reservation.json
:000000 100644 0000000000000000000000000000000000000000 ea7f831e198a32738a41f0179617661719709f90 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-5/record.json
:000000 100644 0000000000000000000000000000000000000000 124abf18cd5784ed8ee43867980ef4d8d666ab6b A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-none-5/reservation.json
:000000 100644 0000000000000000000000000000000000000000 676e92fcd3d8c4ea7b49303935bc0c7c57ddc195 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-1/record.json
:000000 100644 0000000000000000000000000000000000000000 e20de69ebbf79a3916f6c70cdfd1a90d265521de A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-1/reservation.json
:000000 100644 0000000000000000000000000000000000000000 e70eff12525907141fc73bbea01dddd0eaa06cd0 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-2/record.json
:000000 100644 0000000000000000000000000000000000000000 e6b5f99c77b1a9302ad94f0ca4e7d1754498914b A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-2/reservation.json
:000000 100644 0000000000000000000000000000000000000000 a182a4e9de8971845149a40534c3149c2e7d9136 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-3/record.json
:000000 100644 0000000000000000000000000000000000000000 b96442d0c12837b7e32615fd41b7723351e8aea6 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-3/reservation.json
:000000 100644 0000000000000000000000000000000000000000 fc7d672a4a88d535f649d0cfa10104edffa024ec A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-4/record.json
:000000 100644 0000000000000000000000000000000000000000 81099c89913a6a1b019bca42e17432ece7c73afc A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-4/reservation.json
:000000 100644 0000000000000000000000000000000000000000 55728f2e8c829c8f78c89f0613f174dd6a7bd820 A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-5/record.json
:000000 100644 0000000000000000000000000000000000000000 3da9a4bf656239240697d0b4c6c6b8007adf2adb A	logs/capability-first/phase1-872aa67-gpt56sol-max-20260715/records/phase1-872aa67-gpt56sol-max-20260715-verification_only-5/reservation.json
```

## Clean Comparison Evidence

Four working blobs matched both source-base `HEAD` and checkpoint
`1306c157ac434389444e77935d24db8b3189ee2c`:

| Path | Matching blob |
|---|---|
| `governance.toml` | `da0d444ceef156c577636b2bc7d0fc168cff66bd` |
| `scripts/target_binding.py` | `bc8a1a210e1b56d197282c61b6bb5d679368c55b` |
| `tests/unit/test_target_binding.py` | `0fba3865772e8905eec9c795baee86aea6cb842a` |
| `tests/fixtures/compact_kernel/v1_misuse_vectors.json` | `2ed1c69a4700edd9e87f18b436f36f0573917a56` |

Three working blobs differed from the checkpoint but matched the named
contained-`main` advance and source-base `HEAD`:

| Path | Source-base blob | Contained advance | Checkpoint blob |
|---|---|---|---|
| `scripts/compact_state_mapping.py` | `ff9118cbc509ae1a3e5a5f15816f907316f06218` | `484b16a27f45eb6f4b973894499ea1e5edf704c4` | `79dea42051a7f2cba124cc463b60b942642d4bb0` |
| `tests/fixtures/compact_state_mapping/v1.json` | `65e3bf1ec847c3b556f752198c00ba7647fd3a34` | `be1488a41b6174b4503fb23f8885794fa37528fc` | `e184cdb77692dbdc9a67b4c5f78945bd8a064840` |
| `tests/unit/test_compact_state_mapping.py` | `f9905658de63cce75f51a57414f5c211abdac665` | `7151cee977693bcdf0dda262d68bd9e0253f7aa2` | `b7f15f8c571e41aa58b7758cd99e0854a0041562` |

Verified via the corrected Task 3 command block: four
`checkpoint-match` lines plus three `contained-main-advance` lines, exit
`0`. The exclusion check was:

```text
env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r \
  9654ad5c6d9ff8cc6ed8e71fa2863dc6b9174c96 -- \
  governance.toml scripts/target_binding.py \
  tests/unit/test_target_binding.py \
  tests/fixtures/compact_kernel/v1_misuse_vectors.json \
  scripts/compact_state_mapping.py \
  tests/fixtures/compact_state_mapping/v1.json \
  tests/unit/test_compact_state_mapping.py

<no output>
```

## Preservation Evidence

Pre-branch snapshot at
`b3fdd66ddc1ed19654af0172b1da56585bd40a4f`:

- `ARCHITECTURE.md` working blob:
  `f790828b5492f3284a9933a1c6c16e401eb6a433`.
- `logs/capability-first/`: 102 untracked files.
- All sixteen frozen ChatGPT paths and all former seven peer paths: clean.
- Shared index: empty. Protocol locks: empty. Unclassified routed WIP: zero.
- Capacity board: valid; release route validation: valid.
- Protocol Doctor: PASS, 431 tests passed.
- Wave 2: MET.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` → `OK`.

Executed from the preservation branch before commit:

```text
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_target_binding.py \
  tests/unit/test_compact_state_mapping.py -q

70 passed in 0.42s
```

```text
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py

PROJECT SMOKE — governance-OS runtime invariants ... OK
RESULT: no ceremony detected — every relied-on green is backed by execution.
PLACEHOLDER CHECK — PASS (no unallowlisted tokens).
GO-SCHEMA CHECK — PASS (41 verification-report(s) validated; zero violations).
ARCH-FRESHNESS CHECK — PASS (stamp bump detected or body unchanged).
OK
```

Scope proofs:

- `git diff --cached --check` → no output.
- Staged and committed set: 103 allowed paths; no comparison or ambient path.
- After returning to `main`, the following printed no output:

  ```text
  env -u GIT_INDEX_FILE git status --short -- \
    ARCHITECTURE.md logs/capability-first \
    governance.toml scripts/target_binding.py \
    tests/unit/test_target_binding.py \
    tests/fixtures/compact_kernel/v1_misuse_vectors.json \
    scripts/compact_state_mapping.py \
    tests/fixtures/compact_state_mapping/v1.json \
    tests/unit/test_compact_state_mapping.py
  ```
- Excluded ambient set: 35 files; sorted blob/path manifest SHA-256
  `5ebf227e86702ccc12a05188f3d1bae38fbe638f549d33876d9bd25ff44e6829`
  before and after the branch switches.

Known preservation-check failures: none.

## Composite Architecture Disposition

The preserved `ARCHITECTURE.md` blob is a composite anchor refresh. It is
preserved exactly, but it is not accepted as final architecture truth for any
future integration range. The integration owner must regenerate and verify the
anchors against whichever feature range is lawfully selected.

## Evidence-Only Log Disposition

Every newly preserved `logs/capability-first/` file remains evidence-only.
Neither this handoff nor its passing preservation checks accept a Phase-1
measurement, a gate number, or a runtime verdict. A later Phase-1/2 integration
plan must explicitly accept or supersede each relied-on cohort before citing it.

## Historical Canonical Compact Context

- Historical canonical branch name:
  `codex/capability-phase2-shadow-2026-07-15`; the local ref is absent at this
  handoff refresh and was not recreated.
- Historical implementation head, previously recorded clean:
  `2d5b23f819694f2abe39d4aed6cac318a4f9019d`.
- Integration snapshot:
  `bea4cb9fa6117d2c61e78ed05c2ce5a24f7a874a`.
- Historical post-snapshot chain:
  `ae24effb8734cd92e418ae2f032724428d0df94a` →
  `2d5b23f819694f2abe39d4aed6cac318a4f9019d`.
- Root-blob comparison checkpoint:
  `1306c157ac434389444e77935d24db8b3189ee2c`.
- The snapshot and both later commits are contained in current `main`.
  Historical containment is context only; it grants no replay, revised
  allowlist, review, acceptance, integration, or ref-recreation authority.

## Authority And Exclusions

- Authority: epoch 0, writer v1, no activation.
- Integration authority: none.
- Merge authority: none.
- Push or remote-ref authority: none.
- Cleanup or branch-deletion authority: none.
- Provider/browser attempts: zero.
- No mailbox cursor, protocol lock, runtime receipt, paid spend, pod, production
  generation, publication, or deployment was changed.
- No Operator or Operator2 verification trigger is created by this
  preservation-only handoff.
- The seven clean comparison paths and all ambient artifacts are excluded from
  the preservation commit.

## Exact Next Trigger

Run `coordination/bin/codex-seat coordinator -- "continue as coordinator"`.
The coordinator must refresh the plan commit, preservation branch/head, this
committed handoff, current mailbox/locks/index/capacity/route/doctor/wave/smoke
state, and the clean shared-root compact targets before closing or rerouting
this recovery unit. Do not start compact integration from this handoff alone;
the separately governed Phase-1 and Phase-2 handoffs and route must first
authorize that next plan.
