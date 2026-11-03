# MN9 ID mapping v630 -> v783 by (a) annotation (cell_type CB0701, side, nerve) and (b) input-connectivity similarity.
# For the target v630 neuron X (notebook "right" MN9 720575940645521262) we compute the cosine similarity between X's presynaptic
# synapse-count vector (v630) and the presynaptic vector of EVERY v783 neuron (IDs shared between versions are directly comparable),
# and rank. The same analysis for the notebook "left" MN9 (720575940660219265, present in both versions) is the positive control.
import numpy as np, pandas as pd, scipy.sparse as sp
import simlib as S
A = pd.read_csv('/home/user/external/flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv', sep='\t', low_memory=False).set_index('root_id')
con = {v: pd.read_parquet(S.PATHS[v][1], columns=['Presynaptic_ID', 'Postsynaptic_ID', 'Connectivity', 'Excitatory x Connectivity']) for v in S.PATHS}
comp = {v: pd.read_csv(S.PATHS[v][0], index_col=0).index for v in S.PATHS}
X = S.MN9_R; L = S.MN9_L
print('target v630 right-notebook MN9', X, 'in v630:', X in set(comp['v630']), ' in v783:', X in set(comp['v783']), ' in annotation file:', X in A.index)
def in_vec(v, nid):
    c = con[v]; d = c[c.Postsynaptic_ID == nid]
    return pd.Series(d.Connectivity.values, index=d.Presynaptic_ID.values)
def out_vec(v, nid):
    c = con[v]; d = c[c.Presynaptic_ID == nid]
    return pd.Series(d.Connectivity.values, index=d.Postsynaptic_ID.values)
# v783 candidates ranked by input cosine
c783 = con['v783']
ids783 = comp['v783']; idx = pd.Series(np.arange(len(ids783)), index=ids783)
def rank(target, name, col='Presynaptic_ID', other='Postsynaptic_ID', vec=in_vec):
    tv = vec('v630', target)
    pre_known = tv.index[tv.index.isin(ids783)]
    print(f'--- {name} {target}: v630 has {len(tv)} {"presyn" if col=="Presynaptic_ID" else "postsyn"} partners, {int(tv.sum())} synapses; {len(pre_known)} partners ({tv[pre_known].sum()/tv.sum():.3f} of synapses) also exist as v783 IDs')
    sub = c783[c783[col].isin(pre_known)]          # edges touching the target's partners
    M = sp.csr_matrix((sub.Connectivity.values.astype(float), (idx[sub[other]].values, idx[sub[col]].values)), shape=(len(ids783), len(ids783)))
    t = np.zeros(len(ids783)); t[idx[pre_known].values] = tv[pre_known].values
    dots = M @ t
    # norm of each candidate over ALL its partners (not only the target's partners)
    full = c783.groupby(other).Connectivity.apply(lambda s: float(np.sqrt((s.values.astype(float) ** 2).sum())))
    nrm = np.zeros(len(ids783)); nrm[idx[full.index].values] = full.values
    cos = dots / (nrm * np.linalg.norm(tv.values.astype(float)) + 1e-12)
    top = np.argsort(-cos)[:6]
    for k in top:
        i = ids783[k]; a = A.loc[i] if i in A.index else None
        print(f'   cos={cos[k]:.3f} id={i} type={None if a is None else a.cell_type} side={None if a is None else a.side} super={None if a is None else a.super_class} nerve={None if a is None else a.nerve}')
    return cos
print('\n##### INPUT-vector similarity: v630 target vs all v783 neurons')
rank(L, 'POSITIVE CONTROL notebook-left MN9')
rank(X, 'notebook-right MN9')
print('\n##### OUTPUT-vector: MN9 are motor neurons (outputs to nerve), so input-only. Annotation facts:')
print(A[A.cell_type == 'CB0701'][['super_class', 'cell_class', 'cell_sub_class', 'cell_type', 'side', 'nerve', 'top_nt', 'flow']].to_string())
print('\nNotebook labels: MN9_L=720575940660219265 (annotation side=%s); candidate partner 720575940618238523 (annotation side=%s)' % (A.loc[720575940660219265, 'side'], A.loc[720575940618238523, 'side']))
# direct input overlap between v630 X and the v783 candidate and between v630 L and v783 L / cross
for nm, a_v, a_id, b_v, b_id in [('X(v630) vs cand(v783)', 'v630', X, 'v783', 720575940618238523), ('X(v630) vs L(v783)', 'v630', X, 'v783', L),
                                  ('L(v630) vs L(v783)', 'v630', L, 'v783', L), ('L(v630) vs cand(v783)', 'v630', L, 'v783', 720575940618238523)]:
    a = in_vec(a_v, a_id); b = in_vec(b_v, b_id); j = a.index.intersection(b.index)
    cos = float((a[j] * b[j]).sum() / (np.linalg.norm(a) * np.linalg.norm(b)))
    print(f'{nm}: n_in {len(a)} vs {len(b)}, shared presyn {len(j)}, input-vector cosine {cos:.3f}, in-synapses {int(a.sum())} vs {int(b.sum())}')
