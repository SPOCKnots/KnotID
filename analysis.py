
import numpy as n
import json
from pyknot2.spacecurves import Knot
from pyknot2.make.torus import knot as torus_knot



def text_to_json(text):

    points = []
    for line in text.split('\n'):
        values = line.split(' ')
        if len(values) == 1 and len(values[0]) == 0:
            continue
        if len(values) != 3:
            raise ValueError('Invalid text passed.')
        points.append([float(v) for v in values])

    k = Knot(points, verbose=False)
    return knot_to_json(k)
        

def knot_to_json(k):
    k.rotate(n.array([0.001, 0.002, 0.0015]))
    k.zero_centroid()
    max_extent = n.max(n.max(n.abs(k.points), axis=0))
    gc_string = str(k.gauss_code())
    identification = k.identify()
        
    extra_stuff = {'identification': identification,
                   'gauss_code': gc_string,
                   'alex_roots': k.alexander_at_root((2, 3, 4)),
                   # 'hyp_vol': str(k.hyperbolic_volume()),
                   'vassiliev_degree_2': k.vassiliev_degree_2()}

    # try:
    #     gc = k.gauss_code()
    #     if len(gc) < 100:
    #         extra_stuff['alexander'] = str(
    #             k.alexander_polynomial(mode='cypari')).replace('*', '')

    #         print(extra_stuff['alexander'])
    # except ValueError, RuntimeError:
    #     print('ValueError in alexander calculation, only a problem '
    #           'if running in debug mode.')
    
    
    return (json.dumps(k.points.tolist()), 2.5*max_extent, extra_stuff)

def gauss_code_to_json(gc):
    from pyknot2.invariants import alexander
    from pyknot2.catalogue.identify import from_invariants
    from pyknot2.catalogue.database import Knot as DBKnot


    alex_imag_2 = int(n.round(n.abs(
        alexander(gc, n.exp(2 * n.pi * 1.j / 2.)))))
    alex_imag_3 = int(n.round(n.abs(
        alexander(gc, n.exp(2 * n.pi * 1.j / 3.)))))
    alex_imag_4 = int(n.round(n.abs(
        alexander(gc, n.exp(2 * n.pi * 1.j / 4.)))))

    identify_kwargs = {'alex_imag_2': alex_imag_2,
                       'alex_imag_3': alex_imag_3,
                       'alex_imag_4': alex_imag_4}
    num_crossings = len(gc) 
    if num_crossings < 16:
        identify_kwargs['other'] = (
            DBKnot.min_crossings <= num_crossings, )

    identification = from_invariants(**identify_kwargs)

    analysis = {'alex_roots': (alex_imag_2, alex_imag_3,
                               alex_imag_4),
                'identification': identification}

    return analysis


def torus_knot_to_json(p, q):
    
    return knot_to_json(Knot(torus_knot(p, q, 300)*10, verbose=False))
