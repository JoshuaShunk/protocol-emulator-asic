# Source this file: puts OSS CAD Suite, then the project venv, on PATH.
OSS_CAD_SUITE="${OSS_CAD_SUITE:-$HOME/opt/oss-cad-suite}"
if [ ! -f "$OSS_CAD_SUITE/environment" ]; then
  echo "OSS CAD Suite not found at $OSS_CAD_SUITE" >&2
  return 1
fi
# shellcheck disable=SC1091
source "$OSS_CAD_SUITE/environment"
# OSS CAD Suite's vvp wrapper sets PYTHONHOME to its own Python; use Homebrew's Icarus.
export PATH="$(brew --prefix icarus-verilog)/bin:$PATH"
_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
# shellcheck disable=SC1091
source "$_REPO_ROOT/.venv/bin/activate"
export PYTHONPATH="$_REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
unset _REPO_ROOT
