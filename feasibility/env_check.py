# Check Brian2 version, codegen target, compiler availability (Cython needs Python.h + g++)
import sys, sysconfig, os, shutil, subprocess
import brian2
from brian2 import prefs, NeuronGroup, ms, run, defaultclock
print("python", sys.version)
print("brian2", brian2.__version__)
print("Python.h exists:", os.path.exists(os.path.join(sysconfig.get_paths()['include'], 'Python.h')), sysconfig.get_paths()['include'])
print("g++:", shutil.which('g++'), subprocess.run(['g++','--version'],capture_output=True,text=True).stdout.splitlines()[0])
print("prefs codegen.target (configured):", prefs.codegen.target)
import time
G = NeuronGroup(10, 'dv/dt=-v/(10*ms):1', threshold='v>1', reset='v=0')
G.v='rand()'
t=time.time(); run(10*ms); print("first run (incl. compile) s:", time.time()-t)
from brian2.devices.device import get_device
print("device:", get_device())
from brian2.codegen.targets import codegen_targets
print("actual target of stateupdater:", G.state_updater.codeobj.__class__.__name__)
