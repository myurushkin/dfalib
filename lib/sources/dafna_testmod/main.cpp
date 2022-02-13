#include "dafna/dafna.h"
#include <stdio.h>
#include <list>
#include <string>
#include "dfalib/dfa.h"

using namespace std;

int main() {
    auto X = dafna_create_automata("g{1}");

    std::list<string> min_strings;
    find_all_min_strings(X, min_strings);


    return 0;
}
