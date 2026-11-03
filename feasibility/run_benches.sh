#!/bin/bash
cd /home/user/fly_or_fail/feasibility
PY=/home/user/venv-fly/bin/python
$PY bench_store_restore.py v630 100 4 sugarR_100Hz > logs/ref/05_bench_store_restore_v630_100Hz.log 2>&1
# naming/compile diagnosis: new lambda (77 Hz) => first pass compiles; identical second pass => cache hits
$PY bench_naming.py v630 77 4 > logs/ref/03_bench_naming_pass1_v630_77Hz.log 2>&1
$PY bench_naming.py v630 77 4 > logs/ref/03_bench_naming_pass2_identical_v630_77Hz.log 2>&1
echo BENCHES_DONE > logs/ref/03_benches_done.flag
