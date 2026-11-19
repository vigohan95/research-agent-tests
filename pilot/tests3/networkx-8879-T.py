"""Regression tests: group betweenness of groups with 3+ nodes.

The successive-update step of ``group_betweenness_centrality`` mixed the
original ``sigma`` matrix with the already-updated ``sigma_m`` matrix when
removing paths of the form v -> x -> y.  From the third group member on, this
over-counted pairs, so groups that broker nothing got a positive score.

Expected values are computed independently by enumerating all shortest paths
(the definition in Everett & Borgatti 1999).
"""

import itertools
import math

import pytest

import networkx as nx


def _brute_group_betweenness(G, C):
    C = set(C)
    others = [n for n in G if n not in C]
    total = 0.0
    for s, t in itertools.combinations(others, 2):
        if not nx.has_path(G, s, t):
            continue
        paths = list(nx.all_shortest_paths(G, s, t))
        total += sum(1 for p in paths if C & set(p[1:-1])) / len(paths)
    return total


# Peripheral group: the only non-group pair (1, 2) is adjacent, so no
# shortest path between non-members goes through the group -> exactly 0.
PERIPHERAL = (
    [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)],
    [0, 3, 4],
    0.0,
)
# A group that does broker; exact value 7.5 (unnormalized).
BROKER = (
    [(0, 3), (0, 4), (1, 2), (1, 6), (2, 3), (3, 5), (3, 6), (3, 7), (4, 6), (4, 7)],
    [3, 4, 0],
    7.5,
)


@pytest.mark.parametrize("edges, group, expected", [PERIPHERAL, BROKER])
@pytest.mark.parametrize("order", range(6))
def test_group_betweenness_three_member_groups(edges, group, expected, order):
    G = nx.Graph(edges)
    group = list(itertools.permutations(group))[order]
    assert math.isclose(_brute_group_betweenness(G, group), expected, rel_tol=1e-12)

    result = nx.group_betweenness_centrality(G, group, normalized=False)
    # atol: the peripheral expected value is exactly 0 and the algorithm
    # reaches it through float subtractions, so rtol alone cannot apply.
    assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9)

    n, c = len(G), len(group)
    normed = nx.group_betweenness_centrality(G, group, normalized=True)
    # Normalized form divides the directed-pair count 2 * expected by
    # (n - c)(n - c - 1); same atol reason as above.
    assert math.isclose(
        normed, 2 * expected / ((n - c) * (n - c - 1)), rel_tol=1e-9, abs_tol=1e-9
    )


@pytest.mark.parametrize("seed", range(40))
def test_group_betweenness_matches_path_enumeration(seed):
    G = nx.gnp_random_graph(8, 0.4, seed=seed)
    if not nx.is_connected(G):
        pytest.skip("disconnected sample")
    rng = __import__("random").Random(seed)
    for k in (3, 4):
        group = rng.sample(list(G), k)
        result = nx.group_betweenness_centrality(G, group, normalized=False)
        expected = _brute_group_betweenness(G, group)
        # atol: expected can be exactly 0 (see above).
        assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9)
