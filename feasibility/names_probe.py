# Show how Brian2 auto-names evolve when the unmodified model.poi() is called repeatedly in ONE process (toy NeuronGroup, no simulation, no compilation).
import gc, copy
import simlib as S
from brian2 import NeuronGroup, Hz
p = copy.deepcopy(S.M.default_params); p['r_poi'] = 77 * Hz
for k in range(4):
    neu = NeuronGroup(100, model=p['eqs'], method='linear', threshold=p['eq_th'], reset=p['eq_rst'], refractory='rfc', name='default_neurons', namespace=p)
    pois, neu = S.M.poi(neu, list(range(21)), [], p)
    bn = [n for n in pois[0].variables if 'binomial' in n]
    print(f'trial {k}: PoissonInput[0].name={pois[0].name!r}  binomial function in PoissonInput[0]={bn}  PoissonInput[20] binomial={[n for n in pois[20].variables if "binomial" in n]}  NeuronGroup.name={neu.name!r}')
    del neu, pois; gc.collect()
