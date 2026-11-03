"""common: frozen identifiers and data loading for the STRUCT predictor pipeline (PROJECT_DESIGN v1.0 §5.1).

Left/right convention (fixed HERE, asserted in check_conventions()):
  * Shiu's notebook "right" sugar GRNs = FlyWire annotation side "left".
  * Primary readout T = MN9 720575940660219265, annotation CB0701 side "right" => CONTRALATERAL to the GRNs.
  * Secondary readout = ipsilateral MN9: v783 CB0701 side "left" 720575940618238523; v630 720575940645521262 (per ENG).
  * The two MN9s are NEVER summed or averaged: every T-dependent quantity is computed for one readout at a time.
"""
import os, hashlib
import numpy as np, pandas as pd

# Paths: repo-relative; external clones live in $NJ_EXTERNAL (default: <repo>/../external, see README).
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
EXTERNAL = os.path.abspath(os.environ.get('NJ_EXTERNAL', REPO + '../external')) + '/'
DATA = EXTERNAL + 'Drosophila_brain_model/'
PATHS = {'v630': (DATA + '2023_03_23_completeness_630_final.csv', DATA + '2023_03_23_connectivity_630_final.parquet'),
         'v783': (DATA + 'Completeness_783.csv', DATA + 'Connectivity_783.parquet')}
ANNOT = EXTERNAL + 'flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv'
IDS = REPO + 'feasibility/ids/'
ROOT = REPO + 'analysis/'
OUT = ROOT + 'out/'
SIMDIR = REPO + 'sim/'

MN9_CONTRA = 720575940660219265                      # primary T (both versions)
MN9_IPSI = {'v783': 720575940618238523, 'v630': 720575940645521262}
READOUTS = {'contra': lambda ver: MN9_CONTRA, 'ipsi': lambda ver: MN9_IPSI[ver]}

# External-arm cell types (PROJECT_DESIGN v1.0 §7.2 S4/S5). IDs from sez_neurons.pickle; Zorro is not a pickle key:
# Zorro = FlyWire cell_type CB0192 (both members), identified from Jacobs et al. 2024 STAR Methods Zorro ID
# 720575940629888530 (= Shiu & Sterne 2022 "Zorro R"), which is present in v630/v783 and annotated CB0192.
EXT_TYPES = {'Rattle': 'rattle', 'Usnea': 'usnea', 'Zorro': None, 'Clavicle': 'clavicle', 'G2N-1': 'G2N_1',
             'FMIn': 'FMIn', 'Phantom': 'phantom', 'Bract': 'bract', 'Fdg': 'Fdg', 'Roundup': 'roundup'}
ZORRO_SEED_ID = 720575940629888530
ZORRO_CELL_TYPE = 'CB0192'


def md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


_CACHE = {}


def load_annotations():
    if 'annot' not in _CACHE:
        A = pd.read_csv(ANNOT, sep='\t', low_memory=False,
                        usecols=['root_id', 'super_class', 'cell_class', 'cell_sub_class', 'cell_type', 'side', 'top_nt'])
        _CACHE['annot'] = A.set_index('root_id')
    return _CACHE['annot']


