"""Regression tests: group betweenness of multi-node groups on undirected graphs.

Expected values are derived by hand from the definition: for every unordered
pair (s, t) of nodes outside the group, add the fraction of shortest s-t paths
that have an interior node in the group.
"""

import itertools

import pytest

import networkx as nx


def _all_orders(group):
    return [list(p) for p in itertools.permutations(group)]


@pytest.mark.parametrize("group", _all_orders([0, 1, 3]))
def test_group_betweenness_zero_when_outside_pair_adjacent(group):
    # Nodes outside the group are 2 and 4, which are adjacent, so their only
    # shortest path (2-4) has no interior node: group betweenness is 0.
    G = nx.Graph([(0, 1), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4)])
    assert nx.group_betweenness_centrality(G, group) == pytest.approx(0, abs=1e-9)
    assert nx.group_betweenness_centrality(
        G, group, normalized=False
    ) == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize("group", _all_orders([0, 2, 3]))
def test_group_betweenness_all_paths_through_group(group):
    # Outside nodes are 1 and 4 (distance 2). Their shortest paths are
    # 1-0-4 and 1-2-4, both through the group: 1 pair, fraction 1.
    # Normalized: 2 * 1 / ((5 - 3) * (5 - 3 - 1)) = 1.0; unnormalized: 1.0.
    G = nx.Graph([(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 4), (3, 4)])
    assert nx.group_betweenness_centrality(G, group) == pytest.approx(1.0)
    assert nx.group_betweenness_centrality(
        G, group, normalized=False
    ) == pytest.approx(1.0)


def test_group_betweenness_list_of_groups():
    G = nx.Graph([(0, 1), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4)])
    # Group [4] alone: outside pairs among {0,1,2,3}. Shortest paths through 4:
    # (0,2): 0-4-2 only -> 1; (1,2): 1-4-2 -> 1; (2,3): 3-4-2 -> 1;
    # (1,3): 1-0-3 and 1-4-3 -> 1/2; (0,1), (0,3) adjacent -> 0. Sum 3.5,
    # normalized 2 * 3.5 / (4 * 3) = 7/12.
    result = nx.group_betweenness_centrality(G, [[0, 1, 3], [4]])
    assert result == pytest.approx([0.0, 7 / 12], abs=1e-9)
