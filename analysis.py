
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

    analysis = representation_to_json(k.representation())
    
    return (json.dumps(k.points.tolist()), 2.5*max_extent, analysis)


def gauss_code_to_json(gc):
    from pyknot2.representations.representation import Representation
    print('trying to parse', gc, len(gc))
    try:
        representation = Representation(str(gc))
    except:
        return (True, 'FAIL: Gauss code could not be parsed')

    return (False, representation_to_json(representation))

def representation_to_json(rep):
    gc_string = str(rep)
    is_virtual = rep.is_virtual()
    self_linking = rep.self_linking()

    if is_virtual:
        return {'is_virtual': is_virtual,
                'self_linking': self_linking}
    rep.simplify()
    simplified_gc_string = str(rep)

    identification = rep.identify()
    identification_perfect = len(rep) < 14
    
    analysis = {'identification': identification,
                'identification_perfect': identification_perfect,
                'gauss_code': gc_string,
                'simplified_gauss_code': simplified_gc_string,
                'alex_roots': rep.alexander_at_root((2, 3, 4),
                                                    force_no_simplify=True),
                   # 'hyp_vol': str(k.hyperbolic_volume()),
                'vassiliev_degree_2': rep.vassiliev_degree_2(False),
                }

    if len(rep) < 10:
        analysis['vassiliev_degree_3'] = rep.vassiliev_degree_3(False)

    # try:
    #     gc = k.gauss_code()
    #     if len(gc) < 100:
    #         extra_stuff['alexander'] = str(
    #             k.alexander_polynomial(mode='cypari')).replace('*', '')

    #         print(extra_stuff['alexander'])
    # except ValueError, RuntimeError:
    #     print('ValueError in alexander calculation, only a problem '
    #           'if running in debug mode.')

    print('analysis is', analysis)

    return analysis
    


def torus_knot_to_json(p, q):
    
    return knot_to_json(Knot(torus_knot(p, q, 300)*10, verbose=False))
