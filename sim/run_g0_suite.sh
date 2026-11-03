#!/bin/bash
# G0 suite: Brian2 (original objects, injected CRN input) vs fastlif, spike-for-spike, full networks.
cd "$(dirname "$0")"
PY=${PY:-../venv/bin/python}
$PY g0_brian2_exact.py v783 100 0
$PY g0_brian2_exact.py v630 200 1
$PY g0_brian2_exact.py v783 200 2
$PY g0_brian2_exact.py v630 400 3
$PY g0_brian2_exact.py v630 100 4 720575940622695448
$PY g0_brian2_exact.py v783 100 5 720575940627383685
$PY g0_brian2_exact.py v630 100 6 720575940617937543
$PY g0_brian2_exact.py v783 400 7 720575940619973712
echo G0SUITEDONE
