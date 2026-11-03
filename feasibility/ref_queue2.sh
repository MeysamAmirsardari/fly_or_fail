#!/bin/bash
# Same as ref_queue.sh but jobs file is $1 and column 6 is the Brian2 seed offset (trial t uses seed offset+t). Fresh process per trial.
cd /home/user/fly_or_fail/feasibility
PY=/home/user/venv-fly/bin/python
run_one() { ver=$1; exp=$2; rate=$3; n=$4; sl=$5; so=$6
  L=logs/ref/10_${ver}_${exp}.log
  for ((t=0; t<n; t++)); do
    f=out/ref/$ver/_shards/$exp/trial_$(printf %02d $t).json
    [ -f $f ] || $PY ref_run.py $ver $exp $rate $n $sl $so 1 >> $L 2>&1
  done
  [ -f out/ref/$ver/$exp.parquet ] || $PY ref_run.py $ver $exp $rate $n $sl $so 1 >> $L 2>&1
  echo "done $ver $exp $(date +%T)"; }
export -f run_one; export PY
cat $1 | xargs -P 2 -L 1 bash -c 'run_one $0 $1 $2 $3 $4 $5'
echo QUEUE2_ALLDONE
