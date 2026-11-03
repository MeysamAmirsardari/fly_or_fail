#!/bin/bash
cd /home/user/fly_or_fail/feasibility
PY=/home/user/venv-fly/bin/python
$PY repro_run.py v630 sugarR_200Hz 200 10 
$PY repro_run.py v630 sugarR_100Hz 100 10
$PY repro_run.py v630 sugarR-720575940617937543_100Hz 100 10 720575940617937543
$PY repro_run.py v783 sugarR_200Hz 200 10
$PY repro_run.py v783 sugarR_100Hz 100 10
$PY repro_run.py v783 sugarR-720575940617937543_100Hz 100 10 720575940617937543
echo ALLDONE
