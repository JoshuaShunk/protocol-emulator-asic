#!/bin/bash
# Run MCY from a clean database. Fails if the unmutated design fails, any
# task errors, or a killed mutant is formally equivalent.
set -euo pipefail
cd "$(dirname "$0")"
source ../../../env.sh
python ../../preflight.py

rm -rf database tasks
mcy init > mcy-init.log 2>&1
mcy run -j"${JOBS:-6}" > mcy-run.log 2>&1 || { tail -20 mcy-run.log; exit 1; }

baseline=$(sqlite3 database/db.sqlite3 \
  "select r.result from results r join mutations m using (mutation_id)
   where m.mutation = 'mutate -mode none' and r.test = 'test_sim'")
if [ "$baseline" != "PASS" ]; then
  echo "unmutated design did not pass test_sim (got '${baseline}'); results are not valid" >&2
  exit 1
fi

errors=$(sqlite3 database/db.sqlite3 "select count(*) from results where result = 'ERROR'")
if [ "$errors" != "0" ]; then
  echo "$errors task(s) ended in ERROR; results are not valid" >&2
  exit 1
fi

eqgap=$(sqlite3 database/db.sqlite3 "select count(*) from tags where tag = 'EQGAP'")
if [ "$eqgap" != "0" ]; then
  echo "$eqgap killed mutation(s) are formally equivalent: the simulation fails on correct behaviour" >&2
  exit 1
fi

mcy status 2>&1 | sed -n '/Database contains/,$p'
