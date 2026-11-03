#!/bin/bash
# sequential intact curves (lean memory); usage: bash run_intact_all.sh
cd "$(dirname "$0")"
for c in "v783 shiu" "v783 pure" "v630 shiu" "v630 pure"; do
  set -- $c
  ${PY:-../venv/bin/python} intact.py $1 $2 2 > logs/intact_$1_$2.log 2>&1
done
echo ALLDONE > logs/intact_done.txt
