#include "dfa.h"

#include <cassert>
#include <queue>

void intesect_automata(const Automata& first_automata, const Automata& second_automata, Automata& new_automata) {
	new_automata.l_value = std::max(first_automata.l_value, second_automata.l_value);
	new_automata.n_value = new_automata.l_value * first_automata.state_count() * second_automata.state_count();

	for (auto first_state : first_automata.terminal_states) {
		for (auto second_state : second_automata.terminal_states) {
			new_automata.terminal_states.insert(first_state * second_automata.terminal_states.size() + second_state);
		}
	}

	for (int i = 0; i < first_automata.state_count(); ++i) {
		for (int j = 0; j < second_automata.state_count(); ++j) {
			for (int k = 0; k < new_automata.l_value; ++k) {
				int s_first = first_automata.get_to_state(i, k);
				int s_second = second_automata.get_to_state(j, k);

				new_automata.set_transition(i * second_automata.state_count() + j, k,
					s_first * second_automata.state_count() + s_second);
			}
		}
	}
}

void build_minimum_equivalent_automata(const Automata& automata, Automata& new_automata) {
    const int states_count = automata.n_value;
    const int alpha_count = automata.l_value;

    std::vector<int> colors(states_count), new_colors(states_count);
    bool contains_non_terminal_states = false;
    for (int i = 0; i < states_count; ++i) {
        colors[i] = automata.is_terminal(i) == true ? 1 : 0;
        if (colors[i] == 0) {
            contains_non_terminal_states = true;
        }
    }

    if (contains_non_terminal_states == false) {
        for (int i = 0; i < states_count; ++i) {
            colors[i] = 0;
        }
    }

    std::vector<int> indexes(states_count), indexes_new(states_count);
    std::vector<int> digest(states_count);
    std::vector<int> relations(states_count * alpha_count);



    int prev_colors_cout = 2;
    for (int iteration = 0; iteration < states_count; ++iteration) {
        for (int symb = 0; symb < alpha_count; ++symb) {
            for (int st = 0; st < states_count; ++st) {
                int to_state = automata.get_to_state(st, symb);
                relations[symb * states_count + st] = colors[automata.get_to_state(st, symb)];
            }
        }

        {
            for (int i = 0; i < states_count; ++i) {
                digest[i] = 0;
            }
            for (int i = 0; i < states_count; ++i) {
                ++digest[colors[i]];
            }

            int indent = 0;
            for (int i = 0; i < states_count; ++i) {
                int prev_indent = indent;
                indent += digest[i];
                digest[i] = prev_indent;
            }

            for (int i = 0; i < states_count; ++i) {
                int color = colors[i];
                indexes[digest[color]++] = i;
            }
        }

        for (int symb = 0; symb < alpha_count; ++symb) {

            for (int i = 0; i < states_count; ++i) {
                digest[i] = 0;
            }
            for (int i = 0; i < states_count; ++i) {
                int color = relations[symb * states_count + i];
                assert(color >= 0 && color < states_count);
                ++digest[color];
            }

            int indent = 0;
            for (int i = 0; i < states_count; ++i) {
                int prev_indent = indent;
                indent += digest[i];
                digest[i] = prev_indent;
            }

            for (int i = 0; i < states_count; ++i) {
                int color = relations[symb * states_count + indexes[i]];
                indexes_new[digest[color]++] = indexes[i];
            }

            for (int i = 0; i < states_count; ++i) {
                indexes[i] = indexes_new[i];
            }
        }

        int current_color = 0;
        for (int ind = 0; ind < states_count; ++ind) {
            bool change_color = false;
            if (ind > 0) {
                change_color = colors[indexes[ind]] != colors[indexes[ind - 1]];
                for (int j = 0; j < alpha_count; ++j) {
                    if (relations[j * states_count + indexes[ind]]
                        != relations[j * states_count + indexes[ind - 1]]) {
                        change_color = true;
                    }
                }
            }

            if (change_color == true) {
                ++current_color;
            }
            new_colors[indexes[ind]] = current_color;
        }

        for (int i = 0; i < states_count; ++i) {
            colors[i] = new_colors[i];
        }

        if (current_color + 1 == prev_colors_cout) {
            break;
        }
        prev_colors_cout = current_color + 1;
    }


    // ----------------------------------------

    if (colors[0] != 0) {
        int col = colors[0];
        for (int i = 0; i < states_count; ++i) {
            if (colors[i] == 0) {
                colors[i] = col;
            } else {
                if (colors[i] == col) {
                    colors[i] = 0;
                }
            }
        }
    }


    int n_value = 0;
    for (int i = 0; i < states_count; ++i) {
        if (n_value < colors[i])
            n_value = colors[i];

        if (automata.is_terminal(i) == true) {
            new_automata.terminal_states.insert(colors[i]);
        }
    }
    ++n_value;

    new_automata.n_value = n_value;
    new_automata.l_value = automata.l_value;
    new_automata.init();
    for (int i = 0; i < automata.n_value; ++i) {
        for (int symb = 0; symb < automata.l_value; ++symb) {
            int from = colors[i];
            int to = colors[automata.get_to_state(i, symb)];
            new_automata.set_transition(from, symb, to);
        }
    }
}

