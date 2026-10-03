#!/bin/bash
# Run the self-test on one mutant; ERROR means the environment is wrong.
exec 2>&1
set -ex

# The mcy launcher puts OSS CAD Suite's bin first on PATH.
unset PYTHONHOME PYTHONEXECUTABLE
source "$PRJDIR/../../../env.sh"
python "$PRJDIR/../../preflight.py" || { echo "1 ERROR" > output.txt; exit 0; }

bash $SCRIPTS/create_mutated.sh

status=0
BUILD_DIR="$PWD/sim" python -m verif.smoke.run "$PWD/mutated.v" > sim.out || status=$?

if [ "$status" -eq 0 ]; then
	echo "1 PASS" > output.txt
elif [ "$status" -eq 1 ]; then
	echo "1 FAIL" > output.txt
else
	echo "1 ERROR" > output.txt
fi

exit 0
