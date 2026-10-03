#!/usr/bin/env bash
# Install the versions used by TinyTapeout/tt-gds-action@ihp-cmos5l and build
# the hardening image.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PDK_ROOT="${PDK_ROOT:-$HOME/ttsetup/pdk-cmos5l}"
TOOLS_REF="ihp-sg13cmos5l"
IHP_PDK_REPO="https://github.com/IHP-GmbH/IHP-Open-PDK.git"
IHP_PDK_REV="2bbec755dc67ca3db0261c3d6163e15735d66710"
IMAGE="pemu-harden:librelane-3.1.0.dev3"

if [ ! -d "$REPO_ROOT/tt" ]; then
  git clone -q --depth 1 -b "$TOOLS_REF" https://github.com/TinyTapeout/tt-support-tools "$REPO_ROOT/tt"
fi

if [ ! -f "$PDK_ROOT/ihp-sg13cmos5l/SOURCES" ]; then
  mkdir -p "$PDK_ROOT"
  git -C "$PDK_ROOT" init -q
  git -C "$PDK_ROOT" fetch -q --depth 1 "$IHP_PDK_REPO" "$IHP_PDK_REV"
  git -C "$PDK_ROOT" checkout -q FETCH_HEAD
  echo "IHP-Open-PDK $IHP_PDK_REV" > "$PDK_ROOT/ihp-sg13cmos5l/SOURCES"
fi

docker build -t "$IMAGE" -f "$REPO_ROOT/tools/docker/Dockerfile" "$REPO_ROOT/tt"

echo "tt-support-tools: $(git -C "$REPO_ROOT/tt" rev-parse --short HEAD) ($TOOLS_REF)"
echo "PDK: $(cat "$PDK_ROOT/ihp-sg13cmos5l/SOURCES")"
echo "image: $IMAGE"
