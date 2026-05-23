#ifndef DFALIB_DFA_WINDOW_H
#define DFALIB_DFA_WINDOW_H

#include <functional>
#include <list>
#include <string>
#include "dfalib/dfa.h"

// LB: shortest string in L(big) with sum_i cost[w_i] <= budget.
// length_cap == -1 means unbounded.
void find_min_string_under_budget(const Automata* big,
                                  const int cost[4],
                                  int budget,
                                  int length_cap,
                                  std::list<std::string>& result);

// LW: shortest string in L(big) with cost_lo <= sum_i cost[w_i] <= cost_hi.
void find_min_string_in_window(const Automata* big,
                               const int cost[4],
                               int cost_lo,
                               int cost_hi,
                               int length_cap,
                               std::list<std::string>& result);

// GC-window: cost = {0,1,1,0} (a,c,g,t), window [ceil(alpha*l), floor(beta*l)]
// applied per BFS layer l.
void find_min_string_in_gc_window(const Automata* big,
                                  double alpha,
                                  double beta,
                                  int length_cap,
                                  std::list<std::string>& result);

// LB+: all min-length strings within budget, up to n_limit.
void find_all_min_strings_under_budget(const Automata* big,
                                       const int cost[4],
                                       int budget,
                                       int length_cap,
                                       int n_limit,
                                       std::list<std::string>& result);

#endif
