import ctypes, os, sys

share_file_name = "dafna.dll" if sys.platform == 'win32' else "libdafna.so"
dafnalib = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib", share_file_name))

def dafna_min_strings_iterator_create(obj):
    fun = dafnalib.dafna_min_strings_iterator_create
    fun.argtypes = [ctypes.c_void_p]
    fun.restype = ctypes.c_void_p
    return fun(obj)

def dafna_min_strings_iterator_next(it):
    fun = dafnalib.dafna_min_strings_iterator_next
    fun.argtypes = [ctypes.c_void_p]
    return fun(it)

def dafna_min_strings_iterator_at_end(it):
    fun = dafnalib.dafna_min_strings_iterator_at_end
    fun.argtypes = [ctypes.c_void_p]
    fun.restype = ctypes.c_bool
    return fun(it)

def dafna_min_strings_iterator_delete(it):
    fun = dafnalib.dafna_min_strings_iterator_delete
    fun.argtypes = [ctypes.c_void_p]
    fun(it)

def dafna_min_strings_iterator_value(it):
    fun = dafnalib.dafna_min_strings_iterator_value
    fun.argtypes = [ctypes.c_void_p]
    fun.restype = ctypes.c_char_p
    return fun(it)


def dafna_generate_visualization_script(obj):
    fun = dafnalib.dafna_generate_visualization_script
    fun.argtypes = [ctypes.c_void_p]
    fun.restype = ctypes.c_char_p
    return fun(obj)


def dafna_delete_automata(obj):
    fun = dafnalib.dafna_delete_automata
    fun.argtypes = [ctypes.c_void_p]
    fun(obj)


def dafna_find_min_automata(obj):
    fun = dafnalib.dafna_find_min_automata
    fun.argtypes = [ctypes.c_void_p]
    fun.restype = ctypes.c_void_p
    return fun(obj)

def dafna_sum_automata(first, second):
    fun = dafnalib.dafna_sum_automata
    fun.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    fun.restype = ctypes.c_void_p
    return fun(first, second)

def dafna_intersect_automata(first, second):
    fun = dafnalib.dafna_intersect_automata
    fun.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    fun.restype = ctypes.c_void_p
    return fun(first, second)

def dafna_create_automata(expr):
    fun = dafnalib.dafna_create_automata
    fun.argtypes = [ctypes.c_char_p]
    fun.restype = ctypes.c_void_p
    return fun(expr)


def dafna_automata_state_count(obj):
    fun = dafnalib.dafna_automata_state_count
    fun.argtypes = [ctypes.c_void_p]
    fun.restype = ctypes.c_int
    return fun(obj)