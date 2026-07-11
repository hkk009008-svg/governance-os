# route/v1 — typed route manifests (compatibility layer)

Status: compatibility-only (ADR-014). Markdown mailbox routes remain the live
authority; route/v1 pairs are generated alongside, compared, and never yet
consumed by live seats. Do not cut over without the follow-up ADR.

## What a coordinator does differently (today: nothing mandatory)

To EXPERIMENT with a typed route for a new cycle:

1. Build the object (all 18 fields; see `schemas/route-v1.schema.json`;
   `packet_delta` must be null, `capability_refs` must be []).
2. Validate + render the pair into a scratch directory:

       env -u GIT_INDEX_FILE .venv/bin/python - <<'EOF'
       import json, pathlib, sys
       sys.path.insert(0, "scripts"); sys.path.insert(0, ".")
       import route_manifest
       route = json.loads(pathlib.Path("my-route.json").read_text())
       issues = route_manifest.validate_route_object(route)
       if issues: raise SystemExit("\n".join(issues))
       out = pathlib.Path("/tmp/route-preview"); out.mkdir(parents=True, exist_ok=True)
       md, sidecar = route_manifest.write_route_pair(
           out, route, title="Coordinator → All: <cycle>")
       print(md, sidecar, sep="\n")
       EOF

3. Check the projection against the live validator:

       env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py \
           --wave 2 --validate-route /tmp/route-preview/<route-id>.md

4. Run the comparator corpus after any change to route/v1 code:

       env -u GIT_INDEX_FILE .venv/bin/python scripts/route_compat.py \
           --out logs/route-compat-report.json

## Authority rules

- The sidecar `<route-id>.route.json` bytes are the canonical RFC 8785
  serialization; `route_hash:` in the .md pins them. Prose edits never change
  authority; breaking the pin fails closed (`RouteManifestError`).
- Unknown top-level fields are rejected; experimental data goes under
  `extensions`.
- The `.md` filename must equal `<route_id>.md`; `read_manifest` binds the two
  and fails closed (`RouteManifestError`) so a hash-valid object cannot ride in
  under another route's filename.
- No string field anywhere in the object (top-level, nested, or under
  `extensions`) may contain a newline or carriage return; `validate_route_object`
  rejects them (`control characters rejected in <json-path>`). This is the
  injection guard — the projection interpolates fields unescaped, so a smuggled
  newline would otherwise render a second prose line the legacy per-line parser
  reads as authority.
- `generation` / `parent_route_id` / `expected_control_head` are shape-checked
  but not yet CAS-enforced (that is Slice 2 / P0.3).

## Route lineage and currency (ADR-015)

Route currency no longer depends on filename timestamp. A route carries
`Route generation: N` and (unless it is generation 1) `Supersedes route:
<parent>` — both emitted by the route/v1 renderer. The authoritative route is
the lineage TIP: the highest-generation route that no other route supersedes.

- Resolve / audit the current authoritative route:

      env -u GIT_INDEX_FILE .venv/bin/python scripts/route_lineage.py --check

  It reports the authoritative route id, exits non-zero on a fork (two tips at
  one generation) or a cycle, and prints `legacy route set` when no route
  carries a generation (the resolver then falls back to filename order).

- A new route may supersede the current tip only under compare-and-swap: its
  `Supersedes route:` must name the current tip and its generation must be
  the tip's generation + 1. `route_lineage.check_cas` returns a structured
  `stale_parent` refusal otherwise — the stale writer rebases its delta onto
  the new tip rather than overwriting it.

Legacy routes without a generation header keep the prior reverse-lexicographic
behavior, so the live campaign is unaffected until routes adopt generations.
