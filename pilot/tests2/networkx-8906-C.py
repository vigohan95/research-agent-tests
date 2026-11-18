"""Regression tests: whole-graph effective_size must normalize m_vw by
the row-wise (per-node v) maximum mutual weight."""

import math

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def _burt_effective_size(G, weight):
    """Direct implementation of Burt's formula for reference."""
    nodes = list(G)

    def mw(a, b):
        w = 0
        if G.has_edge(a, b):
            w += G[a][b].get(weight, 1)
        if G.has_edge(b, a):
            w += G[b][a].get(weight, 1)
        return w

    nbrs = {u: set(nx.all_neighbors(G, u)) - {u} for u in nodes}
    result = {}
    for u in nodes:
        tot = sum(mw(u, w) for w in nbrs[u])
        es = 0.0
        for v in nbrs[u]:
            vmax = max(mw(v, w) for w in nbrs[v])
            red = sum(
                (mw(u, w) / tot) * (mw(v, w) / vmax) for w in nbrs[u] if w != v
            )
            es += 1 - red
        result[u] = es
    return result


def _weighted_digraph():
    G = nx.DiGraph()
    G.add_weighted_edges_from(
        [
            (0, 1, 2), (0, 3, 9), (0, 6, 1), (0, 7, 3), (1, 2, 5), (1, 3, 4),
            (1, 6, 4), (2, 5, 4), (3, 4, 4), (3, 5, 3), (3, 6, 5), (4, 5, 5),
            (4, 6, 1), (6, 7, 4),
        ],
        weight="w",
    )
    return G


def test_effective_size_weighted_directed_whole_graph():
    G = _weighted_digraph()
    expected = _burt_effective_size(G, "w")
    whole = nx.effective_size(G, weight="w")
    for n in G:
        assert whole[n] == pytest.approx(expected[n])


def test_effective_size_whole_graph_matches_per_node():
    G = _weighted_digraph()
    whole = nx.effective_size(G, weight="w")
    per_node = nx.effective_size(G, nodes=list(G), weight="w")
    for n in G:
        assert whole[n] == pytest.approx(per_node[n])


def test_effective_size_weighted_undirected_whole_graph():
    G = _weighted_digraph().to_undirected()
    whole = nx.effective_size(G, weight="w")
    per_node = nx.effective_size(G, nodes=list(G), weight="w")
    expected = _burt_effective_size(G, "w")
    for n in G:
        assert not math.isnan(whole[n])
        assert whole[n] == pytest.approx(per_node[n])
        assert whole[n] == pytest.approx(expected[n])
