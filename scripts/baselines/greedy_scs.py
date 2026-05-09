"""Deterministic greedy SCS via majority-merge.

For each pair (i, j), compute max overlap = longest suffix of strings[i] that is a prefix of strings[j].
Repeatedly merge the pair with the largest overlap (tie-break: lexicographic on the merged result, then on pair index)
until one string remains. O(n^2 * L) per round, n rounds.
"""

from typing import List


def _overlap(a: str, b: str) -> int:
    """Largest k such that a[-k:] == b[:k] and 0 <= k <= min(len(a), len(b))."""
    max_k = min(len(a), len(b))
    for k in range(max_k, 0, -1):
        if a.endswith(b[:k]):
            return k
    return 0


def greedy_scs(strings: List[str]) -> str:
    """Return a (heuristic) shortest common superstring of `strings`.

    Drops strings that are substrings of others first, then iteratively merges
    the pair with the maximum overlap. Deterministic tie-breaking by (merged-string,
    i, j) lexicographic order.
    """
    if not strings:
        return ""
    # remove substrings to avoid trivial dominators
    pool = list(dict.fromkeys(strings))  # de-duplicate, preserve order
    pool = [s for s in pool if not any(s != t and s in t for t in pool)]
    while len(pool) > 1:
        best_key = None
        best_merged = None
        best_i = None
        best_j = None
        for i, a in enumerate(pool):
            for j, b in enumerate(pool):
                if i == j:
                    continue
                k = _overlap(a, b)
                merged = a + b[k:]
                key = (-k, merged, i, j)
                if best_key is None or key < best_key:
                    best_key = key
                    best_merged = merged
                    best_i = i
                    best_j = j
        # remove the higher index first to keep the lower-index removal valid
        i, j = best_i, best_j
        hi, lo = (i, j) if i > j else (j, i)
        pool.pop(hi)
        pool.pop(lo)
        pool.append(best_merged)
    return pool[0]


if __name__ == "__main__":
    # Smoke test
    result = greedy_scs(["acg", "cgt", "gta"])
    print(result, len(result))
