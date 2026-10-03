#!/bin/bash
# Bounded equivalence of original vs mutant; FAIL means outputs can differ.
exec 2>&1
set -ex

bash $SCRIPTS/create_mutated.sh -c -o mutated.il

ln -s ../../test_eq.sv ../../test_eq.sby .
sby -f test_eq.sby

awk "{ print 1, \$1; }" test_eq/status >> output.txt

exit 0
