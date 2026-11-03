"""Thin helpers around the Shiu et al. model (imported, NOT modified) used by all feasibility probes.
Adds: phase-timed trial (construction vs poisson/silence vs simulation), RSS tracking, ID helpers."""
import sys, time, resource, os
sys.path.insert(0, '/home/user/external/Drosophila_brain_model')
import numpy as np, pandas as pd
import model as M, utils as U
from brian2 import Network, ms, Hz, mV
D = '/home/user/external/Drosophila_brain_model/'
PATHS = {
    'v630': (D + '2023_03_23_completeness_630_final.csv', D + '2023_03_23_connectivity_630_final.parquet'),
    'v783': (D + 'Completeness_783.csv', D + 'Connectivity_783.parquet'),
}
IDS = '/home/user/fly_or_fail/feasibility/ids/'
MN9_L = 720575940660219265
MN9_R = 720575940645521262

def ids(cls_file):
    return pd.read_csv(IDS + cls_file).flywire_id.tolist()

def sugar_right(ver):
    s = ids('sugar_GRN_right.csv')
    comp = pd.read_csv(PATHS[ver][0], index_col=0).index
    return [i for i in s if i in set(comp)]

def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0   # peak RSS so far, MB (Linux: KB)

def timed_trial(exc, exc2, slnc, ver, params, flyid2i):
    """Same operations as model.run_trial but with wall-time per phase. Returns (spk_trn, timings dict)."""
    pc, pn = PATHS[ver]
    t = {}
    t0 = time.perf_counter()
    neu, syn, spk_mon = M.create_model(pc, pn, params)
    t['construct'] = time.perf_counter() - t0
    t0 = time.perf_counter()
    poi_inp, neu = M.poi(neu, [flyid2i[n] for n in exc], [flyid2i[n] for n in exc2], params)
    t['poisson'] = time.perf_counter() - t0
    t0 = time.perf_counter()
    syn = M.silence([flyid2i[n] for n in slnc], syn)
    t['silence'] = time.perf_counter() - t0
    net = Network(neu, syn, spk_mon, *poi_inp)
    t0 = time.perf_counter()
    net.run(duration=params['t_run'])
    t['run'] = time.perf_counter() - t0
    spk = M.get_spk_trn(spk_mon)
    t['total'] = sum(t.values())
    t['rss_mb'] = rss_mb()
    return spk, t

def flyid2i_map(ver):
    comp = pd.read_csv(PATHS[ver][0], index_col=0)
    return {j: i for i, j in enumerate(comp.index)}

def spk_to_df(res, name, flyid2i):
    i2f = {v: k for k, v in flyid2i.items()}
    return M.construct_dataframe(res, name, i2f)
