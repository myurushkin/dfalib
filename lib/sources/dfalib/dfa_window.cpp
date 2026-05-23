#include "dfalib/dfa_window.h"

#include <algorithm>
#include <climits>
#include <cmath>
#include <queue>
#include <set>
#include <string>
#include <unordered_map>

// Alphabet index -> nucleotide character.
// dfa.cpp read_from_stream uses symb2id = {a:0, g:1, c:2, t:3}.
static const char k_symb[4] = {'a', 'g', 'c', 't'};

struct BfsNode {
    int q;
    int b;
    int len;
};

struct PredInfo {
    int prev_q;
    int prev_b;
    int symb;    // symbol taken to reach (q,b)
    int len;
};

// Encode (q, b) into a single long long key.
static inline long long encode_key(int q, int b, int budget_plus1) {
    return static_cast<long long>(q) * budget_plus1 + b;
}

// Reconstruct a single string from predecessor map back to start state.
static std::string reconstruct(
        const std::unordered_map<long long, PredInfo>& pred,
        int accept_q, int accept_b, int budget_plus1) {
    std::string result;
    int q = accept_q;
    int b = accept_b;
    while (true) {
        long long key = encode_key(q, b, budget_plus1);
        auto it = pred.find(key);
        if (it == pred.end()) break;  // reached start (no predecessor stored)
        const PredInfo& p = it->second;
        result.push_back(k_symb[p.symb]);
        if (p.prev_q == q && p.prev_b == b) break;  // safety
        q = p.prev_q;
        b = p.prev_b;
    }
    // String was built backwards; reverse it.
    std::reverse(result.begin(), result.end());
    return result;
}

// Core BFS over augmented state (q, b).
// accept_fn(q, b, len) -> true if this state is an accepting configuration.
// cost_hi is the hard upper bound on b (states with b > cost_hi are pruned).
// n_limit == 1 -> return first string found; > 1 -> return all min-length strings up to n_limit.
static void bfs_window_core(
        const Automata* big,
        const int cost[4],
        int cost_hi,
        int length_cap,
        std::function<bool(int, int, int)> accept_fn,
        std::list<std::string>& result,
        int n_limit = 1) {

    result.clear();

    const int cap = (length_cap == -1) ? INT_MAX : length_cap;
    const int bp1 = cost_hi + 1;  // budget_plus1 for key encoding

    // pred[encode(q,b)] = predecessor info; start state has no entry.
    std::unordered_map<long long, PredInfo> pred;
    // visited[encode(q,b)] = shortest length to reach this augmented state.
    std::unordered_map<long long, int> visited;

    std::queue<BfsNode> bfs;

    long long start_key = encode_key(0, 0, bp1);
    visited[start_key] = 0;
    bfs.push({0, 0, 0});

    int best_len = INT_MAX;

    // For find_all variant we collect all accepting (q,b) at best_len.
    std::vector<std::pair<int,int>> accept_states;

    while (!bfs.empty()) {
        BfsNode cur = bfs.front();
        bfs.pop();

        if (cur.len > best_len) break;  // BFS is level-ordered; nothing shorter ahead

        if (accept_fn(cur.q, cur.b, cur.len)) {
            if (cur.len < best_len) {
                best_len = cur.len;
                accept_states.clear();
            }
            accept_states.push_back({cur.q, cur.b});
            if (n_limit == 1) break;
            continue;  // do not expand past accepting state for length-shortest semantics
        }

        if (cur.len + 1 > cap || cur.len + 1 > best_len) continue;

        for (int k = 0; k < 4; ++k) {
            int nb = cur.b + cost[k];
            if (nb > cost_hi) continue;

            int nq = big->get_to_state(cur.q, k);
            long long key = encode_key(nq, nb, bp1);

            auto vis_it = visited.find(key);
            if (vis_it != visited.end() && vis_it->second <= cur.len + 1) continue;

            visited[key] = cur.len + 1;
            pred[key] = {cur.q, cur.b, k, cur.len + 1};
            bfs.push({nq, nb, cur.len + 1});
        }
    }

    if (accept_states.empty()) return;

    if (n_limit == 1) {
        result.push_back(reconstruct(pred, accept_states[0].first, accept_states[0].second, bp1));
        return;
    }

    // find_all variant: reconstruct from all accepting states, deduplicate, limit.
    // Re-run BFS backwards from each accept state to collect all min-length paths.
    // For simplicity (plan §4 variant A): one string per accept_state already found.
    // This gives up to |accept_states| strings; apply n_limit.
    for (auto& as : accept_states) {
        result.push_back(reconstruct(pred, as.first, as.second, bp1));
        if (n_limit > 0 && (int)result.size() >= n_limit) break;
    }
}

void find_min_string_under_budget(const Automata* big,
                                  const int cost[4],
                                  int budget,
                                  int length_cap,
                                  std::list<std::string>& result) {
    auto accept = [&](int q, int b, int /*len*/) -> bool {
        return big->is_terminal(q) && b <= budget;
    };
    bfs_window_core(big, cost, budget, length_cap, accept, result, 1);
}

void find_min_string_in_window(const Automata* big,
                               const int cost[4],
                               int cost_lo,
                               int cost_hi,
                               int length_cap,
                               std::list<std::string>& result) {
    auto accept = [&](int q, int b, int /*len*/) -> bool {
        return big->is_terminal(q) && b >= cost_lo && b <= cost_hi;
    };
    bfs_window_core(big, cost, cost_hi, length_cap, accept, result, 1);
}

