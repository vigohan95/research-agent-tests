"""Regression tests: whole-graph effective_size must match the per-node
definition (Burt) on weighted graphs, where nodes have different maximum
mutual weights."""

import math

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def _burt_effective_size(G, u, weight):
    """Direct implementation of Burt's formula, independent of networkx."""

    def mw(a, b):
        s = 0
        if G.has_edge(a, b):
            s += G[a][b].get(weight, 1)
        if G.is_directed() and G.has_edge(b, a):
            s += G[b][a].get(weight, 1)
        if not G.is_directed():
            s *= 2
        return s

    nbrs = set(nx.all_neighbors(G, u)) - {u}
    total_u = sum(mw(u, q) for q in nbrs)
    es = 0.0
    for j in nbrs:
        j_nbrs = set(nx.all_neighbors(G, j)) - {j}
        max_j = max(mw(j, q) for q in j_nbrs)
        red = sum(
            mw(u, q) / total_u * mw(j, q) / max_j for q in nbrs if q != j
        )
        es += 1 - red
    return es


def _weighted_digraph():
    G = nx.DiGraph()
    G.add_weighted_edges_from(
        [(0, 1, 3), (1, 0, 1), (0, 2, 2), (2, 1, 5), (1, 3, 4), (3, 0, 1), (2, 3, 1)]
    )
    return G


def _weighted_graph():
    G = nx.Graph()
    G.add_weighted_edges_from([(0, 1, 3), (0, 2, 2), (2, 1, 5), (1, 3, 4), (3, 0, 1)])
    return G


@pytest.mark.parametrize("make", [_weighted_digraph, _weighted_graph])
def test_effective_size_whole_graph_weighted_matches_definition(make):
    G = make()
    result = nx.effective_size(G, weight="weight")
    for u in G:
        assert math.isclose(result[u], _burt_effective_size(G, u, "weight"))


@pytest.mark.parametrize("make", [_weighted_digraph, _weighted_graph])
def test_effective_size_whole_graph_matches_per_node(make):
    G = make()
    whole = nx.effective_size(G, weight="weight")
    per_node = nx.effective_size(G, nodes=list(G), weight="weight")
    for u in G:
        assert whole[u] == pytest.approx(per_node[u])


def test_effective_size_weighted_undirected_known_value():
    # Hand computed: node 3 has neighbors 0 (w=1) and 1 (w=4).
    # j=0: 1 - (4/5)*(3/3) = 0.2 ; j=1: 1 - (1/5)*(3/5) = 0.88
    G = _weighted_graph()
    assert nx.effective_size(G, weight="weight")[3] == pytest.approx(1.08)