def load_graph(ver):
    """Whole-brain connectome, memory-lean (int32/int8 arrays, read column by column). Returns dict with
    fid (n,) FlyWire ids in completeness row order (= Brian2 index); pre, post (m,) int32 indices; nsyn (m,) int32
    synapse counts n_ij >= 1; sign (m,) int8 +-1 of the PRESYNAPTIC neuron.
    Asserts: rows sorted by presynaptic index, no duplicate pairs, no self loops, sign constant per presynaptic neuron,
    'Excitatory x Connectivity' == sign * n."""
    if ('g', ver) in _CACHE: return _CACHE[('g', ver)]
    import pyarrow.parquet as pq
    comp = pd.read_csv(PATHS[ver][0], index_col=0)
    n = len(comp)
    pf = pq.ParquetFile(PATHS[ver][1])
    col = lambda c, dt: pf.read(columns=[c]).column(0).to_numpy().astype(dt)
    pre = col('Presynaptic_Index', np.int32); post = col('Postsynaptic_Index', np.int32)
    nsyn = col('Connectivity', np.int32); sign = col('Excitatory', np.int8)
    exn = col('Excitatory x Connectivity', np.int32)
    assert np.array_equal(sign.astype(np.int32) * nsyn, exn); del exn
    assert np.all(nsyn >= 1) and set(np.unique(sign).tolist()) <= {-1, 1}
    assert np.all(np.diff(pre) >= 0), 'not sorted by presynaptic index'
    assert not np.any(pre == post)
    key = pre.astype(np.int64) * n + post
    assert len(np.unique(key)) == len(key), 'duplicate edges'; del key
    s_by_pre = np.zeros(n, np.int8); s_by_pre[pre] = sign
    assert np.array_equal(s_by_pre[pre], sign), 'sign not constant per presynaptic neuron'
    g = dict(ver=ver, n=n, fid=comp.index.values.astype(np.int64), pre=pre, post=post, nsyn=nsyn, sign=sign,
             f2i=pd.Series(np.arange(n), index=comp.index.values.astype(np.int64)))
    _CACHE[('g', ver)] = g
    return g


def idx_of(g, fids, strict=True):
    out = []
    for f in fids:
        f = int(f)
        if f in g['f2i'].index: out.append(int(g['f2i'][f]))
        elif strict: raise KeyError(f)
    return np.array(out, np.int64)


def present_ids(ver):
    """FlyWire ids in the completeness table (cheap; does not load the connectivity)."""
    if ('present', ver) not in _CACHE:
        _CACHE[('present', ver)] = set(pd.read_csv(PATHS[ver][0], index_col=0).index.astype(np.int64).tolist())
    return _CACHE[('present', ver)]


def S_shiu(ver):
    s = pd.read_csv(IDS + 'sugar_GRN_right.csv').flywire_id.astype(np.int64).tolist()
    present = present_ids(ver)
    return [f for f in s if f in present]


def S_pure_all():
    """All v783 neurons annotated cell_sub_class 'sugar' (LB3c) or 'sugar/low_salt' (LB3b), annotation side 'left'
    (= the side of Shiu's 'right' list)."""
    A = load_annotations()
    m = A.cell_sub_class.isin(['sugar', 'sugar/low_salt']) & (A.side == 'left')
    return sorted(int(i) for i in A.index[m])


def S_pure(ver):
    present = present_ids(ver)
    return [f for f in S_pure_all() if f in present]


INPUTS = {'shiu': S_shiu, 'pure': S_pure}


def ext_type_members(ver):
    import pickle
    d = pickle.load(open(DATA + 'sez_neurons.pickle', 'rb'))
    A = load_annotations()
    present = present_ids(ver)
    out = {}
    for name, key in EXT_TYPES.items():
        if key is None:
            assert A.loc[ZORRO_SEED_ID, 'cell_type'] == ZORRO_CELL_TYPE
            ids = sorted(int(i) for i in A.index[A.cell_type == ZORRO_CELL_TYPE])
        else:
            ids = [int(i) for i in d[key]]
        out[name] = dict(all=ids, present=[i for i in ids if i in present])
    return out


def check_conventions():
    A = load_annotations()
    assert A.loc[MN9_CONTRA, 'cell_type'] == 'CB0701' and A.loc[MN9_CONTRA, 'side'] == 'right'
    assert A.loc[MN9_IPSI['v783'], 'cell_type'] == 'CB0701' and A.loc[MN9_IPSI['v783'], 'side'] == 'left'
    sides = A.loc[[f for f in S_shiu('v783') if f in A.index], 'side']
    assert (sides == 'left').all(), 'S_shiu should be annotation side left'
    return True
