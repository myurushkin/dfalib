#include <sstream>

#include "dafna/dafna.h"
#include "dfalib/dfa.h"
#include "regex/regex.h"
#include <string.h>
#include <fstream>

struct MinStringsIterator {
    std::list<std::string> values;
    std::list<std::string>::iterator it;
};

Automata* dafna_create_automata(const char* reg_expr) {
    RegEx re;
    re.Compile(reg_expr);

    std::stringstream buffer;
    re.Dump2Stream(buffer);

    return Automata::read_from_stream(buffer);
}

int dafna_automata_state_count(Automata* automata) {
    return automata->state_count();
}

void dafna_delete_automata(Automata* automata) {
    delete automata;
}
Automata* dafna_sum_automata(const Automata* first_automata, const Automata* second_automata) {
    return sum_automata(first_automata, second_automata);
}
Automata* dafna_intersect_automata(const Automata* first_automata, const Automata* second_automata) {
    return intesect_automata(first_automata, second_automata);
}
Automata* dafna_find_min_automata(const Automata* first_automata) {
    return find_min_automata(first_automata);
}
bool dafna_check_eq(const Automata* automata_first_, const Automata* automata_second_) {
    return check_eq(automata_first_, automata_second_);
}

const char* dafna_generate_visualization_script(const Automata* automata) {
    std::ostringstream result;
    generate_automata_visualization_script(automata, result);
    return strdup(result.str().c_str());
}

MinStringsIterator* dafna_min_strings_iterator_create(const Automata* automata) {
    MinStringsIterator* it = new MinStringsIterator;

    find_all_min_strings(automata, it->values);
    it->it = it->values.begin();
    return it;
}

void dafna_min_strings_iterator_next(MinStringsIterator* it) {
    ++it->it;
}

bool dafna_min_strings_iterator_at_end(MinStringsIterator* it) {
    return it->it == it->values.end();
}

void dafna_min_strings_iterator_delete(MinStringsIterator* it) {
    delete it;
}

char* dafna_min_strings_iterator_value(MinStringsIterator* it) {
    auto value = *it->it;
    return strdup(value.c_str());
}

void dafna_delete_string(char* pointer) {
    if (pointer)
        free(pointer);
}
