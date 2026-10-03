#!/usr/bin/env bash
# Harden with the CMOS5L CI steps in a container that mounts only this
# repository and the PDK. Run tools/setup_harden.sh first.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PDK_ROOT="${PDK_ROOT:-$HOME/ttsetup/pdk-cmos5l}"
LIBRELANE_IMAGE="ghcr.io/librelane/librelane:3.1.0.dev3"
IMAGE="pemu-harden:librelane-3.1.0.dev3"

image_env() {
  docker image inspect "$LIBRELANE_IMAGE" --format '{{range .Config.Env}}{{println .}}{{end}}'
}

env_file="$(mktemp)"
trap 'rm -f "$env_file"' EXIT
image_env | grep -v -E '^(PATH|USER|EDITOR|NIX_PATH|MANPATH)=' | grep . > "$env_file"
nix_path="$(image_env | sed -n 's/^PATH=//p')"

docker run --rm \
  --env-file "$env_file" \
  -e PATH="$nix_path:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
  -e HOME=/tmp \
  -e PDK_ROOT=/pdk \
  -e PDK=ihp-sg13cmos5l \
  -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
  -v "$REPO_ROOT:/work" \
  -v "$PDK_ROOT:/pdk:ro" \
  -w /work \
  "$IMAGE" \
  bash -c '
    set -euo pipefail
    tt() { /opt/tt/bin/python tt/tt_tool.py --ihp "$@"; }
    tt --create-user-config
    tt --harden --no-docker
    tt --print-warnings
    tt --print-stats
    tt --print-cell-category
  '
