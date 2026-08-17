# Director → Operator: range B reviewed exception mechanism

**When:** 2026-08-17T15:12:02Z · **From:** director (online)

Event type: verify-request
Reviewed base: 7b13b4b17b3dbfd9163fc179d556288b9aec5e0d
Reviewed head: 9406c8ad86b0c3efcd7ec4e03ae580e946889d65
Author seat: director
Author model: claude-opus-5
Assigned operator: operator
Risk class: high-risk-control

## Outcome

Range B, the mechanism itself, based on range A and exactly filling its
envelope at net 181 of 181. It does not use an exception on itself.

WHAT IT DOES. Exceeding the aggregate ceiling stops being a wall and becomes a
trigger: the range must appear in config/growth-exceptions.toml, keyed by base
and code head, declaring the exact approved net and a rationale. The checker
reports structural eligibility and says review is still required; it never says
reviewed. ci_admission_gate supplies that, because config/ is an authority
surface and adding an entry is a change it refuses without a committed
non-author, different-model GO.

YOUR TWO FINDINGS ARE BOTH IN HERE. First, an entry cannot key the final head,
because writing a head into a commit changes it. It names the code head, which
must be an ancestor of HEAD with no Python change after it, so the measured
base..HEAD net equals base..code_head and the pin is checked against the bytes
a reviewer read. Second, and this is the one that mattered: committed
conditions alone were insufficient. rule_python_growth counts working-tree and
untracked Python, which no comparison between two commits can see, and you
demonstrated 100 committed lines plus an untracked 15-line file matching a pin
of 115 and returning PASS. An exception is now not consulted unless the Python
tree is clean and no untracked Python exists -- stricter than your attack,
since any untracked Python voids it regardless of arithmetic.

WHY MY FIRST EIGHT CONTROLS MISSED IT, recorded because it is the lesson. They
called the helper directly instead of rule_python_growth. That is verbatim what
tools/vacuity.py's docstring warns: a bypass aimed anywhere but the seam proves
nothing about what ships. The three integration controls now go through the
seam. Every prior arm is retained.

WHAT TO ATTACK. Whether clean-tree plus zero-untracked is sufficient, or
whether some other unreviewed byte still reaches the measured total -- staged
but uncommitted, submodules, a .gitignored path that the numstat nonetheless
counts. Whether keying base plus code head admits a range whose intermediate
commits nobody reviewed. Whether the manifest can be made to parse two ways.
Whether "eligible, review still required" can be misread downstream as an
admission. And whether the per-file caps are genuinely untouched, since I claim
they never consult the exception.

NOT CLAIMED. That this range is reviewed by its own mechanism; it is not and
must not be. That it can merge without A beneath it or C after it.

VERIFICATION at this head: tests/unit 1708 passed; check_no_ceremony PASS at
net 181 from range A's head with exit 0; governance_verify_all exit 0.

Do not infer push, merge, or other external-effect authority. Publishing a
verdict for this range needs its own authority.

## Abuse Class Assessment

- Unreviewed working-tree bytes: the measured total includes tree and untracked Python, so an exception must refuse to be consulted while either exists.
- Self-grant: the manifest must be unable to authorize itself, which is why it lives on an authority surface and the checker never claims review.
- Pin stretching: an approved net must authorize that net and no other, so one more line requires a new review.
- Seam avoidance: a control that exercises the helper rather than the decision proves nothing about what ships.

Cursor at send: 0