void find_min_string_in_gc_window(const Automata* big,
                                  double alpha,
                                  double beta,
                                  int length_cap,
                                  std::list<std::string>& result) {
    // GC cost: a=0, g=1, c=1, t=0 (alphabet positions 0..3 -> a,g,c,t per dfa.cpp symb2id).
    static const int gc_cost[4] = {0, 1, 1, 0};
    // cost_hi upper bound: at most all characters are GC.
    const int cap = (length_cap == -1) ? INT_MAX / 2 : length_cap;
    auto accept = [&](int q, int b, int len) -> bool {
        if (!big->is_terminal(q) || len == 0) return false;
        int lo = static_cast<int>(std::ceil(alpha * len));
        int hi = static_cast<int>(std::floor(beta * len));
        return b >= lo && b <= hi;
    };
    bfs_window_core(big, gc_cost, cap, length_cap, accept, result, 1);
}

// ---------------------------------------------------------------------------
// Variant B: exhaustive multi-path reconstruction for find_all_min_strings_under_budget.
//
// Step 1 — forward BFS over augmented states (q, b) to build min_len table.
// Step 2 — backward recursive enumeration from every accepting (q*, b*) at
//           the global minimum length, collecting all distinct paths.
//
// Mirrors the round-2 find_all_min_strings / find_all_min_strings_limited
// pattern in dfa.cpp:681-749 but over augmented (q, b) states.
// ---------------------------------------------------------------------------

// Backward recursive enumeration over the augmented state space.
// min_len[(q, b)] gives the shortest BFS distance from (0,0) to (q,b).
// memo[(q, b)] caches the FULL list of paths from (0,0) to (q,b); n_limit
// truncation is applied by the caller, never inside this function, so cached
// entries are always complete and reusable across multiple call sites.
static const std::list<std::string>& enum_paths_backward(
        const Automata* big,
        const int cost[4],
        const std::unordered_map<long long, int>& min_len,
        std::unordered_map<long long, std::list<std::string>>& memo,
        int bp1,           // budget + 1, for key encoding
        int q, int b) {

    long long cur_key = encode_key(q, b, bp1);

    auto memo_it = memo.find(cur_key);
    if (memo_it != memo.end()) return memo_it->second;

    std::list<std::string>& result = memo[cur_key];  // insert empty entry

    auto it = min_len.find(cur_key);
    if (it == min_len.end()) return result;
    int cur_dist = it->second;

    if (cur_dist == 0) {
        result.push_back("");
        return result;
    }

    int prev_dist = cur_dist - 1;

    for (int k = 0; k < 4; ++k) {
        int pb = b - cost[k];
        if (pb < 0) continue;

        for (int pq = 0; pq < big->state_count(); ++pq) {
            if (big->get_to_state(pq, k) != q) continue;

            long long prev_key = encode_key(pq, pb, bp1);
            auto pit = min_len.find(prev_key);
            if (pit == min_len.end() || pit->second != prev_dist) continue;

            const std::list<std::string>& sub =
                enum_paths_backward(big, cost, min_len, memo, bp1, pq, pb);

            for (const auto& s : sub) {
                result.push_back(s + k_symb[k]);
            }
        }
    }
    return result;
}

void find_all_min_strings_under_budget(const Automata* big,
                                       const int cost[4],
                                       int budget,
                                       int length_cap,
                                       int n_limit,
                                       std::list<std::string>& result) {
    result.clear();
    if (budget < 0) return;

    const int cap = (length_cap == -1) ? INT_MAX : length_cap;
    const int bp1 = budget + 1;

    // Step 1: forward BFS to populate min_len for all reachable (q, b).
    std::unordered_map<long long, int> min_len;
    std::queue<BfsNode> bfs;

    long long start_key = encode_key(0, 0, bp1);
    min_len[start_key] = 0;
    bfs.push({0, 0, 0});

    int best_accept_len = INT_MAX;

    while (!bfs.empty()) {
        BfsNode cur = bfs.front();
        bfs.pop();

        // Track best accepting length to prune the BFS once a whole layer is done.
        if (big->is_terminal(cur.q) && cur.b <= budget) {
            if (cur.len < best_accept_len) best_accept_len = cur.len;
        }

        // Do not expand beyond best_accept_len or length_cap.
        if (cur.len + 1 > cap) continue;
        if (cur.len + 1 > best_accept_len) continue;

        for (int k = 0; k < 4; ++k) {
            int nb = cur.b + cost[k];
            if (nb > budget) continue;

            int nq = big->get_to_state(cur.q, k);
            long long key = encode_key(nq, nb, bp1);

            if (min_len.count(key)) continue;  // already reached via shorter/equal path
            min_len[key] = cur.len + 1;
            bfs.push({nq, nb, cur.len + 1});
        }
    }

    if (best_accept_len == INT_MAX) return;

    // Step 2: collect all accepting (q*, b*) at best_accept_len, then enumerate
    // all backward paths from each. memo is shared across all accepting states so
    // repeated sub-problems are computed only once.
    std::unordered_map<long long, std::list<std::string>> memo;
    std::set<std::string> seen;  // deduplication across multiple accepting states

    for (int q = 0; q < big->state_count(); ++q) {
        if (!big->is_terminal(q)) continue;
        for (int b = 0; b <= budget; ++b) {
            long long key = encode_key(q, b, bp1);
            auto it = min_len.find(key);
            if (it == min_len.end() || it->second != best_accept_len) continue;

            const std::list<std::string>& sub =
                enum_paths_backward(big, cost, min_len, memo, bp1, q, b);

            for (const auto& s : sub) {
                if (seen.insert(s).second) {
                    result.push_back(s);
                    if (n_limit > 0 && (int)result.size() >= n_limit) return;
                }
            }
        }
        if (n_limit > 0 && (int)result.size() >= n_limit) break;
    }
}
