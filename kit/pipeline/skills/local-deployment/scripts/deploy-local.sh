#!/usr/bin/env bash
# Project overlay. Rewrite the body for this repository before devops can succeed.
# Contract: ../assets/local-deploy-runbook.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SLUG="${1:-}"
TARGET="${2:-auto}"

if [[ -z "$SLUG" ]]; then
  echo "usage: deploy-local.sh <feature-slug> [target]" >&2
  echo "target must be a name from .pipeline/config.json deploy.targets" >&2
  exit 2
fi

FEAT="$ROOT/features/$SLUG"
mkdir -p "$FEAT"
RESULT="$FEAT/deploy-result.env"
LOG="$FEAT/deploy-log.txt"
: >"$LOG"

log() { printf '%s\n' "$*" | tee -a "$LOG"; }

cat >"$RESULT" <<EOF
OVERALL=failed
DEPLOY_TARGET=$TARGET
APP_A_HEALTH=skipped
APP_B_HEALTH=skipped
EOF

log "deploy-local.sh is a placeholder."
log "Edit .pipeline/skills/local-deployment/scripts/deploy-local.sh"
log "and .pipeline/skills/local-deployment/assets/local-deploy-runbook.md"
log "so they match this repository's apps, ports, and health URLs."
log "See docs/CUSTOMER-GUIDE.md section 5."
exit 1
