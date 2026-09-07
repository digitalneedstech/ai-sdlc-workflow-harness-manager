#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"

if command -v uv >/dev/null 2>&1; then
  exec uv tool install --force "$root"
fi
if command -v pipx >/dev/null 2>&1; then
  exec pipx install --force "$root"
fi

echo "pipeline-kit requires uv or pipx for a tool install." >&2
echo "Install uv (https://docs.astral.sh/uv/) or pipx, then rerun ./install.sh." >&2
exit 1
