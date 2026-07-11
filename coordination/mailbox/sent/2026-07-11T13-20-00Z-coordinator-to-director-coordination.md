# Coordinator route — Task 4 quality correction

- **from:** coordinator
- **to:** director
- **kind:** route
- **wave:** 2
- **plan correction:** `b13428c`

Task 4 remains gated at QUALITY CHANGES REQUIRED. Implement only the newly
bound corrections in the four Task 4 paths: recovery CLI dispatch before the
old-source hash check for the governed same-path reverify flow; canonical
directory fsync before DB commit; unique descriptor-bound no-follow restore and
manifest temps with file and containing-directory fsync. Add strict tests for
the real apply → `committed_unverified` → same-path CLI reverify and for
symlink/hardlink/substitution/durability barriers. Run RED before production,
then focused/full suites and fresh spec + quality review. Token B only; no
canonical workbook or real-data mutation; no push.
