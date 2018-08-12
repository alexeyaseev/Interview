import time
import itertools
from collections import defaultdict

"""
12 august 2018
Number of runs: 100
<0.000041> for <CountSol0> (Dynamic programming (counting only))
<0.012174> for <Sol1> (Generate 28 classes)
<0.151866> for <Sol2> (Six for loops with constraints)
<0.359588> for <Sol3> (Six for loops 0..9)
"""

def CountSol0():
    """
    Dynamic programming (counting only)
    """
    base = [1]*10
    for k in range(2):
        base = [0]*9 + base + [0]*9
        base = [sum(base[i-9:i+1]) for i in range(9,len(base))]
    return sum(val**2 for val in base)

def Sol1():
    """
    Generate 28 classes
    """
    res = []
    groups = defaultdict(list)
    for i,j,k in itertools.product(range(10),repeat=3):
        groups[i + j + k].append(str(i) + str(j) + str(k))
    for _sum in groups:
        res.extend(a + b for a,b in itertools.product(groups[_sum],repeat=2))
    return res

def Sol2():
    """
    Six for loops with constraints
    """
    res = []
    for i in range(10):
        for j in range(10):
            for k in range(10):
                s = i + j + k
                range_h = min(10, s + 1)
                for h in range(range_h):
                    range_l = min(10, s - h + 1)
                    for l in range(range_l):
                        p = s - h - l
                        if p <= 9:
                            res.append(str(i) + str(j) + str(k) + str(h) + str(l) + str(p))
    return res

def Sol3():
    """
    Six for loops 0..9
    """
    res = []
    for i,j,k,l,m,n in itertools.product(range(10),repeat=6):
        if (i + j + k == l + m + n):
            res.append(str(i) + str(j) + str(k) + str(l) + str(m) + str(n))
    return res

def Benchmark(func, name, RUNS = 10):
    start = time.time()
    for k in range(RUNS):
        #print('run number <{}> for function <{}>'.format(k, name))
        res = func()
        if isinstance(res, list): res = len(res)
        if res != 55252:
            return -1
    stop = time.time()
    return (stop - start) / RUNS
    
funcs = []
for key, value in locals().copy().items():
    if callable(value):
        if value.__module__ == __name__:
            if 'Sol' in key:
                funcs.append( (key, value) )

NUM_RUNS = 100
times = []
for key,value in funcs:
    desc = value.__doc__.strip()
    ts = Benchmark(value, key, NUM_RUNS)
    times.append( (ts, key, desc) )

times = ( '<{:2f}> for <{}> ({})'.format(time,name,desc) for time,name,desc in sorted(times))
print("Number of runs: {}".format(NUM_RUNS))
print("\n".join(times))
