"""Regression test: whole-graph effective_size must normalize m_vw by the
row maximum (per node v), not by the column maximum."""

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def _weighted_digraph():
    G = nx.DiGraph()
    G.add_weighted_edges_from(
        [(0, 1, 3), (1, 0, 1), (0, 2, 2), (2, 1, 5), (1, 3, 1), (3, 0, 4), (2, 3, 1)]
    )
    return G


def _burt_effective_size(G, u, weight):
    """Direct implementation of Burt's formula, independent of the library."""
    nbrs = lambda x: set(G.predecessors(x)) | set(G.successors(x))

    def a(x, y):
        return G[x][y].get(weight, 1) if G.has_edge(x, y) else 0

    def mw(x, y):
        return a(x, y) + a(y, x)

    def p(x, y):
        return mw(x, y) / sum(mw(x, z) for z in nbrs(x))

    def m(x, y):
        return mw(x, y) / max(mw(x, z) for z in nbrs(x))

    return sum(1 - sum(p(u, w) * m(v, w) for w in nbrs(u)) for v in nbrs(u))


@pytest.mark.parametrize("weight", ["weight", None])
def test_effective_size_whole_graph_weighted_directed(weight):
    G = _weighted_digraph()
    expected = {u: _burt_effective_size(G, u, weight) for u in G}
    whole = nx.effective_size(G, weight=weight)
    per_node = nx.effective_size(G, nodes=list(G), weight=weight)
    assert whole == pytest.approx(expected)
    assert per_node == pytest.approx(expected)


def test_effective_size_whole_graph_weighted_undirected():
    G = nx.Graph()
    G.add_weighted_edges_from([(0, 1, 1), (0, 2, 4), (1, 2, 2), (2, 3, 3), (3, 0, 1)])
    expected = {u: _burt_effective_size(G.to_directed(), u, "weight") for u in G}
    # For undirected graphs, the mutual weight of an edge is counted from both
    # directions, which scales numerator and denominator equally.
    assert nx.effective_size(G, weight="weight") == pytest.approx(expected)
    assert nx.effective_size(G, nodes=list(G), weight="weight") == pytest.approx(
        expected
    )
