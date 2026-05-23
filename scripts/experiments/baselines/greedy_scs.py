"""Жадный алгоритм shortest common SUPERSEQUENCE (Tournament).

Используется как baseline для сравнения с предлагаемым подходом
(SCS как частный случай AND из X*-разложений). Реализует классическую
итеративную схему: на каждом шаге выбирается пара строк с максимальным
LCS, заменяется их кратчайшей надпоследовательностью.
"""

from typing import Iterable, List


def lcs_length(a: str, b: str) -> int:
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai = a[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = dp[i - 1][j] if dp[i - 1][j] >= dp[i][j - 1] else dp[i][j - 1]
    return dp[n][m]


def shortest_supersequence(a: str, b: str) -> str:
    """Кратчайшая надпоследовательность пары через классическое DP."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        ai = a[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = 1 + (dp[i - 1][j] if dp[i - 1][j] <= dp[i][j - 1] else dp[i][j - 1])
    out: List[str] = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] <= dp[i][j - 1]:
            out.append(a[i - 1])
            i -= 1
        else:
            out.append(b[j - 1])
            j -= 1
    while i > 0:
        out.append(a[i - 1])
        i -= 1
    while j > 0:
        out.append(b[j - 1])
        j -= 1
    return "".join(reversed(out))


def greedy_scs(strings: Iterable[str]) -> str:
    """Tournament: пока > 1 строки, объединяем пару с наибольшим LCS."""
    pool = list(strings)
    if not pool:
        return ""
    while len(pool) > 1:
        best_score = -1
        best_i, best_j = 0, 1
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                score = lcs_length(pool[i], pool[j])
                if score > best_score:
                    best_score = score
                    best_i, best_j = i, j
        merged = shortest_supersequence(pool[best_i], pool[best_j])
        pool = [merged] + [pool[k] for k in range(len(pool)) if k not in (best_i, best_j)]
    return pool[0]
