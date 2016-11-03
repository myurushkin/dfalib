#include <iostream>
#include <set>
#include <fstream>
#include <queue>
#include <map>
//#include "../dfalib/dfa.h"
//#include "regex++/regex.h"
#include <cassert>
#include <list>
#include <stack>
#include <algorithm>
#include <vector>
#include <cctype>
#include <memory>

#include "../dfalib/dfa.h"
#include "parserequest.h"
//
//void test() {
//    for (int i = 0; i < 1000; i++) {
//        std::cout << "test " << i << std::endl;
//
//        int n_value = 100;
//        int alpha_size = 20;
//
//       
//
//        int terminal_states_count = rand() % 10 + 1;
//        std::set<int> terminal_states;
//        for (int i = 0; i < terminal_states_count; ++i) {
//            terminal_states.insert(rand() % n_value);
//        }
//
//        Automata automata;
//        automata.l_value = alpha_size;
//        automata.n_value = n_value;
//        automata.terminal_states = terminal_states;
//        automata.init();
//
//        for (int symb = 0; symb < alpha_size; ++symb) {
//            for (int j = 0; j < n_value; ++j) {
//                int from = j;
//                int to = rand() % alpha_size;
//                automata.set_transition(from, symb, to);
//            }
//        }
//
//        find_min_states_count(automata);
//    }
//}




//int main() {
//    std::ifstream in("A.in");
//
//    Automata first, second;
//    for (int next = 0; next < 2; ++next) {
//        auto& current_automata = next == 0 ? first : second;
//
//        int k_value;
//        in >> current_automata.n_value >> k_value >> current_automata.l_value;
//
//        current_automata.init();
//        for (int j = 0; j < k_value; ++j) {
//            int term_index;
//            in >> term_index;
//            current_automata.terminal_states.insert(term_index);
//        }
//
//        int from, to;
//        char symb;
//        for (int j = 0; j < current_automata.n_value * current_automata.l_value; ++j) {
//            in >> from >> symb >> to;
//            current_automata.set_transition(from, symb - 'a', to);
//        }
//    }
//
//    std::ofstream out("A.out");
//    out << (check_eq(first, second) && check_eq(second, first) ? "EQUIVALENT" : "NOT EQUIVALENT") << std::endl;
//    return 0;
//}

/* Main program */



std::shared_ptr<Automata> generate_big_automata(std::shared_ptr<GrammarExprTree> root, std::map<std::string, std::shared_ptr<Automata>>& processed_items) {
	if (root->childs.empty()) {
		return processed_items.at(root->name);
	}
	
	std::shared_ptr<Automata> result = find_min_automata(generate_big_automata(root->childs[0], processed_items));
	for (int i = 1; i < processed_items.size(); ++i) {
		auto next = find_min_automata(generate_big_automata(root->childs[i], processed_items));
		if (root->op == '*') {
			result = find_min_automata(intesect_automata(result, next));
			continue;
		}
		if (root->op == '|') {
			result = find_min_automata(sum_automata(result, next));
			continue;
		}
	}
	return result;
}

int main() {
	std::string input = "result =   (I | I4) ( I5 | I)";
	assert(std::find(input.begin(), input.end(), '*') == input.end());

	
	int pos = input.find("=") + 1;
	std::shared_ptr<GrammarExprTree> calculations_graph = parse_request(input.substr(pos));

	std::set<std::string> items;
	std::queue<std::shared_ptr<GrammarExprTree>> nodes;
	nodes.push(calculations_graph);
	while (nodes.empty() == false) {
		auto next = nodes.front();
		nodes.pop();
		for (int i = 0; i < next->childs.size(); ++i) {
			nodes.push(next->childs[i]);
		}
		if (next->childs.empty()) {
			items.insert(next->name);
		}
	}

	std::map<std::string, std::shared_ptr<Automata>> processed_items;
	// read processed items
	
	std::shared_ptr<Automata> result = generate_big_automata(calculations_graph, processed_items);
	



    // test();

    //Automata result;
    //// create_automata("ab", result);

    //RegEx re;

    //std::ofstream f("./temp.txt");
    //re.Compile("(((a)))");
    //re.Dump2Stream(f);
    //return 0;
    //
    

    //create_automata("a", result);
    //create_automata("a+b", result);
    //create_automata("ab", result);
    //create_automata("a(bc)", result);
    //create_automata("a(b+|(c))", result);
    //create_automata("(d(a+b)c*d*ed)", result);
    //std::ifstream in("B.in");

    //int k_value;
    //Automata automata;
    //in >> automata.n_value >> k_value >> automata.l_value;

    //automata.init();
    //for (int j = 0; j < k_value; ++j) {
    //    int term_index;
    //    in >> term_index;
    //    automata.terminal_states.insert(term_index);
    //}

    //int from, to;
    //char symb;
    //for (int j = 0; j < automata.n_value * automata.l_value; ++j) {
    //    in >> from >> symb >> to;
    //    automata.set_transition(from, symb - 'a', to);
    //}


    //std::ofstream out("B.out");
    //Automata new_automata;
    //find_min_automata(automata, new_automata);
    //out << new_automata.n_value;

    return 0;
}
