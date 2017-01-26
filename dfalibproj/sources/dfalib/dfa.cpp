#include "dfalib/dfa.h"

#include <cassert>
#include <queue>
#include <stack>
#include <list>
#include <algorithm>

std::shared_ptr<Automata> Automata::read_from_stream(std::ifstream& in)
{
    int teminate_state_count;

    std::shared_ptr<Automata> automata(new Automata());
    in >> automata->n_value >> teminate_state_count;
    automata->n_value;
    automata->l_value = 4;

    automata->init();
    for (int j = 0; j < teminate_state_count; ++j) {
        int term_index;
        in >> term_index;
        automata->terminal_states.insert(term_index);
    }

    int from, to;
    char symb;

    int transition_count = 4 * automata->n_value;
    for (int j = 0; j < transition_count; ++j) {
        in >> from >> symb >> to;
        automata->set_transition(from, symb - 'a', to);
    }

    return automata;
}
void Automata::dump_to_stream(std::ofstream& out)
{
    out << this->n_value << " " << this->terminal_states_count() << std::endl;
    for (auto state : this->terminal_states) {
        out << state << " ";
    }
    out << std::endl;

    for (int i = 0; i < this->transitions.size(); ++i)
    {
        int from = i / 4;
        int symb = i % 4;
        out << from << " " << char(symb + 'a') << " " << this->transitions[i] << std::endl;
    }
}

// https://github.com/davinash/regex/tree/master/src

struct Token {
    enum Type {
        Terminal,
        Nonterminal,
        Operation,
        ScopeOpen,
        ScopeClose
    };
};

struct GraphToken {
    struct Edge {
        int from, to;
        char symbol;
    };

    GraphToken() {
    }

    GraphToken(char symb) {
        from = to = 0;
        
    }

    int from, to;
    std::list<Edge> edges;
    int node_count() {
        int max_index = -1;
        assert(edges.empty() == false);
        for (auto& edge : edges) {
            max_index = std::max(max_index, std::max(edge.from, edge.to));
        }
        return max_index + 1;
    }
};

GraphToken mult_graphtokens(const GraphToken& first, const GraphToken& second) {

    return GraphToken();
}

GraphToken or_graphtokens(const GraphToken& first, const GraphToken& second) {
    return GraphToken();
}

GraphToken inc_graphtoken(const GraphToken& first) {
    return GraphToken();
}

void private_create_automata(std::list<char>& input, std::list<char>::iterator& it,
    std::stack<GraphToken>& tokens, std::stack<char>& control) {

    char control_symbols[] = "+|*()";
    int control_symbols_count = sizeof(control_symbols) / sizeof(char);
    while (it != input.end()) {
        char symb = *it++;

        if (std::find(control_symbols, control_symbols + control_symbols_count, symb)
            == control_symbols + control_symbols_count) {
            tokens.push(GraphToken(symb));
            continue;
        }
        

        if (symb == '(') {
            control.push(symb);
            private_create_automata(input, it, tokens, control);
        }
        if (symb == ')'/* || it == input.end()*/) {
            while (/*control.empty() == false &&*/ control.top() != '(') {
                char op = control.top();
                control.pop();
                if (op != '|') {
                    throw std::runtime_error("smth is wrong");
                }

                GraphToken second_token = tokens.top();
                tokens.pop();
                GraphToken first_token = tokens.top();
                tokens.pop();
                tokens.push(or_graphtokens(first_token, second_token));
            }
            
            assert(control.top() == '(');
            control.pop();
            return;
        }

        if (symb == '|') {
            control.push(symb);
            continue;
        }

        if (symb == '+') {
            GraphToken token = tokens.top();
            tokens.pop();
            tokens.push(inc_graphtoken(token));
            continue;
        }

        if (symb == '*') {
            if (*it == '(') {
                control.push('(');
                private_create_automata(input, ++it, tokens, control);
            } else {
                char symb = *it++;
                tokens.push(GraphToken(symb));
            }

            GraphToken second_token = tokens.top();
            tokens.pop();
            GraphToken first_token = tokens.top();
            tokens.pop();
            tokens.push(mult_graphtokens(first_token, second_token));
            continue;
        }
    }
}

