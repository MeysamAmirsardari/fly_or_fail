# Probe: dump Brian2 scheduling + generated abstract/target code for the exact model.py equations (tiny network).
import sys, os; sys.path.insert(0, os.path.join(os.environ.get('NJ_EXTERNAL', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'external')), 'Drosophila_brain_model'))
import model as M
from brian2 import *
p = M.default_params
neu = NeuronGroup(3, model=p['eqs'], method='linear', threshold=p['eq_th'], reset=p['eq_rst'],
                  refractory='rfc', name='default_neurons', namespace=p)
neu.v = p['v_0']; neu.g = 0; neu.rfc = p['t_rfc']
syn = Synapses(neu, neu, 'w : volt', on_pre='g += w', delay=p['t_dly'], name='default_synapses')
syn.connect(i=[0], j=[1]); syn.w = 10*p['w_syn']
pois, neu = M.poi(neu, [0], [], p)
mon = SpikeMonitor(neu)
net = Network(neu, syn, mon, *pois)
net.run(0*ms)
print('target:', prefs.codegen.target)
print(net.scheduling_summary())
for obj in net.sorted_objects:
    for co in getattr(obj, '_code_objects', []):
        if co is None: continue
        print('=' * 20, obj.name, co.name, co.template_name)
        print('ABSTRACT:', getattr(obj, 'abstract_code', None))
        src = co.code
        s = str(getattr(src, 'main', src))
        # print only the generated main loop region
        print(s[-3000:])
print('queue delays', syn.pre.queue)
print('syn.delay', syn.delay[:], float(syn.delay[0]/defaultclock.dt))
