#ifndef DAFNA_LIB_H
#define DAFNA_LIB_H

#ifdef __linux__
    #define EXPORT extern "C"
#elif _WIN32
    #define EXPORT extern "C" __declspec(dllexport)
#else

#endif

class Automata;
struct MinStringsIterator;

EXPORT Automata* dafna_create_automata(const char* reg_expr);
EXPORT int dafna_automata_state_count(Automata* automata);
EXPORT void dafna_delete_automata(Automata* automata);

EXPORT Automata* dafna_sum_automata(const Automata* first_automata, const Automata* second_automata);
EXPORT Automata* dafna_intersect_automata(const Automata* first_automata, const Automata* second_automata);
EXPORT Automata* dafna_find_min_automata(const Automata* first_automata);
EXPORT bool dafna_check_eq(const Automata* automata_first_, const Automata* automata_second_);

EXPORT const char* dafna_generate_visualization_script(const Automata* automata);

EXPORT MinStringsIterator* dafna_min_strings_iterator_create(const Automata* automata);
EXPORT void dafna_min_strings_iterator_next(MinStringsIterator* it);
EXPORT bool dafna_min_strings_iterator_at_end(MinStringsIterator* it);
EXPORT void dafna_min_strings_iterator_delete(MinStringsIterator* it);
EXPORT char* dafna_min_strings_iterator_value(MinStringsIterator* it);

EXPORT void dafna_delete_string(char* pointer);


#endif
