from setuptools import find_packages, setup
from cmake_build_extension import BuildExtension, CMakeExtension

setup(
    url="broutonlab.com",
    ext_modules=[
        CMakeExtension(name="DafnaCpp",
                       install_prefix="dafna"),
    ],
    cmdclass=dict(build_ext=BuildExtension)
)