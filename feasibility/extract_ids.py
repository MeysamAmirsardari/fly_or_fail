# Extract FlyWire ID lists from example.ipynb / figures.ipynb (first definition of each list, via exec of
# only the assignment cells that define plain lists/ints) + sez_neurons.pickle (opcode-checked: pure data).
import json, ast, pickle, csv, re
import pandas as pd
D='/home/user/external/Drosophila_brain_model/'
OUT='/home/user/fly_or_fail/feasibility/ids/'
v783=set(pd.read_csv(D+'Completeness_783.csv',index_col=0).index)
v630=set(pd.read_csv(D+'2023_03_23_completeness_630_final.csv',index_col=0).index)
rows=[]
def add(name_cls, side, ids, nb, cell):
    for k,i in enumerate(ids):
        rows.append(dict(flywire_id=i,name=f'{name_cls}_{k+1}',class_=name_cls,side=side,source_notebook=nb,cell_index=cell,
                         in_v630=i in v630,in_v783=i in v783))
def parse_assign(src):
    """return dict var -> literal (int or list of ints) for simple assignments of ints/lists in a cell"""
    out={}
    try: tree=ast.parse(src)
    except SyntaxError: return out
    for n in tree.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try: out[n.targets[0].id]=ast.literal_eval(n.value)
            except Exception: pass
    return out
targets={ # var -> (class, side)
 'neu_sugar':('sugar_GRN','right'),'neu_water':('water_GRN','right'),'neu_bitter':('bitter_GRN','right'),
 'neu_ir94e':('Ir94e_GRN','right'),'neu_sugar_left':('sugar_GRN','left'),
 'neu_JON_CE':('JON_CE','unspecified'),'neu_JON_F':('JON_F','unspecified'),'neu_JON_D_m':('JON_D_m','unspecified'),
 'id_mn9':('MN9','see notebook'),'ids_mn9':('MN9','left,right (order as in notebook)'),
 'id_DN1_1':('DN1_1','unspecified'),'id_DN2_l':('DN2_l','left'),'id_aBN1':('aBN1','unspecified'),
 'three_inhibitory':('three_inhibitory_silenced','unspecified'),
}
seen=set()
for nb in ['example.ipynb','figures.ipynb']:
    d=json.load(open(D+nb))
    for ci,c in enumerate(d['cells']):
        if c['cell_type']!='code': continue
        for var,val in parse_assign(''.join(c['source'])).items():
            if var in targets and (var,tuple(val) if isinstance(val,list) else val) not in seen:
                seen.add((var,tuple(val) if isinstance(val,list) else val))
                ids=val if isinstance(val,list) else [val]
                cls,side=targets[var]
                if var=='ids_mn9': 
                    for sd,i in zip(['left','right'],ids): add('MN9',sd,[i],nb,ci)
                else: add(cls,side,ids,nb,ci)
# sez_neurons.pickle
sez=pickle.load(open(D+'sez_neurons.pickle','rb'))
print('sez_neurons.pickle keys and sizes:',{k:len(v) for k,v in sez.items()})
for k,v in sez.items(): add('SEZ_'+k,'unspecified',list(v),'sez_neurons.pickle',-1)
df=pd.DataFrame(rows).rename(columns={'class_':'class'})
# duplicates within same (class,id) across notebooks collapse
df=df.sort_values(['class','side','source_notebook','cell_index']).reset_index(drop=True)
df.to_csv(OUT+'all_ids_long.csv',index=False)
# per-class files (first occurrence of identical set)
# MN9 id in example.ipynb is the same ID as the 'left' one in figures.ipynb: label it left, keep both sources
df.loc[(df['class']=='MN9')&(df['side']=='see notebook'),'side']='left'
df=df.drop_duplicates(['class','side','flywire_id','source_notebook']).reset_index(drop=True)
df.to_csv(OUT+'all_ids_long.csv',index=False)
df[df['class'].str.startswith('SEZ_')].to_csv(OUT+'SEZ_custom_types.csv',index=False)
for (cls,side),g in df[~df['class'].str.startswith('SEZ_')].groupby(['class','side']):
    fn=f"{cls}_{side.replace(',','_').replace(' ','_').replace('(','').replace(')','')}.csv"
    g.drop_duplicates('flywire_id')[['flywire_id','name','class','side','source_notebook','cell_index','in_v630','in_v783']].to_csv(OUT+fn,index=False)
summ=df[~df['class'].str.startswith('SEZ_')].drop_duplicates(['class','side','flywire_id']).groupby(['class','side']).agg(n=('flywire_id','size'),in630=('in_v630','sum'),in783=('in_v783','sum'),nb=('source_notebook','first'),cell=('cell_index','first'))
print(summ.to_string())
# single-ID duplicates between classes?
dup=df.drop_duplicates(['class','flywire_id']).groupby('flywire_id')['class'].apply(list)
print('IDs in >1 class (excluding SEZ):',{k:v for k,v in dup.items() if len(v)>1 and not all(x.startswith('SEZ') for x in v)})

sz=df[df['class'].str.startswith('SEZ_')].drop_duplicates('flywire_id')
print('SEZ pickle: n types',df[df['class'].str.startswith('SEZ_')]['class'].nunique(),'n unique ids',len(sz),'in630',sz.in_v630.sum(),'in783',sz.in_v783.sum())
