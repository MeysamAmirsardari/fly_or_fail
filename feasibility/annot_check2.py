# Detail: full cell_sub_class labels of notebook 'sugar R' / 'water R' sets, missing-from-v783 IDs, and per-ID MN9 labels
import pandas as pd, simlib as S
A = pd.read_csv('/home/user/external/flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv', sep='\t', low_memory=False).set_index('root_id')
v783 = set(pd.read_csv(S.PATHS['v783'][0], index_col=0).index)
for cls in ['sugar_GRN_right', 'water_GRN_right', 'bitter_GRN_right', 'Ir94e_GRN_right', 'sugar_GRN_left']:
    d = pd.read_csv(S.IDS + cls + '.csv')
    print('====', cls, 'n', len(d), ' missing from v783 completeness:', d[~d.in_v783].flywire_id.tolist(), ' missing from annotation:', [i for i in d.flywire_id if i not in A.index])
    sub = A.loc[[i for i in d.flywire_id if i in A.index]]
    print(sub.groupby(['cell_sub_class', 'cell_type', 'side'], dropna=False).size().to_string())
print('MN9 labels:'); print(A.loc[[S.MN9_L], ['super_class', 'cell_class', 'cell_sub_class', 'cell_type', 'side', 'nerve', 'top_nt']].to_string())
print('MN9_R (720575940645521262) in 783 completeness:', S.MN9_R in v783)
mn = A[(A.super_class == 'motor')]
print('motor super_class cell_sub_class counts:', mn.cell_sub_class.value_counts(dropna=False).to_dict())
print('cell_type CB0701 neurons (MN9 type?):', A[A.cell_type == 'CB0701'][['side', 'cell_sub_class', 'nerve']].reset_index().to_string())
print('cell_type MN9-like: types containing "MN9":', A[A.cell_type.astype(str).str.contains('MN9')].shape[0])
