"""Regression tests: group betweenness must use the updated path counts
for every correction term while nodes are added to the group."""

import itertools

import pytest

import networkx as nx


def _brute_group_betweenness(G, C):
    C = set(C)
    total = 0.0
    others = [n for n in G if n not in C]
    pairs = itertools.permutations if G.is_directed() else itertools.combinations
    for s, t in pairs(others, 2):
        if not nx.has_path(G, s, t):
            continue
        paths = list(nx.all_shortest_paths(G, s, t))
        total += sum(1 for p in paths if C & set(p[1:-1])) / len(paths)
    return total


def test_peripheral_group_has_zero_betweenness():
    # The only nodes outside the group, 0 and 1, are adjacent, so no
    # shortest path between non-group nodes passes through the group.
    G = nx.Graph([(0, 1), (1, 3), (1, 4), (2, 3), (2, 4)])
    C = [2, 3, 4]
    assert nx.group_betweenness_centrality(G, C, normalized=False) == pytest.approx(
        0.0, abs=1e-12
    )
    assert nx.group_betweenness_centrality(G, C) == pytest.approx(0.0, abs=1e-12)


def test_complete_bipartite_group_zero():
    G = nx.complete_bipartite_graph(2, 3)  # parts {0,1} and {2,3,4}
    # group {0, 2, 3}: remaining nodes 1 and 4 are adjacent
    assert nx.group_betweenness_centrality(
        G, [0, 2, 3], normalized=False
    ) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize("seed", range(40))
def test_matches_brute_force_on_random_graphs(seed):
    G = nx.gnp_random_graph(8, 0.4, seed=seed)
    for C in itertools.islice(itertools.combinations(G, 3), 0, None, 7):
        expected = _brute_group_betweenness(G, C)
        got = nx.group_betweenness_centrality(G, C, normalized=False)
        assert got == pytest.approx(expected, abs=1e-9), (sorted(G.edges()), C)
