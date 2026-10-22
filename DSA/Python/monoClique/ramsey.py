"""
Monochromatic clique problem / two-colour Ramsey numbers R(s, t).

Colour every edge of the complete graph K_N red or blue.
R(s, t) is the smallest N such that EVERY colouring contains a red K_s
or a blue K_t.

For each N = 1, 2, 3, ... we search systematically:
  * if a colouring with no red K_s and no blue K_t exists, it is a
    COUNTEREXAMPLE, so R(s, t) > N, and we store it;
  * if the exhaustive search finds none, every colouring of K_N is forced
    to contain the clique, so R(s, t) = N.

Search = backtracking over the edges (0,1), (0,2), (1,2), (0,3), ...
(vertex by vertex). Pruning:
  1. Clique check: when edge (i, j) gets colour c, we only need to look for a
     c-clique that contains both i and j, i.e. a (k-2)-clique inside
     common_c(i) & common_c(j). Done with bitmasks.
  2. Degree bound (the classic proof R(s,t) <= R(s-1,t) + R(s,t-1)):
     a vertex can have at most R(s-1,t)-1 red neighbours and at most
     R(s,t-1)-1 blue neighbours in any counterexample.
  3. Colour symmetry: when s == t, swapping red/blue maps counterexamples to
     counterexamples, so edge (0,1) can be fixed red.
For larger N a circulant search (colour depends only on |i-j| mod N) is tried
first; it is tiny (2^(N/2) cases) and finds the famous constructions such as
the Paley graph on 17 vertices for R(4,4).

Usage:
  python ramsey.py 3 3                 # find R(3,3) with counterexamples
  python ramsey.py 3 3 --show-all      # also print the counterexample for every N
  python ramsey.py 3 4 --count         # also count all labelled counterexamples
  python ramsey.py --sweep 5           # all (s,t) with s+t=5: (1,4) .. (4,1)
  python ramsey.py 4 4 --budget 2e6    # node budget per exhaustive search
  python ramsey.py 3 3 --json out.json # save everything for the visualizer
"""

import argparse
import json
import sys
import time

RED, BLUE = 0, 1

# Literature values / bounds, only used for display and sanity checks.
KNOWN = {
    (3, 3): 6, (3, 4): 9, (3, 5): 14, (3, 6): 18, (3, 7): 23, (3, 8): 28,
    (3, 9): 36, (4, 4): 18, (4, 5): 25,
}


KNOWN_RANGE = {(3, 10): (40, 41), (4, 6): (36, 40), (5, 5): (43, 46)}


def known_text(s, t):
    v = known_value(s, t)
    if v is not None:
        return str(v)
    r = KNOWN_RANGE.get((min(s, t), max(s, t)))
    return f"{r[0]}-{r[1]}" if r else "not in table"


def known_value(s, t):
    s, t = min(s, t), max(s, t)
    if s == 1:
        return 1
    if s == 2:
        return t
    return KNOWN.get((s, t))



def has_clique(cand, size, adj):
    """True if the vertex set `cand` (bitmask) contains a clique of `size`
    in the graph given by adjacency bitmasks `adj`."""
    if size == 0:
        return True
    if bin(cand).count("1") < size:
        return False
    while cand:
        v = (cand & -cand).bit_length() - 1
        cand &= cand - 1                      # drop v, keep higher vertices
        if has_clique(cand & adj[v], size - 1, adj):
            return True
    return False


def find_clique(cand, size, adj, picked=()):
    """Like has_clique but returns the clique vertices."""
    if size == 0:
        return list(picked)
    if bin(cand).count("1") < size:
        return None
    while cand:
        v = (cand & -cand).bit_length() - 1
        cand &= cand - 1
        res = find_clique(cand & adj[v], size - 1, adj, picked + (v,))
        if res:
            return res
    return None


def matrix_to_adj(mat):
    n = len(mat)
    red = [0] * n
    blue = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j:
                if mat[i][j] == RED:
                    red[i] |= 1 << j
                else:
                    blue[i] |= 1 << j
    return red, blue


def mono_clique(mat, s, t):
    """Return ('R', clique) / ('B', clique) if the colouring has one, else None.
    Used to verify counterexamples independently of the search."""
    n = len(mat)
    if n == 0:
        return None
    red, blue = matrix_to_adj(mat)
    full = (1 << n) - 1
    c = find_clique(full, s, red)
    if c:
        return ("R", c)
    c = find_clique(full, t, blue)
    if c:
        return ("B", c)
    return None


# ----------------------------------------------------------------------------
# Degree bounds from smaller Ramsey numbers (rigorous, never from the table)
# ----------------------------------------------------------------------------

def upper_bound(s, t):
    """Proven upper bound on R(s,t) via R(s,t) <= R(s-1,t) + R(s,t-1),
    tightened by results this program has already proven exactly."""
    if s == 1 or t == 1:
        return 1
    if s == 2:
        return t
    if t == 2:
        return s
    if (s, t) in PROVEN:
        return PROVEN[(s, t)]
    a, b = upper_bound(s - 1, t), upper_bound(s, t - 1)
    exact = is_exact(s - 1, t) and is_exact(s, t - 1)
    # Greenwood-Gleason: if both are exact and even, the sum is not reached
    if exact and a % 2 == 0 and b % 2 == 0:
        return a + b - 1
    return a + b


