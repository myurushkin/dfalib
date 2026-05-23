#include <sstream>

#include "dafna/dafna.h"
#include "dfalib/dfa.h"
#include "dfalib/dfa_window.h"
#include "regex/regex.h"
#include <string.h>
#include <fstream>
#include <vector>

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
Automata* dafna_intersect_automata_lazy(const Automata* first_automata, const Automata* second_automata) {
    return intersect_lazy(first_automata, second_automata);
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

MinStringsIterator* dafna_min_strings_iterator_create_n_first(const Automata* automata, int n_limit) {
    MinStringsIterator* it = new MinStringsIterator;

    find_all_min_strings(automata, it->values, n_limit);
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

// Helper: write result string into caller buffer; return length or -1.
static int write_result(const std::list<std::string>& res, char* out_buf, int out_buf_len) {
    if (res.empty()) return -1;
    const std::string& s = res.front();
    if (out_buf && out_buf_len > 0) {
        int n = static_cast<int>(s.size());
        if (n >= out_buf_len) n = out_buf_len - 1;
        memcpy(out_buf, s.c_str(), n);
        out_buf[n] = '\0';
        return n;
    }
    return static_cast<int>(s.size());
}

// Alphabet positions (per dfa.cpp:read_from_stream symb2id): a=0, g=1, c=2, t=3.
// All cost_0/cost_1/cost_2/cost_3 parameters MUST be passed in that order.
// GC cost vector: {0, 1, 1, 0}.
int dafna_find_min_string_under_budget(
        const Automata* big,
        int cost_0, int cost_1, int cost_2, int cost_3,
        int budget, int length_cap,
        char* out_buf, int out_buf_len) {
    const int cost[4] = {cost_0, cost_1, cost_2, cost_3};
    std::list<std::string> res;
    find_min_string_under_budget(big, cost, budget, length_cap, res);
    return write_result(res, out_buf, out_buf_len);
}

int dafna_find_min_string_in_window(
        const Automata* big,
        int cost_0, int cost_1, int cost_2, int cost_3,
        int cost_lo, int cost_hi, int length_cap,
        char* out_buf, int out_buf_len) {
    const int cost[4] = {cost_0, cost_1, cost_2, cost_3};
    std::list<std::string> res;
    find_min_string_in_window(big, cost, cost_lo, cost_hi, length_cap, res);
    return write_result(res, out_buf, out_buf_len);
}

int dafna_find_min_string_in_gc_window(
        const Automata* big,
        double alpha, double beta, int length_cap,
        char* out_buf, int out_buf_len) {
    std::list<std::string> res;
    find_min_string_in_gc_window(big, alpha, beta, length_cap, res);
    return write_result(res, out_buf, out_buf_len);
}

struct WindowResult {
    std::vector<std::string> strings;
};

void* dafna_find_all_min_strings_under_budget(
        const Automata* big,
        int cost_0, int cost_1, int cost_2, int cost_3,
        int budget, int length_cap, int n_limit) {
    const int cost[4] = {cost_0, cost_1, cost_2, cost_3};
    std::list<std::string> res;
    find_all_min_strings_under_budget(big, cost, budget, length_cap, n_limit, res);
    WindowResult* wr = new WindowResult;
    wr->strings.assign(res.begin(), res.end());
    return wr;
}

int dafna_window_result_count(void* handle) {
    if (!handle) return 0;
    return static_cast<int>(static_cast<WindowResult*>(handle)->strings.size());
}

const char* dafna_window_result_get(void* handle, int index) {
    if (!handle) return nullptr;
    auto* wr = static_cast<WindowResult*>(handle);
    if (index < 0 || index >= static_cast<int>(wr->strings.size())) return nullptr;
    return wr->strings[index].c_str();
}

void dafna_window_result_delete(void* handle) {
    delete static_cast<WindowResult*>(handle);
}
