#ifndef DFA_H
#define DFA_H

#include <vector>

struct Automata {
    int n_value; // state count
    int l_value; // alphabet size

    std::set<int> terminal_states;
    std::vector<int> transitions;

    int terminal_states_count() {
        return terminal_states.size();
    }

    void init() {
        transitions.resize(l_value * n_value);
    }

    void set_transition(int from, int symb, int to) {
        transitions[symb * n_value + from] = to;
    }

    bool is_terminal(int state) const {
        return terminal_states.find(state) != terminal_states.end();
    }

    int get_to_state(int from, int symbol) const {
        return transitions[symbol * n_value + from];
    }
};

void find_min_automata(const Automata& automata, Automata& new_automata);
bool check_eq(const Automata& automata_first_, const Automata& automata_second_);

#endif
