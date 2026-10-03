#!/usr/bin/env bash
# Harden locally with the CMOS5L CI steps. Run tools/setup_harden.sh first.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TT_HOME="${TT_HOME:-$HOME/ttsetup}"
export PDK_ROOT="${PDK_ROOT:-$TT_HOME/pdk-cmos5l}"
export PDK=ihp-sg13cmos5l
# cairocffi needs Homebrew's libcairo. macOS drops DYLD_* through /usr/bin/env,
# so tt_tool.py is run with python directly.
export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"

# shellcheck disable=SC1091
source "$TT_HOME/venv/bin/activate"
cd "$REPO_ROOT"
python tt/tt_tool.py --create-user-config --ihp
python tt/tt_tool.py --harden --ihp
python tt/tt_tool.py --print-warnings --ihp
python tt/tt_tool.py --print-stats --ihp
python tt/tt_tool.py --print-cell-category --ihp
