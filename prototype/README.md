# minstr: minimal and optimal strings under Boolean combinations of constraints

Pure-Python prototype, no dependencies. The problem: a finite alphabet, a set of
constraints on a string and a Boolean formula over them (intersection, union,
negation, arbitrary nesting). Two questions:

1. find the strings of **minimal length** satisfying the formula, exactly;
2. among feasible strings of a given length, find strings with a high value of
   an arbitrary **black-box score**, approximately, within an evaluation budget.

This is a string-analysis and search-algorithm problem. The alphabet is a
parameter and nothing here is tied to an application domain.

## The two designs being compared

**Eager (`minstr/baseline.py`), the conventional pipeline.** Every constraint is
turned into a regular expression, determinised, minimised; the Boolean formula is
folded pairwise into one explicit product DFA, minimising after each operation;
breadth-first search on the result gives the shortest word.

**Lazy (`minstr/search.py`), the alternative.** The product is never built. A
search state is

    (residual formula, ((leaf index, tracker state), ...), phase)

One step applies the symbol to every live tracker. Acceptance is the Boolean
formula evaluated over the leaves' acceptance bits, so nesting and parentheses
cost nothing. Four things make it work:

- **Trackers instead of tables.** A tracker is any deterministic machine with a
  compact state exposing `step`, `accepts`, `always`, `min_remaining`. A regex
  leaf carries a bitmask of NFA states; `count(sub) >= k` carries a KMP position
  and a counter saturating at `k`; the balanced `x{n} M z{n}` construct carries a
  small set of threads, one per candidate `n`, instead of being unrolled into a
  union over the range.
- **An admissible bound.** Each tracker reports a lower bound on the symbols it
  still needs. The bound for the formula is the maximum over conjuncts and the
  minimum over disjuncts, which is admissible and consistent, so A* with a bucket
  queue keeps optimality without a heap.
- **On-the-fly formula folding.** A leaf that has accepted for ever, or that can
  never accept again, is substituted into the formula as a constant and dropped
  from the state. Tuples shrink while searching, states merge more often, and a
  branch whose formula folds to `false` is cut immediately.
- **A solution graph, not a list.** All optimal-length solutions are returned as
  a layered graph supporting exact counting, enumeration without duplicates, and
  uniform sampling by path counts.

## Measured

`python3 bench.py`, alphabet of four symbols, one core. "Answer" is the minimal
length, identical for both methods on every row (each row cross-checks them).
"Eager peak" is the largest intermediate DFA; the run is abandoned above 300,000
states. "No-fold states" is the lazy search with formula folding switched off.

| family | answer | lazy states | lazy s | no-fold states | eager peak | eager s |
|---|---|---|---|---|---|---|
| lookback n=8 | 9 | 3,544 | 0.06 | 4,212 | 13,122 | 0.11 |
| lookback n=10 | 11 | 34,804 | 0.58 | 42,588 | 118,098 | 1.22 |
| lookback n=12 | 13 | 335,312 | 6.50 | 418,604 | over limit | - |
| lookback n=14 | 15 | 3,182,956 | 129.2 | 4,031,388 | not attempted | - |
| union of 3 pairs | 4 | 33 | 0.001 | 42 | 179 | 0.002 |
| union of 4 pairs | 4 | 41 | 0.001 | 46 | 684 | 0.006 |
| 8 substrings | 14 | 1,268 | 0.055 | 2,905 | 838 | 0.020 |
| balanced n=[1..6] | 6 | 59 | 0.002 | 93 | 24 | 0.004 |
| 5 balanced | 7 | 1,190 | 0.042 | 1,197 | 199 | 0.013 |

Reading the table honestly:

- **Where determinisation is the bottleneck the lazy search wins outright.** The
  `lookback` family is the textbook exponential case, a constraint on a symbol
  some fixed distance from the end. At `n = 12` the eager pipeline is already
  over the state limit while the lazy search answers in seconds, and it keeps
  answering two sizes further.
- **Unions favour the lazy search too**, because a disjunct that is already
  settled disappears from the state instead of multiplying it.
- **Where the final product is small, the eager pipeline is competitive or
  better.** Minimisation after each operation collapses those cases to a few
  dozen states, and a table lookup per symbol beats stepping several trackers.
  This is a real result, not a caveat: the two methods should coexist, with the
  eager one used when a cheap size estimate says the product stays small.
- **Formula folding buys about a factor of two** on the families with many
  independent constraints, and nothing when no leaf ever settles.

## Optimising a black-box score

`minstr/optimize.py` works on the feasible graph of strings of a fixed length,
pruned so every node has a completion. Any walk along its edges is feasible by
construction, so no proposal is ever rejected for violating the constraints.
Three optimisers share one budget of score evaluations:

- `uniform_search`: uniform sampling by path counts, the honest baseline;
- `cross_entropy`: a tabular policy over graph nodes, refit on the elite each
  round, initialised at the uniform-over-strings policy;
- `window_mcmc`: Metropolis, where the move resamples a random window uniformly
  among all feasible fillings with the same boundary states. The proposal is
  symmetric, so the acceptance ratio is the plain Metropolis one.

`python3 demo_optimize.py` on a non-additive score, strings of length 14, three
seeds, mean of the best score found:

| method | @100 | @300 | @1000 | @3000 |
|---|---|---|---|---|
| uniform | 11.83 | 14.00 | 15.00 | 15.50 |
| cross-entropy | 12.67 | 15.17 | 16.00 | 16.17 |
| window-mcmc | 14.83 | 15.50 | 16.17 | 16.67 |

The instance has 7,258,920 feasible strings held in a graph of 608 nodes. Both
learners beat uniform sampling at every checkpoint, and the local chain is ahead
early. These are the numbers any learned policy has to beat before it earns its
training cost.

## Worked examples

`python3 examples.py` prints five queries end to end: the constraints, the
Boolean relation between them, the minimal string, how many minimal strings
exist, and what the eager pipeline reports on the same query.  The fifth adds
the black-box optimisation on two landscapes, a smooth one where uniform
sampling already reaches the ceiling and a rugged one where the learners
separate from it.

## Use

    python3 -m minstr.cli query.txt --stats --count --list 5 --sample 3 --eager
    python3 examples.py
    python3 bench.py
    python3 demo_optimize.py
    python3 run_tests.py

Query format:

    alphabet: abcd
    length: 0..30                 # or "length: <= 30"
    A = .*aa.*                    # regex; <A> refers to an earlier definition
    B = count("cc") >= 3
    C = runs(a, 2) >= 2
    D = balanced(a, ., c, 1, 3)   # the x{n} M z{n} construct
    query: A and (B or not C) and D

## Correctness

`run_tests.py` runs the suite without pytest. The regex engine is checked
against Python's `re` on random patterns; every tracker is checked against a
brute-force definition over all short words; the bounds are checked to be
admissible against brute-force true distances; `always` is checked to be sound;
the lazy search is checked against exhaustive enumeration, and against the eager
pipeline including the exact count of optimal solutions; A* is checked against
uninformed breadth-first search on instances beyond the brute-force horizon.

Two real defects were caught this way while building: a wrong regular-expression
expansion of the `runs` tracker, and a missing length component in the search
state that broke queries with a lower length bound.

## Next step

Reinforcement learning on top of this, in the order the measurements justify:
first a query-level model that predicts whether the exact search will fit the
budget, then a learned node policy trained by expert iteration from the graph,
with the cross-entropy and Metropolis curves above as the bar to clear.
