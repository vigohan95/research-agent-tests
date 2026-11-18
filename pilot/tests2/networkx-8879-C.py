"""Regression tests: group betweenness for groups of three or more nodes.

The successive-update step must use the already-updated sigma matrix for
every term; mixing in the original sigma gave peripheral groups (through
which no shortest path between non-members passes) a positive score.
"""

import itertools

import pytest

import networkx as nx


def _brute_group_betweenness(G, C):
    C = set(C)
    total = 0.0
    others = [n for n in G if n not in C]
    for s, t in itertools.combinations(others, 2):
        if not nx.has_path(G, s, t):
            continue
        paths = list(nx.all_shortest_paths(G, s, t))
        total += sum(1 for p in paths if C & set(p[1:-1])) / len(paths)
    return total


def test_peripheral_group_of_three_has_zero_betweenness():
    G = nx.Graph(
        [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 5), (2, 4), (2, 5), (4, 5)]
    )
    # No shortest path between nodes 1, 2, 5 passes through 0, 3 or 4.
    assert _brute_group_betweenness(G, [4, 0, 3]) == 0
    assert nx.group_betweenness_centrality(G, [4, 0, 3]) == pytest.approx(0, abs=1e-12)
    assert nx.group_betweenness_centrality(
        G, [4, 0, 3], normalized=False
    ) == pytest.approx(0, abs=1e-12)


@pytest.mark.parametrize(
    ("edges", "group"),
    [
        ([(0, 4), (1, 4), (1, 5), (2, 4), (3, 4), (3, 5)], [5, 1, 4]),
        ([(0, 1), (0, 2), (0, 4), (1, 3), (2, 4), (3, 4)], [1, 4, 0]),
        (
            [(0, 2), (0, 4), (1, 2), (1, 3), (1, 5), (1, 6), (2, 5), (2, 6), (3, 5)],
            [4, 1, 3],
        ),
    ],
)
def test_group_of_three_matches_definition(edges, group):
    G = nx.Graph(edges)
    expected = _brute_group_betweenness(G, group)
    result = nx.group_betweenness_centrality(G, group, normalized=False)
    assert result == pytest.approx(expected)


def test_random_groups_match_definition():
    for seed in range(60):
        G = nx.gnp_random_graph(8, 0.4, seed=seed)
        for k in (1, 2, 3, 4):
            for group in itertools.islice(itertools.combinations(G, k), 0, None, 7):
                expected = _brute_group_betweenness(G, group)
                result = nx.group_betweenness_centrality(G, group, normalized=False)
                assert result == pytest.approx(expected), (seed, group)
