"""Regression tests for group betweenness of groups with three or more nodes.

The successive-update step of ``group_betweenness_centrality`` mixed the
original path counts ``sigma`` with the reduced counts ``sigma_m`` (paths that
avoid the nodes already processed), and skipped some update terms in directed
graphs. Groups of size >= 3 then got wrong scores, e.g. a positive score for a
group that no shortest path between two non-members goes through.
"""

import itertools

import pytest

import networkx as nx


def _brute_force_gbc(G, C):
    """Unnormalized group betweenness straight from the definition."""
    C = set(C)
    others = [n for n in G if n not in C]
    pairs = (
        itertools.permutations(others, 2)
        if G.is_directed()
        else itertools.combinations(others, 2)
    )
    total = 0.0
    for s, t in pairs:
        if not nx.has_path(G, s, t):
            continue
        paths = list(nx.all_shortest_paths(G, s, t))
        total += sum(1 for p in paths if C & set(p[1:-1])) / len(paths)
    return total


def test_peripheral_group_not_brokering_scores_zero():
    # The only non-members, 3 and 4, are adjacent: no one goes through the group.
    G = nx.Graph([(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (3, 4)])
    group = [0, 1, 2]
    assert nx.group_betweenness_centrality(G, group, normalized=False) == 0
    assert nx.group_betweenness_centrality(G, group) == 0


def test_three_node_group_matches_definition_undirected():
    G = nx.Graph(
        [
            (0, 3), (0, 4), (0, 8), (1, 4), (1, 5), (1, 8), (2, 3),
            (2, 6), (2, 8), (3, 5), (4, 5), (5, 7), (6, 7),
        ]
    )  # fmt: skip
    group = [0, 2, 4]
    expected = _brute_force_gbc(G, group)
    assert expected == pytest.approx(4.0)
    assert nx.group_betweenness_centrality(
        G, group, normalized=False
    ) == pytest.approx(expected)


def test_three_node_group_matches_definition_directed():
    G = nx.DiGraph([(0, 1), (1, 2), (1, 4), (2, 3), (3, 0), (4, 2)])
    group = [0, 1, 2]
    # 3 -> 4 goes 3, 0, 1, 4 and 4 -> 3 goes 4, 2, 3: both through the group.
    assert _brute_force_gbc(G, group) == pytest.approx(2.0)
    assert nx.group_betweenness_centrality(G, group, normalized=False) == (
        pytest.approx(2.0)
    )


@pytest.mark.parametrize("seed", range(20))
def test_random_groups_match_definition(seed):
    G = nx.gnp_random_graph(9, 0.35, seed=seed)
    for group in itertools.combinations(list(G)[:6], 3):
        assert nx.group_betweenness_centrality(
            G, group, normalized=False
        ) == pytest.approx(_brute_force_gbc(G, group)), group
