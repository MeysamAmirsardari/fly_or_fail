# Check flywire_annotations Supplemental_file1 coverage vs v783 Completeness; labels for MN9 and sugar GRNs; NT confidence.
import pandas as pd, numpy as np
import simlib as S
A = pd.read_csv('/home/user/external/flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv', sep='\t', low_memory=False)
print('rows', len(A), 'unique root_id', A.root_id.nunique()); print('columns', list(A.columns))
comp = pd.read_csv(S.PATHS['v783'][0], index_col=0).index
con = pd.read_parquet(S.PATHS['v783'][1], columns=['Presynaptic_ID', 'Excitatory'])
sg = con.drop_duplicates('Presynaptic_ID').set_index('Presynaptic_ID')['Excitatory']
inA = comp.isin(A.root_id); print('v783 completeness neurons', len(comp), 'with annotation row', int(inA.sum()), 'frac', round(inA.mean(), 4))
print('annotation rows not in v783 completeness:', int((~A.root_id.isin(comp)).sum()))
M = A[A.root_id.isin(comp)].set_index('root_id')
for c in ['super_class', 'cell_class', 'cell_type', 'side', 'ito_lee_hemilineage', 'hartenstein_hemilineage', 'top_nt', 'top_nt_conf', 'flow', 'known_nt']:
    print(f'{c}: non-null {M[c].notna().sum()} ({M[c].notna().mean():.3f}); n unique {M[c].nunique()}')
print('super_class counts:\n', M.super_class.value_counts(dropna=False).to_string())
print('side counts:', M.side.value_counts(dropna=False).to_dict())
print('top_nt counts:', M.top_nt.value_counts(dropna=False).to_dict())
print('top_nt_conf quantiles', M.top_nt_conf.quantile([.05, .25, .5, .75, .95]).round(3).to_dict())
# Model sign (Excitatory column, per presynaptic neuron) vs top_nt
j = M.join(sg.rename('model_sign'), how='inner')
j['nt_inhib'] = j.top_nt.isin(['gaba', 'glutamate'])
print('Model sign vs top_nt (neurons with outgoing edges):')
print(pd.crosstab(j.top_nt.fillna('NA'), j.model_sign).to_string())
print('model sign agrees with {ach,dop,ser,oct => +1; gaba,glut => -1}:')
pos = {'acetylcholine': 1, 'gaba': -1, 'glutamate': -1}
jj = j[j.top_nt.isin(pos)]; print('  agreement frac among ach/gaba/glut neurons', round((jj.top_nt.map(pos) == jj.model_sign).mean(), 4), 'n', len(jj))
print('  mean top_nt_conf among disagreeing vs agreeing:', jj[jj.top_nt.map(pos) != jj.model_sign].top_nt_conf.mean(), jj[jj.top_nt.map(pos) == jj.model_sign].top_nt_conf.mean())
# labels for key neurons
cols = ['super_class', 'cell_class', 'cell_sub_class', 'cell_type', 'hemibrain_type', 'side', 'ito_lee_hemilineage', 'top_nt', 'top_nt_conf', 'flow', 'nerve']
for nm, idl in [('MN9_L', [S.MN9_L]), ('MN9_R', [S.MN9_R]), ('sugar_R', S.ids('sugar_GRN_right.csv')), ('water_R', S.ids('water_GRN_right.csv')),
                ('bitter_R', S.ids('bitter_GRN_right.csv')), ('Ir94e_R', S.ids('Ir94e_GRN_right.csv')), ('sugar_L', S.ids('sugar_GRN_left.csv'))]:
    print('-----', nm, 'n ids', len(idl), 'in annotation file (783 root ids):', int(pd.Series(idl).isin(A.root_id).sum()))
    sub = A[A.root_id.isin(idl)]
    print(sub[['root_id'] + cols].to_string(max_colwidth=22) if len(sub) <= 6 else sub[cols].astype(str).apply(lambda s: s.value_counts().to_dict() if s.name not in ['top_nt_conf'] else pd.Series({'median': sub.top_nt_conf.median()}).to_dict()).to_string())