void create_automata(std::string rexpr, Automata& new_automata) {
    std::stack<GraphToken> tokens;
    std::stack<char> control;

    std::list<char> input;
    char control_symbols[] = "+|*()";
    int control_symbols_count = sizeof(control_symbols) / sizeof(char);

    bool prev_symb_ischar = false;
    for (int i = 0; i < rexpr.size(); ++i) {
        if (rexpr[i] == ' ') {
            continue;
        }
        if (rexpr[i] == '+') {
            input.push_back(rexpr[i]);
            continue;
        }

        bool current_symb_isletter = std::find(control_symbols,
            control_symbols + control_symbols_count, rexpr[i]) == control_symbols + control_symbols_count;
        if (prev_symb_ischar == true && (current_symb_isletter == true || rexpr[i] == '(')) {
            input.push_back('*');
        }
        input.push_back(rexpr[i]);
        prev_symb_ischar = current_symb_isletter || rexpr[i] == ')';
    }

    auto it = input.begin();
    private_create_automata(input, it, tokens, control);
    assert(control.size() == 0 && tokens.size() == 1);
}

void sum_automata(const Automata& first_automata, const Automata& second_automata, Automata& new_automata) {
    new_automata.l_value = std::max(first_automata.l_value, second_automata.l_value);
    new_automata.n_value = first_automata.state_count() * second_automata.state_count();
    new_automata.init();

    for (auto first_state : first_automata.terminal_states) {
        for (int second_state = 0; second_state < second_automata.state_count(); ++second_state) {
            new_automata.terminal_states.insert(first_state * second_automata.state_count() + second_state);
        }
    }

    for (auto second_state : second_automata.terminal_states) {
        for (int first_state = 0; first_state < first_automata.state_count(); ++first_state) {
            new_automata.terminal_states.insert(first_state * second_automata.state_count() + second_state);
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

void intesect_automata(const Automata& first_automata, const Automata& second_automata, Automata& new_automata) {
	new_automata.l_value = std::max(first_automata.l_value, second_automata.l_value);
    new_automata.n_value = first_automata.state_count() * second_automata.state_count();
    new_automata.init();

	for (auto first_state : first_automata.terminal_states) {
		for (auto second_state : second_automata.terminal_states) {
            new_automata.terminal_states.insert(first_state * second_automata.state_count() + second_state);
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
    interesting_states[0] = true;
    while (current_nodes.empty() == false) {
        int node = current_nodes.front();
        current_nodes.pop();

        for (int i = 0; i < automata.l_value; ++i) {
            int to = automata.get_to_state(node, i);
            if (interesting_states[to] == true)
                continue;
            current_nodes.push(to);
            interesting_states[to] = true;
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



std::shared_ptr<Automata> sum_automata(const std::shared_ptr<Automata>& first_automata, std::shared_ptr<Automata>& second_automata)
{
    Automata* result = new Automata();
    sum_automata(*first_automata.get(), *second_automata.get(), *result);
    return std::make_shared<Automata>(*result);
}
std::shared_ptr<Automata> intesect_automata(const std::shared_ptr<Automata>& first_automata, std::shared_ptr<Automata>& second_automata)
{
	Automata* result = new Automata();
	intesect_automata(*first_automata.get(), *second_automata.get(), *result);
    return std::make_shared<Automata>(*result);
}
std::shared_ptr<Automata> find_min_automata(const std::shared_ptr<Automata>& automata)
{
	Automata* result = new Automata();
	find_min_automata(*automata.get(), *result);
    return std::make_shared<Automata>(*result);
}

void generate_automata_visualization_script(const std::shared_ptr<Automata>& automata, std::string filepath)
{
	std::ofstream file(filepath);
	file << "digraph finite_state_machine{\n";
	file << "    rankdir = LR;\n";
	file << "    size = \"20,20\"\n";
	file << "    node[shape = doublecircle]; S;\n";
	file << "    node[shape = point]; qi\n";
	file << "    node[shape = circle];\n";
	file << "    qi->S;\n";

	for (int i = 0; i < automata->state_count(); ++i)
	{
		for (int symb = 0; symb < 4; ++symb)
		{
			int j = automata->get_to_state(i, symb);

			file << "    ";
			if (i == 0)
				file << "S";
			else
				file << "q" << i;

			file << "->";

			if (j == 0)
				file << "S";
			else
				file << "q" << j;

			file << " [ label = \"" << (char)(symb + 'a') << "\" ];\n";
		}
	}
	

	file << "}";
}