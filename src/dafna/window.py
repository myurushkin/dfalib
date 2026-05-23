import ctypes
from typing import Optional
from dafna.internal import dafnalib


def _buf(size=512):
    return ctypes.create_string_buffer(size)


def find_min_string_under_budget(big, cost, budget: int, length_cap: int = 256) -> Optional[str]:
    fun = dafnalib.dafna_find_min_string_under_budget
    fun.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int,
        ctypes.c_char_p, ctypes.c_int,
    ]
    fun.restype = ctypes.c_int
    buf = _buf()
    n = fun(big.obj, cost[0], cost[1], cost[2], cost[3], budget, length_cap, buf, len(buf))
    return buf.value.decode('utf-8') if n >= 0 else None


def find_min_string_in_window(big, cost, cost_lo: int, cost_hi: int, length_cap: int = 256) -> Optional[str]:
    fun = dafnalib.dafna_find_min_string_in_window
    fun.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_char_p, ctypes.c_int,
    ]
    fun.restype = ctypes.c_int
    buf = _buf()
    n = fun(big.obj, cost[0], cost[1], cost[2], cost[3], cost_lo, cost_hi, length_cap, buf, len(buf))
    return buf.value.decode('utf-8') if n >= 0 else None


def find_min_string_in_gc_window(big, alpha: float, beta: float, length_cap: int = 256) -> Optional[str]:
    fun = dafnalib.dafna_find_min_string_in_gc_window
    fun.argtypes = [
        ctypes.c_void_p,
        ctypes.c_double, ctypes.c_double, ctypes.c_int,
        ctypes.c_char_p, ctypes.c_int,
    ]
    fun.restype = ctypes.c_int
    buf = _buf()
    n = fun(big.obj, alpha, beta, length_cap, buf, len(buf))
    return buf.value.decode('utf-8') if n >= 0 else None


def find_all_min_strings_under_budget(big, cost, budget: int, length_cap: int = 256, n_limit: int = 100):
    fun_find = dafnalib.dafna_find_all_min_strings_under_budget
    fun_find.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ]
    fun_find.restype = ctypes.c_void_p

    fun_count = dafnalib.dafna_window_result_count
    fun_count.argtypes = [ctypes.c_void_p]
    fun_count.restype = ctypes.c_int

    fun_get = dafnalib.dafna_window_result_get
    fun_get.argtypes = [ctypes.c_void_p, ctypes.c_int]
    fun_get.restype = ctypes.c_char_p

    fun_del = dafnalib.dafna_window_result_delete
    fun_del.argtypes = [ctypes.c_void_p]

    handle = fun_find(big.obj, cost[0], cost[1], cost[2], cost[3], budget, length_cap, n_limit)
    results = []
    if handle:
        count = fun_count(handle)
        for i in range(count):
            s = fun_get(handle, i)
            if s is not None:
                results.append(s.decode('utf-8'))
        fun_del(handle)
    return results