def is_exact(s, t):
    return min(s, t) <= 2 or (s, t) in PROVEN


PROVEN = {}   # (s,t) -> exact value proven by exhaustive search in this run


# ----------------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------------

class Budget(Exception):
    pass


def search(n, s, t, find_all=False, budget=None, on_solution=None):
    """Exhaustive backtracking for colourings of K_n with no red K_s and no
    blue K_t.  Returns (first_solution_matrix_or_None, stats)."""
    stats = {"nodes": 0, "pruned_clique": 0, "pruned_degree": 0,
             "solutions": 0, "complete": True}
    if n == 0:
        stats["solutions"] = 1
        return [], stats
    if s == 1 or t == 1:            # a single vertex is already a K_1
        return None, stats

    edges = [(i, j) for j in range(1, n) for i in range(j)]
    maxdeg = (upper_bound(s - 1, t) - 1, upper_bound(s, t - 1) - 1)
    adj = ([0] * n, [0] * n)
    deg = ([0] * n, [0] * n)
    colour = {}
    need = (s - 2, t - 2)
    first = [None]
    m = len(edges)
    # with s == t, edge (0,1) red is w.l.o.g.; only valid when counting
    # up to colour swap, so disable it in find_all mode
    sym = (s == t) and not find_all

    def snapshot():
        mat = [[-1] * n for _ in range(n)]
        for (i, j), c in colour.items():
            mat[i][j] = mat[j][i] = c
        return mat

    def rec(k):
        if k == m:
            stats["solutions"] += 1
            if first[0] is None:
                first[0] = snapshot()
            if on_solution:
                on_solution(snapshot())
            return not find_all       # True = stop
        i, j = edges[k]
        for c in (RED, BLUE):
            if sym and k == 0 and c == BLUE:
                continue
            stats["nodes"] += 1
            if budget is not None and stats["nodes"] > budget:
                raise Budget
            if deg[c][i] >= maxdeg[c] or deg[c][j] >= maxdeg[c]:
                stats["pruned_degree"] += 1
                continue
            a = adj[c]
            if has_clique(a[i] & a[j], need[c], a):
                stats["pruned_clique"] += 1
                continue
            a[i] |= 1 << j
            a[j] |= 1 << i
            deg[c][i] += 1
            deg[c][j] += 1
            colour[(i, j)] = c
            if rec(k + 1):
                return True
            del colour[(i, j)]
            a[i] &= ~(1 << j)
            a[j] &= ~(1 << i)
            deg[c][i] -= 1
            deg[c][j] -= 1
        return False

    sys.setrecursionlimit(max(10000, m * 4))
    try:
        rec(0)
    except Budget:
        stats["complete"] = False
    return first[0], stats


