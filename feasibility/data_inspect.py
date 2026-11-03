# Data inspection for v783 and v630 Completeness + Connectivity files
import pandas as pd, numpy as np
D='/home/user/external/Drosophila_brain_model/'
sets={'v783':('Completeness_783.csv','Connectivity_783.parquet'),
      'v630':('2023_03_23_completeness_630_final.csv','2023_03_23_connectivity_630_final.parquet')}
for k,(c,p) in sets.items():
    print('='*20,k)
    comp=pd.read_csv(D+c,index_col=0); con=pd.read_parquet(D+p)
    print('completeness file:',c,'shape',comp.shape); print(comp.dtypes.to_string()); print(comp.head(3).to_string())
    print('index name:',comp.index.name,'dtype',comp.index.dtype,'unique',comp.index.is_unique,'monotonic',comp.index.is_monotonic_increasing)
    print('connectivity file:',p,'shape',con.shape); print(con.dtypes.to_string()); print(con.head(3).to_string())
    print('n neurons',len(comp),'n edges',len(con))
    print('columns NaN counts:',con.isna().sum().to_dict())
    s=con['Connectivity_Syn_Count'] if 'Connectivity_Syn_Count' in con else None
    for col in con.columns:
        if 'Count' in col or 'Connectivity' in col:
            pass
    syn=con['Connectivity']
    print('synapse count per edge (Connectivity col): min',syn.min(),'max',syn.max(),'mean',syn.mean(),'median',syn.median())
    print('quantiles',syn.quantile([.01,.1,.25,.5,.75,.9,.99,.999]).to_dict())
    print('value counts of Connectivity (first 12):',syn.value_counts().sort_index().head(12).to_dict())
    print('total synapses',syn.sum())
    ex=con['Excitatory']
    print('Excitatory unique values',ex.unique())
    xc=con['Excitatory x Connectivity']
    print('Exc x Conn: min',xc.min(),'max',xc.max())
    print('check xc == sign*Connectivity:', ((xc.abs()==syn).all()), 'sign(xc)==Excitatory?', (np.sign(xc)==ex).all())
    print('frac inhibitory edges',(xc<0).mean(),'n',(xc<0).sum(),' frac zero',(xc==0).mean())
    print('frac inhibitory synapses',syn[xc<0].sum()/syn.sum())
    # index consistency
    n=len(comp)
    print('Pre idx range',con['Presynaptic_Index'].min(),con['Presynaptic_Index'].max(),'Post',con['Postsynaptic_Index'].min(),con['Postsynaptic_Index'].max(),'n comp',n)
    pre_id=con['Presynaptic_ID'].values; post_id=con['Postsynaptic_ID'].values
    ids=comp.index.values
    print('pre idx -> comp.index matches Presynaptic_ID:',(ids[con['Presynaptic_Index'].values]==pre_id).all())
    print('post idx -> comp.index matches Postsynaptic_ID:',(ids[con['Postsynaptic_Index'].values]==post_id).all())
    print('all pre ids in completeness:',np.isin(pre_id,ids).all(),'post:',np.isin(post_id,ids).all())
    print('duplicate (pre,post) pairs:',con.duplicated(['Presynaptic_Index','Postsynaptic_Index']).sum())
    print('self loops:',(con['Presynaptic_Index']==con['Postsynaptic_Index']).sum())
    print('neurons with any outgoing',con['Presynaptic_Index'].nunique(),'any incoming',con['Postsynaptic_Index'].nunique(),'isolated',n-len(set(con['Presynaptic_Index'])|set(con['Postsynaptic_Index'])))
    # sign consistency per presynaptic neuron (Dale's law as encoded)
    sg=con.groupby('Presynaptic_Index')['Excitatory'].nunique()
    print('presyn neurons with mixed signs:',(sg>1).sum())
    print('Excitatory dtype',ex.dtype)
    # other columns
    print('other columns summary:'); print(con.describe().T.to_string())
    print('completeness other cols:',[c for c in comp.columns])
    print('ids dtype',comp.index.dtype,'min/max',comp.index.min(),comp.index.max())
    print('outdegree per neuron: mean',con.groupby('Presynaptic_Index').size().mean(),'max',con.groupby('Presynaptic_Index').size().max())
    print('mean synapses/edge excit vs inhib',syn[xc>0].mean(),syn[xc<0].mean())
a=pd.read_csv(D+sets['v783'][0],index_col=0).index; b=pd.read_csv(D+sets['v630'][0],index_col=0).index
print('IDs shared v783&v630:',len(a.intersection(b)),'only783',len(a.difference(b)),'only630',len(b.difference(a)))
