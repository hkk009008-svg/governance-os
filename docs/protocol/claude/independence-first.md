# Proportional independent review

Executable policy lives in `pipeline/codex_protocol_model.py` and
`pipeline/compact_pair_loop.py`.

Material behavior needs a non-author Codex or Claude review of the exact
committed range. High-risk controls additionally need a different model family
and request-level abuse/evasion analysis. Early advice is optional; there is no
preflight-clear ritual.

The reviewer reads the actual diff, reproduces material evidence, and publishes
one GO, NITS, or FAIL report bound to the committed request. A FAIL remains
active until a valid remediation report supersedes it. AGY challenges are
first-class evidence but not the formal verdict.

Review depth is proportional to the risk. The exact range, non-authorship,
model-family rule, and abuse binding remain strict once formal review is
required. No verdict grants an external effect.
