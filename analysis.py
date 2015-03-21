
import numpy as n
import json
from pyknot2.spacecurves import Knot
from pyknot2.make.torus import knot as torus_knot

from cache import CachedGaussCode, db



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

def cached_from_gauss_code(gc):
    '''
    Takes a Gauss code as a string, checks if it is in the cache
    database, and returns it if so.
    '''
    db.connect()
    cached = CachedGaussCode.select().where(CachedGaussCode.gauss_code == gc)
    first = cached.first()  # this may be None
    db.close()

    return first


def representation_to_json(rep):
    gc_string = str(rep)
    is_virtual = rep.is_virtual()
    self_linking = rep.self_linking()
    gc_length = len(rep)

    if is_virtual:
        return {'is_virtual': is_virtual,
                'self_linking': self_linking}
    rep.simplify()
    simplified_gc_string = str(rep)
    simplified_gc_length = len(rep)

    from pyknot2.catalogue.database import Knot
    cached = cached_from_gauss_code(simplified_gc_string)
    if cached is not None:
        print('gc was cached!')
        return analysis_from_cache(cached, gc_string, gc_length)

    identification = [
        (knot.identifier,
         identifier_to_latex(knot.identifier)) for knot in rep.identify()]
    identification_perfect = len(rep) < 14
    
    analysis = {'identification': identification,
                'identification_perfect': identification_perfect,
                'gauss_code': gc_string,
                'num_crossings': gc_length,
                'reduced_num_crossings': simplified_gc_length,
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

    cache_from_analysis(analysis)

    return analysis
    
def analysis_from_cache(cache, gauss_code, num_crossings):
    analysis = {'gauss_code': gauss_code,
                'num_crossings': num_crossings}
    analysis['simplified_gauss_code'] = cache.gauss_code
    analysis['reduced_num_crossings'] = cache.num_crossings
    if cache.alexander is not None:
        analysis['alexander'] = cache.alexander
    if cache.determinant is not None:
        analysis['alex_roots'] = (cache.determinant,
                                  cache.alex_imag_3,
                                  cache.alex_imag_4)
    if cache.vassiliev_degree_2 is not None:
        analysis['vassiliev_degree_2'] = cache.vassiliev_degree_2
    if cache.vassiliev_degree_3 is not None:
        analysis['vassiliev_degree_3'] = cache.vassiliev_degree_3
    if cache.identification is not None:
        identification = json.loads(cache.identification)
        analysis['identification'] = identification
    else:
        analysis['identification'] = []

    return analysis
            
def cache_from_analysis(analysis):
    db.connect()
    cache = CachedGaussCode(gauss_code=analysis['simplified_gauss_code'])
    if 'reduced_num_crossings' in analysis:
        cache.num_crossings = analysis['reduced_num_crossings']
    if 'alexander' in analysis:
        cache.alexander = analysis['alexander']
    if 'hyp_vol' in analysis:
        cache.alexander = str(analysis['hyp_vol'])
    if 'alex_roots' in analysis:
        roots = analysis['alex_roots']
        cache.determinant = roots[0]
        cache.alex_imag_3 = roots[1]
        cache.alex_imag_4 = roots[2]
    if 'vassilev_degree_2' in analysis:
        cache.vassiliev_degree_2 = analysis['vassiliev_degree_2']
    if 'vassilev_degree_3' in analysis:
        cache.vassiliev_degree_3 = analysis['vassiliev_degree_3']
    if 'identification' in analysis:
        cache.identification = json.dumps(analysis['identification'])
    cache.save()
    db.close()
            
            

            

def torus_knot_to_json(p, q):
    
    return knot_to_json(Knot(torus_knot(p, q, 300)*10, verbose=False))

def identifier_to_latex(i):
    if '_' in i:
        return ''.join([i.replace('_', '_{'), '}'])
    return i
