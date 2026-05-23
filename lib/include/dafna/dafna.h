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
EXPORT Automata* dafna_intersect_automata_lazy(const Automata* first_automata, const Automata* second_automata);
EXPORT Automata* dafna_find_min_automata(const Automata* first_automata);
EXPORT bool dafna_check_eq(const Automata* automata_first_, const Automata* automata_second_);

EXPORT const char* dafna_generate_visualization_script(const Automata* automata);

EXPORT MinStringsIterator* dafna_min_strings_iterator_create(const Automata* automata);
EXPORT MinStringsIterator* dafna_min_strings_iterator_create_n_first(const Automata* automata, int n_limit);
EXPORT void dafna_min_strings_iterator_next(MinStringsIterator* it);
EXPORT bool dafna_min_strings_iterator_at_end(MinStringsIterator* it);
EXPORT void dafna_min_strings_iterator_delete(MinStringsIterator* it);
EXPORT char* dafna_min_strings_iterator_value(MinStringsIterator* it);

EXPORT void dafna_delete_string(char* pointer);

// Window/budget functions.
// cost_a..cost_t: per-symbol costs for alphabet positions a=0,c=1,g=2,t=3.
// Returns string length written to out_buf, or -1 if none found.
// out_buf is caller-allocated; out_buf_len should be >= length_cap+1.
EXPORT int dafna_find_min_string_under_budget(
    const Automata* big,
    int cost_a, int cost_c, int cost_g, int cost_t,
    int budget,
    int length_cap,
    char* out_buf,
    int out_buf_len);

EXPORT int dafna_find_min_string_in_window(
    const Automata* big,
    int cost_a, int cost_c, int cost_g, int cost_t,
    int cost_lo,
    int cost_hi,
    int length_cap,
    char* out_buf,
    int out_buf_len);

EXPORT int dafna_find_min_string_in_gc_window(
    const Automata* big,
    double alpha,
    double beta,
    int length_cap,
    char* out_buf,
    int out_buf_len);

// Returns number of strings written; caller iterates via dafna_window_result_*.
// Result handle must be freed with dafna_window_result_delete.
EXPORT void* dafna_find_all_min_strings_under_budget(
    const Automata* big,
    int cost_a, int cost_c, int cost_g, int cost_t,
    int budget,
    int length_cap,
    int n_limit);

EXPORT int dafna_window_result_count(void* handle);
EXPORT const char* dafna_window_result_get(void* handle, int index);
EXPORT void dafna_window_result_delete(void* handle);

#endif
