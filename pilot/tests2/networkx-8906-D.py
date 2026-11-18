"""Regression test: whole-graph effective_size on weighted graphs must
normalize mutual weights by each node's own (row) maximum."""

import math

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def _burt_effective_size(G, u, weight):
    """Direct implementation of Burt's formula, independent of networkx."""

    def mw(a, b):
        w = 0
        if G.has_edge(a, b):
            w += G[a][b].get(weight, 1)
        if G.is_directed() and G.has_edge(b, a):
            w += G[b][a].get(weight, 1)
        elif not G.is_directed() and G.has_edge(a, b):
            w *= 2
        return w

    def nbrs(a):
        return set(nx.all_neighbors(G, a)) - {a}

    total_u = sum(mw(u, q) for q in nbrs(u))
    result = 0.0
    for j in nbrs(u):
        max_j = max(mw(j, q) for q in nbrs(j))
        redundancy = sum(mw(u, q) / total_u * mw(j, q) / max_j for q in nbrs(u))
        result += 1 - redundancy
    return result


@pytest.mark.parametrize("graph_type", [nx.DiGraph, nx.Graph])
def test_effective_size_weighted_whole_graph_matches_burt(graph_type):
    G = graph_type()
    G.add_weighted_edges_from(
        [(0, 1, 5), (1, 2, 1), (2, 0, 2), (0, 3, 1), (3, 1, 4), (2, 3, 3)]
    )
    whole = nx.effective_size(G, weight="weight")
    per_node = nx.effective_size(G, nodes=list(G), weight="weight")
    for n in G:
        expected = _burt_effective_size(G, n, "weight")
        assert math.isclose(whole[n], expected, rel_tol=1e-12)
        assert math.isclose(per_node[n], expected, rel_tol=1e-12)
