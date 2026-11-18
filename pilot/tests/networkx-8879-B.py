"""Regression tests for group_betweenness_centrality on small undirected graphs
where the incremental update over several group nodes went wrong."""

import pytest

import networkx as nx


def test_group_betweenness_zero_when_no_path_crosses_group():
    # Nodes outside the group are 1 and 3, which are adjacent, so the only
    # shortest 1-3 path is the edge itself and no group node is an interior
    # node of it. The group betweenness must be 0.
    G = nx.Graph([(0, 3), (0, 4), (1, 3), (1, 4), (2, 3)])
    C = {0, 2, 4}
    assert nx.group_betweenness_centrality(G, C) == pytest.approx(0.0, abs=1e-12)
    assert nx.group_betweenness_centrality(
        G, C, normalized=False
    ) == pytest.approx(0.0, abs=1e-12)


def test_group_betweenness_single_crossing_pair():
    # Nodes outside the group are 0 and 1 (not adjacent). Their only shortest
    # path is 0-3-1, which passes through group node 3, so the unnormalized
    # value is 1 (one undirected pair) and the normalized value is
    # 2 / ((5 - 3) * (5 - 3 - 1)) = 1.
    G = nx.Graph([(0, 3), (0, 4), (1, 3), (2, 3), (2, 4)])
    C = {2, 3, 4}
    assert nx.group_betweenness_centrality(G, C) == pytest.approx(1.0)
    assert nx.group_betweenness_centrality(G, C, normalized=False) == pytest.approx(
        1.0
    )


def test_group_betweenness_list_of_groups():
    G = nx.Graph([(0, 3), (0, 4), (1, 3), (1, 4), (2, 3)])
    result = nx.group_betweenness_centrality(G, [{0, 2, 4}, [4, 2, 0]])
    assert result == pytest.approx([0.0, 0.0], abs=1e-12)
