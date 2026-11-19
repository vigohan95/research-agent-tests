"""Regression tests for group betweenness centrality with groups of 3+ nodes."""

import itertools

import pytest

import networkx as nx


def _brute_force_gbc(G, C):
    """Unnormalized group betweenness, endpoints excluded, from all shortest paths."""
    C = set(C)
    others = [n for n in G if n not in C]
    pairs = (
        itertools.permutations(others, 2)
        if G.is_directed()
        else itertools.combinations(others, 2)
    )
    total = 0
    for s, t in pairs:
        if not nx.has_path(G, s, t):
            continue
        paths = list(nx.all_shortest_paths(G, s, t))
        total += sum(1 for p in paths if C & set(p[1:-1])) / len(paths)
    return total


def test_peripheral_group_has_zero_betweenness_undirected():
    # The only pair outside the group, (0, 1), is adjacent, so no shortest
    # path between non-group nodes passes through the group.
    G = nx.Graph([(0, 1), (1, 3), (1, 4), (2, 3), (2, 4)])
    C = [2, 3, 4]
    assert nx.group_betweenness_centrality(G, C, normalized=False) == pytest.approx(
        0.0, abs=1e-12
    )
    assert nx.group_betweenness_centrality(G, C) == pytest.approx(0.0, abs=1e-12)


def test_group_betweenness_directed_three_nodes():
    # Pairs outside the group: 0 -> 1 is a direct edge, 1 -> 0 goes 1 -> 2 -> 0.
    G = nx.DiGraph(
        [(0, 1), (0, 4), (1, 2), (2, 0), (2, 1), (2, 4), (3, 1), (3, 2), (4, 0), (4, 3)]
    )
    C = [2, 3, 4]
    assert nx.group_betweenness_centrality(G, C, normalized=False) == pytest.approx(
        1.0
    )


@pytest.mark.parametrize("directed", [False, True])
def test_group_betweenness_matches_brute_force(directed):
    p = 0.45 if directed else 0.3
    checked = 0
    for seed in range(60):
        G = nx.gnp_random_graph(8, p, seed=seed, directed=directed)
        connected = (
            nx.is_strongly_connected(G) if directed else nx.is_connected(G)
        )
        if not connected:
            continue
        nodes = sorted(G)
        for k in (2, 3, 4):
            C = nodes[seed % 3 : seed % 3 + k]
            expected = _brute_force_gbc(G, C)
            result = nx.group_betweenness_centrality(G, C, normalized=False)
            assert result == pytest.approx(expected), (seed, C)
            checked += 1
    assert checked > 0
