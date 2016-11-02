#include <iostream>
#include <set>
#include <fstream>

#include "../dfalib/dfa.h"


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
int main() {
    // test();

    std::ifstream in("B.in");

    int k_value;
    Automata automata;
    in >> automata.n_value >> k_value >> automata.l_value;

    automata.init();
    for (int j = 0; j < k_value; ++j) {
        int term_index;
        in >> term_index;
        automata.terminal_states.insert(term_index);
    }

    int from, to;
    char symb;
    for (int j = 0; j < automata.n_value * automata.l_value; ++j) {
        in >> from >> symb >> to;
        automata.set_transition(from, symb - 'a', to);
    }


    std::ofstream out("B.out");
    Automata new_automata;
    find_min_automata(automata, new_automata);
    out << new_automata.n_value;

    return 0;
}
