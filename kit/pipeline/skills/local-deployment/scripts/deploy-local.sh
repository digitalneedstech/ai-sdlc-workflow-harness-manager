#!/usr/bin/env bash
# Local build + optional preview + health checks. See ../assets/local-deploy-runbook.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SLUG="${1:-}"
TARGET="${2:-auto}"
STORE_PORT="${STORE_PORT:-4173}"
HEALTH_PATH="${HEALTH_PATH:-/}"
ENGINE_START="${ENGINE_START:-0}"
RUN_PYTEST="${RUN_PYTEST:-0}"

if [[ -z "$SLUG" ]]; then
  echo "usage: deploy-local.sh <feature-slug> [auto|ecommerce-store|chorus|both]" >&2
  exit 2
fi

FEAT="$ROOT/features/$SLUG"
mkdir -p "$FEAT"
RESULT="$FEAT/deploy-result.env"
LOG="$FEAT/deploy-log.txt"
: >"$LOG"

log() { printf '%s\n' "$*" | tee -a "$LOG"; }

listening() {
  python3 - "$1" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
s.settimeout(1)
try:
    s.connect(("127.0.0.1", port))
except OSError:
    sys.exit(1)
finally:
    s.close()
sys.exit(0)
PY
}

http_ok() {
  python3 - "$1" <<'PY'
import sys, urllib.error, urllib.request
url = sys.argv[1]
try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        sys.exit(0 if 200 <= resp.status < 400 else 1)
except (urllib.error.URLError, OSError, TimeoutError):
    sys.exit(1)
PY
}

write_result() {
  cat >"$RESULT" <<EOF
OVERALL=${OVERALL:-failed}
DEPLOY_TARGET=$TARGET
STORE_BUILD=${STORE_BUILD:-skipped}
STORE_HEALTH=${STORE_HEALTH:-skipped}
STORE_URL=${STORE_URL:-}
CHORUS_WEB_BUILD=${CHORUS_WEB_BUILD:-skipped}
PYTEST=${PYTEST:-skipped}
ENGINE_HEALTH=${ENGINE_HEALTH:-skipped}
ENGINE_STARTED=${ENGINE_STARTED:-no}
PREVIEW_STARTED=${PREVIEW_STARTED:-no}
ENGINE_URL=${ENGINE_URL:-}
EOF
}

detect_auto() {
  local notes="$FEAT/implementation-notes.md"
  local handoff="$FEAT/HANDOFF-developer.md"
  local blob=""
  [[ -f "$notes" ]] && blob+=" $(cat "$notes")"
  [[ -f "$handoff" ]] && blob+=" $(cat "$handoff")"
  local store=0 chorus=0
  [[ "$blob" == *ecommerce-store* ]] && store=1
  [[ "$blob" == *"/web/"* || "$blob" == *"web/src"* || "$blob" == *canvas_engine* || "$blob" == *canvas_agent* ]] && chorus=1
  if [[ $store -eq 0 && $chorus -eq 0 ]]; then
    echo "ecommerce-store"
  elif [[ $store -eq 1 && $chorus -eq 1 ]]; then
    echo "both"
  elif [[ $chorus -eq 1 ]]; then
    echo "chorus"
  else
    echo "ecommerce-store"
  fi
}

if [[ "$TARGET" == "auto" ]]; then
  TARGET="$(detect_auto)"
  log "auto target → $TARGET"
fi

cd "$ROOT"
OVERALL=failed
STORE_BUILD=skipped
STORE_HEALTH=skipped
STORE_URL=""
CHORUS_WEB_BUILD=skipped
PYTEST=skipped
ENGINE_HEALTH=skipped
ENGINE_STARTED=no
PREVIEW_STARTED=no
ENGINE_URL=""

need_store=0
need_chorus=0
[[ "$TARGET" == "ecommerce-store" || "$TARGET" == "both" ]] && need_store=1
[[ "$TARGET" == "chorus" || "$TARGET" == "both" ]] && need_chorus=1

if [[ $need_store -eq 1 ]]; then
  if [[ ! -d "$ROOT/ecommerce-store/node_modules" ]]; then
    log "FAIL: ecommerce-store/node_modules missing (run npm install outside this pipeline)"
    write_result
    exit 1
  fi
  log "building ecommerce-store"
  (cd "$ROOT/ecommerce-store" && npm run build) >>"$LOG" 2>&1
  STORE_BUILD=passed
  STORE_URL="http://127.0.0.1:${STORE_PORT}/"
  if listening "$STORE_PORT"; then
    log "port $STORE_PORT already in use — health-check existing listener"
  else
    log "starting vite preview on 127.0.0.1:$STORE_PORT"
    (cd "$ROOT/ecommerce-store" && npm run preview -- --host 127.0.0.1 --port "$STORE_PORT") >>"$LOG" 2>&1 &
    echo $! >"$FEAT/.preview.pid"
    PREVIEW_STARTED=yes
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      listening "$STORE_PORT" && break
      sleep 0.5
    done
  fi
  if http_ok "$STORE_URL" && http_ok "http://127.0.0.1:${STORE_PORT}${HEALTH_PATH}"; then
    STORE_HEALTH=passed
  else
    log "FAIL: storefront health ${STORE_URL}"
    write_result
    exit 1
  fi
fi

if [[ $need_chorus -eq 1 ]]; then
  if [[ ! -d "$ROOT/web/node_modules" ]]; then
    log "FAIL: web/node_modules missing"
    write_result
    exit 1
  fi
  log "building web/"
  (cd "$ROOT/web" && npm run build) >>"$LOG" 2>&1
  CHORUS_WEB_BUILD=passed
  if [[ "$RUN_PYTEST" == "1" ]]; then
    log "pytest"
    (cd "$ROOT" && uv run pytest -q) >>"$LOG" 2>&1
    PYTEST=passed
  fi
  ENGINE_URL="http://127.0.0.1:8000/health"
  if listening 8000; then
    if http_ok "$ENGINE_URL"; then
      ENGINE_HEALTH=passed
    else
      log "FAIL: engine listening but /health failed"
      write_result
      exit 1
    fi
  elif [[ "$ENGINE_START" == "1" ]]; then
    log "starting canvas-engine on :8000"
    (cd "$ROOT" && uv run canvas-engine) >>"$LOG" 2>&1 &
    echo $! >"$FEAT/.engine.pid"
    ENGINE_STARTED=yes
    for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
      http_ok "$ENGINE_URL" && break
      sleep 0.5
    done
    if http_ok "$ENGINE_URL"; then
      ENGINE_HEALTH=passed
    else
      log "FAIL: engine start did not become healthy"
      write_result
      exit 1
    fi
  else
    ENGINE_HEALTH=skipped
    log "engine not on :8000 (ENGINE_START=0) — web build only"
  fi
fi

OVERALL=passed
write_result
log "OVERALL=passed target=$TARGET"
cat "$RESULT"
