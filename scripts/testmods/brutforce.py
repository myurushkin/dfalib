from itertools import *
from modules import parsers
from timeit import default_timer as timer
length = 14

start = timer()

with open('result.txt', 'w') as f:
    for s in product('acgt', repeat=length):
        s = ''.join(s)
        result_tuple = parsers.analyze_string(s, [True, True, True, 1])
        if result_tuple >= (1, 1, 1, 1):
            f.write('{0} {1}\n'.format(s, result_tuple))

    end = timer()
    f.write('total seconds:{0}'.format(end - start))



