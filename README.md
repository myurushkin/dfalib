# DAFNA - package

[DAFNA tutorial](https://colab.research.google.com/drive/1JRkKK-3yBIT7gCNQMs1inFMF0euY29qf?usp=sharing) for easy start.

## Installation

Compatible with Windows and Linux.

```
!pip install  git+https://github.com/myurushkin/dfalib
```

## Tests running

```python
python -m unittest discover --verbose
```

## `prototype/` — exact search for minimal strings

`prototype/minstr` finds the shortest string in a language given by a boolean
combination of regular constraints **without building the product automaton**.
A search state carries one tracker per leaf of the formula; the formula is
folded as leaves become permanently satisfied or unsatisfiable; and an
admissible bound defined recursively over it (max for conjunction, min for
disjunction) drives an A\* search. On top of that, a query is decomposed into
the conjuncts of its disjunctive normal form, ordered by bound and pruned
against the best answer found so far.

The result is the minimal length, the number of minimal strings and a layered
graph of all optimal solutions — or a proof that there is none.

```sh
python prototype/run_tests.py           # unit tests
python prototype/crosscheck_dfalib.py   # same minimal-string sets as the C++ pipeline, 14 queries
python prototype/bench_time_memory.py   # time and peak memory, three runs per cell
python prototype/smt_compare.py         # comparison against the cvc5 string solver
python prototype/pareto_front.py        # attainable strength vectors at a fixed length
python prototype/check_monotone.py      # does a level-l pattern imply some level-(l-1) pattern?
```

The package itself needs nothing beyond the standard library; `smt_compare.py`
additionally needs `cvc5`.
