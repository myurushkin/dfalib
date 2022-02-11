import numpy as np
from numpy import trapz
from math import pi
from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count()
import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('\t%r  %2.3f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed


def w(x, y):
    #print(x.shape)
    #print(y.shape)
    return np.exp(-(x**2 + y**2))


def S(x):
    return ((1/(1+ np.exp(-x))) - 0.5)*2

def integral(x, y):
    """ From 12.34, page 632 """
    x_star, y_star = np.meshgrid(x, y)
    print(x_star.shape)
    print(y_star.shape)

    N_X = len(x)
    N_Y = len(y)
    result_1 = np.zeros((N_Y, N_X))
    for jj, j in enumerate(y):
        for ii, i in enumerate(x):
            result_1[jj, ii] = trapz(trapz(w(i - x_star, j - y_star), x), y)

    result_2 = np.zeros((N_Y, N_X))
    for ii, i in enumerate(y):
        for jj, j in enumerate(x):
            result_2[ii, jj] = trapz(trapz(w(j - x_star, i - y_star), x), y)

    result_3 = np.zeros((N_Y, N_X))
    for ii, i in enumerate(y):
        for jj, j in enumerate(x):
            result_3[ii, jj] = trapz(trapz(w(j - x_star, i - y_star), x), y)

    assert (result_1 == result_2).all()


    return np.asarray([[trapz(trapz(w(i - x_star, j - y_star), x), y) for i in x] for j in y])
    #return np.asarray([[trapz(trapz(w(i - x_star, j - y_star) * E, x), y) for i in x] for j in y])

a = np.array([2.,  8.])
np.trapz(a, axis=0)

# Create space and time
x_end = 16
y_end = 10
resolution = 5
x = np.linspace(0, x_end, resolution)
y = np.linspace(0, y_end, resolution)
t_start = 0
t_end = 1000
t_step = 0.5
time_range = np.arange(0,t_end+t_step,t_step)

# Parameters
aEE = 1
aIE = 2
aEI = 1
aII = 1
p = .1
k = 60

# Introduction of bifurcation parameters
aEE = aEE * p * k
aIE = aIE * p
aEI = aEI * p * k
aII = aII * p
b_scale = 0.25

params = {'x_end': x_end, 'y_end': y_end, 'b_EE': 0.06*b_scale, 'b_EI': 0.4*b_scale, 'b_IE': 0.06*b_scale, 'b_II': 0.01*b_scale}

# Initial states
E = (np.random.random((resolution, resolution)) - np.random.random((resolution, resolution)))/1
I = (np.random.random((resolution, resolution)) - np.random.random((resolution, resolution)))/1

# Run simulation here
for t in time_range:
    print(t, 'mean ' + str(round(np.average(E),3)))
    print('\r\tmin: ' + str(round(np.amin(E),3)))
    print('\r\tmax: ' + str(round(np.amax(E),3)))

    print(integral(x, y))
    break


