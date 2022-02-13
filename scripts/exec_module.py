import dafna

from dafna.shared import Automata


# import ctypes
# hello = ctypes.cdll.LoadLibrary("C:/projects/dfalib/dfalibproj/out/build/x64-Debug/pymodule/hellomodule.dll")
#
# print(hello)
#
# class Summator:
#     def __init__(self):
#         fun = hello.create_object
#         fun.argtypes = []
#         fun.restype = ctypes.c_void_p
#         self.obj = fun()
#
#
#     def sum(self, first, second):
#         fun = hello.calculate_value
#         fun.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
#         fun.restype = ctypes.c_int
#         return fun(self.obj, first, second)
#
#     def __del__(self):
#         fun = hello.delete_object
#         fun.argtypes = [ctypes.c_void_p]
#         fun.restype = None
#         fun(self.obj)
#
#
# s = Summator()
# print(s.sum(10, 20))
# print(s.sum(10, 201))
# del s

#
# hello.delete_object.argtypes = []
# hello.create_object.restype = ctypes.c_void_p
# hello.delete_object.argtypes = [ctypes.c_void_p]
# #hello.delete_object.restype = ctypes.c_void_p
#
# obj = hello.create_object()
# #print(hello.calculate_value(obj, 1, 2) + 4)
#
# #print(hello.calculate_value(obj, 1, 2) + 11)
# hello.delete_object(obj)