void find_min_automata(const Automata& automata, Automata& new_automata) {

    std::vector<bool> interesting_states(automata.n_value, false);
    std::queue<int> current_nodes;
    current_nodes.push(0);
    while (current_nodes.empty() == false) {
        int node = current_nodes.front();
        current_nodes.pop();

        interesting_states[node] = true;
        for (int i = 0; i < automata.l_value; ++i) {
            int to = automata.get_to_state(node, i);
            if (interesting_states[to] == true)
                continue;
            current_nodes.push(to);
        }
    }

    std::vector<int> new_numeration(automata.n_value);
    int new_n_value = 0;
    for (int i = 0; i < automata.n_value; ++i) {
        if (interesting_states[i] == true) {
            new_numeration[i] = new_n_value++;
            continue;
        }
    }

    Automata reduced_automata;
    reduced_automata.n_value = new_n_value;
    reduced_automata.l_value = automata.l_value;
    reduced_automata.init();
    for (int st = 0; st < automata.n_value; ++st) {
        if (interesting_states[st] == false) {
            continue;
        }

        if (automata.is_terminal(st))
            reduced_automata.terminal_states.insert(new_numeration[st]);

        for (int symb = 0; symb < reduced_automata.l_value; ++symb) {
            reduced_automata.set_transition(new_numeration[st], symb,
                new_numeration[automata.get_to_state(st, symb)]);
        }
    }

    build_minimum_equivalent_automata(reduced_automata, new_automata);
}

bool check_eq(const Automata& automata_first_, const Automata& automata_second_) {
    if (automata_first_.l_value != automata_second_.l_value)
        return false;

    Automata automata_first_reduced, automata_second_reduced;
    find_min_automata(automata_first_, automata_first_reduced);
    find_min_automata(automata_second_, automata_second_reduced);

    if (automata_first_reduced.n_value != automata_second_reduced.n_value
        || automata_first_reduced.l_value != automata_second_reduced.l_value)
        return false;

    std::queue<int> states;
    std::vector<int> states_map(automata_first_reduced.n_value, -1);
    std::vector<int> visited_states(automata_first_reduced.n_value, false);

    states.push(0);
    visited_states[0] = true;
    states_map[0] = 0;

    while (states.empty() == false) {
        int current_state = states.front();
        int current_mapped_state = states_map[current_state];

        states.pop();

        for (int i = 0; i < automata_first_reduced.l_value; ++i) {
            int next_state = automata_first_reduced.get_to_state(current_state, i);
            states_map[next_state] = automata_second_reduced.get_to_state(current_mapped_state, i);

            if (visited_states[next_state])
                continue;
            states.push(next_state);
            visited_states[next_state] = true;
        }
    }

    for (int i = 0; i < automata_first_reduced.n_value; ++i) {
        if (automata_first_reduced.is_terminal(i)
            != automata_second_reduced.is_terminal(states_map[i]))
            return false;
        for (int j = 0; j < automata_first_reduced.l_value; ++j) {
            int to_state = automata_first_reduced.get_to_state(i, j);
            int to_state_mapped = automata_first_reduced.get_to_state(states_map[i], j);
            if (states_map[to_state] != to_state_mapped)
                return false;
        }
    }

    return true;
}
