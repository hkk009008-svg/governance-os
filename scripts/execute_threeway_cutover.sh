#!/usr/bin/env bash
set -euo pipefail

# Three-Way Protocol cutover driver: provision keys (idempotent) + run the IRREVERSIBLE
# legacy->signed-bus cutover. Both this script AND threeway.cutover refuse the irreversible
# step without an explicit --yes (double-gated; DECISIONS.md ADR-045).

REGISTRY_DIR="coordination/threeway/keys"
KEYSTORE_DIR="${THREEWAY_KEYSTORE:-$HOME/.threeway/keys}"
PY="${PYTHON:-.venv/bin/python}"

if [ "${1:-}" != "--yes" ]; then
  echo "REFUSING: the legacy->signed-bus cutover is IRREVERSIBLE (DECISIONS.md ADR-045)."
  echo "Re-run to confirm:   $0 --yes"
  exit 2
fi

echo "=== Three-Way Protocol Cutover ==="

# [1/2] The bootstrap owns exact-roster validation. It creates an absent roster,
#       leaves a complete matching roster byte-for-byte unchanged, and rejects
#       partial, mismatched, symlinked, or insecure key state before cutover.
echo "[1/2] Validating/provisioning exact key roster..."
"$PY" -m threeway.keys_bootstrap --registry "$REGISTRY_DIR" --keystore "$KEYSTORE_DIR"
echo "Public keys -> $REGISTRY_DIR ; private keys -> $KEYSTORE_DIR (NEVER commit private keys)."

# Cutover consumes only an object-addressed public-key trust root. A first run
# may provision keys, but it must stop so those public files can be reviewed and
# committed before any signed-bus ref becomes live.
REGISTRY_COMMITTED=1
PUBLIC_KEY_COUNT=0
for PUBLIC_KEY in "$REGISTRY_DIR"/*.pub; do
  if [ ! -f "$PUBLIC_KEY" ]; then
    continue
  fi
  PUBLIC_KEY_COUNT=$((PUBLIC_KEY_COUNT + 1))
  if ! git ls-files --error-unmatch -- "$PUBLIC_KEY" >/dev/null 2>&1; then
    REGISTRY_COMMITTED=0
    continue
  fi
  if ! git diff --quiet HEAD -- "$PUBLIC_KEY"; then
    REGISTRY_COMMITTED=0
  fi
done
if [ "$PUBLIC_KEY_COUNT" -eq 0 ] || [ "$REGISTRY_COMMITTED" -ne 1 ]; then
  echo "STOP: public-key roster is new, dirty, staged-only, or untracked." >&2
  echo "Review and commit the exact $REGISTRY_DIR/*.pub roster, then request cutover again." >&2
  exit 3
fi

# [2/2] Execute the cutover. The CLI also requires --yes (double-gated).
echo "[2/2] Executing Slice 2.5 cutover (IRREVERSIBLE)..."
"$PY" -m threeway.cutover --repo . --coord-root . --yes

echo "=== Cutover complete: the signed bus is now the live coordination substrate. ==="
