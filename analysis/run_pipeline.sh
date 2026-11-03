#!/bin/bash
# STRUCT pipeline. Stage 1 (structure only) starts when ENG's Brian2 jobs are gone or the intact sims are done
# (CPU budget: <= 2 cores while Brian2 jobs run). Stage 2 needs all intact curves.
cd "$(dirname "$0")"
PY=${PY:-../venv/bin/python}
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
until [ -f logs/intact_done.txt ] || ! pgrep -f "ref_run.py|repro_run.py|brian2_extra.py|g0_brian2" >/dev/null; do sleep 30; done
$PY predictors.py v783 struct >> logs/pipeline.log 2>&1
$PY predictors.py v630 struct >> logs/pipeline.log 2>&1
until [ -f logs/intact_done.txt ]; do sleep 30; done
$PY predictors.py v783 all >> logs/pipeline.log 2>&1
$PY predictors.py v630 all >> logs/pipeline.log 2>&1
$PY predictors.py finalize >> logs/pipeline.log 2>&1
echo PIPELINE_DONE >> logs/pipeline.log
