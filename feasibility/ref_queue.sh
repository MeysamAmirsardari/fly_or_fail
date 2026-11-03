#!/bin/bash
# Runs ref_jobs.txt with at most 2 parallel jobs. Each TRIAL runs in a FRESH python process (ref_run.py ... max_new=1) because
# Brian2 auto-generated names advance within a process => Cython re-compilation every trial (~40 s) (see report, benchmark section).
# Resumable: finished trials (shards) are skipped.
cd /home/user/fly_or_fail/feasibility
PY=/home/user/venv-fly/bin/python
run_one() { ver=$1; exp=$2; rate=$3; n=$4; sl=$5
  L=logs/ref/10_${ver}_${exp}.log
  for ((t=0; t<n; t++)); do
    f=out/ref/$ver/_shards/$exp/trial_$(printf %02d $t).json
    [ -f $f ] || $PY ref_run.py $ver $exp $rate $n $sl 0 1 >> $L 2>&1
  done
  [ -f out/ref/$ver/$exp.parquet ] || $PY ref_run.py $ver $exp $rate $n $sl 0 1 >> $L 2>&1
  echo "done $ver $exp $(date +%T)"; }
export -f run_one; export PY
cat ref_jobs.txt | xargs -P 2 -L 1 bash -c 'run_one $0 $1 $2 $3 $4'
echo QUEUE_ALLDONE