def circulant_search(n, s, t):
    """Colour edge (i,j) by the class of d = min(|i-j|, n-|i-j|).
    Tries all 2^(n//2) distance sets systematically."""
    if n < 2 or n // 2 > 15:          # 2^15 distance sets is the limit here
        return None
    dists = n // 2
    for mask in range(1 << dists):
        mat = [[-1] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = min(abs(i - j), n - abs(i - j))
                    mat[i][j] = RED if (mask >> (d - 1)) & 1 else BLUE
        if mono_clique(mat, s, t) is None:
            return mat
    return None


def ramsey(s, t, budget=None, count=False, verbose=True, show_all=False):
    """Increase N until no counterexample exists.  Returns a result dict.

    For each N, in order:
      1. N >= U (the recurrence upper bound) -> forced; still run the
         exhaustive search when it fits in the budget, to show it.
      2. circulant construction (fast, systematic)
      3. exhaustive backtracking (finds one, or proves none exist)
      4. if the budget runs out: restrict a larger counterexample (any
         induced sub-colouring of a counterexample is a counterexample)
    """
    U = upper_bound(s, t)
    out = {"s": s, "t": t, "levels": [], "R": None, "status": "unknown",
           "known": known_value(s, t), "upper_bound": U}

    # largest circulant counterexample below U, used for step 4
    big = None
    for n in range(min(U - 1, 31), 4, -1):
        big = circulant_search(n, s, t)
        if big is not None:
            break

    n = 0
    while True:
        t0 = time.perf_counter()
        sol, stats, method = None, None, "backtracking"
        if 5 <= n < U:
            sol = circulant_search(n, s, t)
            if sol is not None:
                method = "circulant"
        if sol is None:
            sol, stats = search(n, s, t, budget=budget)
        if sol is None and not stats["complete"] and big and n <= len(big):
            sol = [row[:n] for row in big[:n]]
            method = f"restriction of K_{len(big)}"
        level = {"n": n, "method": method, "stats": stats,
                 "seconds": round(time.perf_counter() - t0, 4)}
        if sol is not None:
            assert mono_clique(sol, s, t) is None, "bad counterexample"
            level["result"] = "counterexample"
            level["coloring"] = sol
            if count and n <= 8:
                _, cs = search(n, s, t, find_all=True, budget=budget)
                level["labelled_count"] = cs["solutions"] if cs["complete"] else None
        elif stats["complete"]:
            level["result"] = "forced"
            level["proof"] = "exhaustive"
        elif n >= U:
            level["result"] = "forced"
            level["proof"] = "bound"
        else:
            level["result"] = "budget"
        out["levels"].append(level)
        if verbose:
            print_level(level, s, t)
            if show_all and level.get("coloring") and n >= 2:
                print_matrix(level["coloring"])
        if level["result"] == "forced":
            out["R"], out["status"] = n, "proven"
            PROVEN[(s, t)] = PROVEN[(t, s)] = n
            break
        if level["result"] == "budget":
            out["status"] = "range"
            out["lower_bound"] = n
            break
        n += 1
    return out


def print_level(level, s, t):
    n = level["n"]
    st = level["stats"] or {}
    if level["result"] == "counterexample":
        extra = ""
        if "labelled_count" in level:
            extra = f", {level['labelled_count']} labelled counterexamples in total"
        nodes = f", {st['nodes']} nodes" if st else ""
        print(f"  N={n:2d}  counterexample found ({level['method']}{nodes}, "
              f"{level['seconds']}s){extra}")
    elif level["result"] == "forced" and level["proof"] == "exhaustive":
        print(f"  N={n:2d}  NO counterexample: exhaustive search of "
              f"{st['nodes']} nodes ({st['pruned_clique']} clique prunes, "
              f"{st['pruned_degree']} degree prunes, {level['seconds']}s)")
        print(f"  => every red/blue colouring of K_{n} has a red K_{s} "
              f"or a blue K_{t}")
    elif level["result"] == "forced":
        print(f"  N={n:2d}  NO counterexample: forced by the bound "
              f"R({s},{t}) <= R({s-1},{t}) + R({s},{t-1}) = {n} "
              f"(exhaustive search would exceed the budget)")
    else:
        print(f"  N={n:2d}  search budget exhausted after {st['nodes']} nodes "
              f"- undecided")


def print_matrix(mat):
    n = len(mat)
    print("     " + " ".join(f"{j:2d}" for j in range(n)))
    for i in range(n):
        row = " ".join(" ." if i == j else (" R" if mat[i][j] == RED else " B")
                       for j in range(n))
        print(f"  {i:2d} {row}")


def report(res, show_matrix=True):
    s, t = res["s"], res["t"]
    print()
    if res["status"] == "proven":
        print(f"R({s},{t}) = {res['R']}")
    else:
        print(f"{res['lower_bound']} <= R({s},{t}) <= {res['upper_bound']}  "
              f"(undecided at N={res['lower_bound']} within the budget; "
              f"literature value: {known_text(s, t)})")
    last = [l for l in res["levels"] if l["result"] == "counterexample"]
    if show_matrix and last and last[-1]["n"] > 0:
        l = last[-1]
        print(f"Largest counterexample: K_{l['n']} with no red K_{s} and "
              f"no blue K_{t}:")
        print_matrix(l["coloring"])


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("s", nargs="?", type=int, help="red clique size")
    p.add_argument("t", nargs="?", type=int, help="blue clique size")
    p.add_argument("--sweep", type=int, metavar="K",
                   help="solve every (s,t) with s+t=K, from (1,K-1) to (K-1,1)")
    p.add_argument("--budget", type=float, default=5e6,
                   help="max search nodes per N (default 5e6)")
    p.add_argument("--count", action="store_true",
                   help="count all labelled counterexamples for N<=8")
    p.add_argument("--json", help="write results to this JSON file")
    p.add_argument("--show-all", action="store_true",
                   help="print the counterexample colouring for every N")
    a = p.parse_args()

    budget = int(a.budget)
    pairs = []
    if a.sweep:
        pairs = [(s, a.sweep - s) for s in range(1, a.sweep)]
    elif a.s and a.t:
        pairs = [(a.s, a.t)]
    else:
        p.error("give s t, or --sweep K")

    # solve smaller pairs first so their exact values tighten the degree bound
    results = []
    for s, t in pairs:
        for a2 in range(2, s + 1):
            for b2 in range(2, t + 1):
                if (a2, b2) != (s, t) and (a2, b2) not in PROVEN \
                        and upper_bound(a2, b2) <= 18:
                    ramsey(a2, b2, budget=budget, verbose=False)
        print(f"\n=== R({s},{t}): red K_{s} vs blue K_{t} ===")
        res = ramsey(s, t, budget=budget, count=a.count, show_all=a.show_all)
        report(res)
        results.append(res)

    if a.sweep:
        print(f"\nSweep s+t={a.sweep}:")
        for r in results:
            v = r["R"] if r["status"] == "proven" else \
                f"in [{r['lower_bound']}, {r['upper_bound']}]"
            print(f"  R({r['s']},{r['t']}) = {v}")

    if a.json:
        with open(a.json, "w") as f:
            json.dump(results, f)
        print(f"\nSaved to {a.json}")


if __name__ == "__main__":
    main()
