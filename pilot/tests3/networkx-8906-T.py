"""Regression tests: whole-graph ``effective_size`` on weighted / directed graphs.

The sparse-matrix fast path (used when ``nodes is None`` and scipy is
available) normalized the mutual-weight matrix by row maxima using a 1-D
array, which broadcasts across columns: column ``j`` was divided by the max
of row ``j`` instead of row ``i`` by the max of row ``i``.  Whenever row
maxima differ (weighted graphs, or directed graphs with a mix of reciprocated
and one-way ties) the results disagreed with Burt's definition, while
unweighted undirected graphs (all row maxima equal to 1) were unaffected.
"""

import pytest

import networkx as nx

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")


def burt_effective_size(G, weight=None):
    """Independent reference implementation of Burt's (1992) effective size.

    e(u) = sum_{v in N(u)} (1 - sum_{w in N(u), w != u, v} p_uw * m_vw)
    with p_uw = mutual weight / sum of u's mutual weights and
    m_vw = mutual weight / v's largest mutual weight.
    """

    def a(x, y):
        if G.has_edge(x, y):
            return 1 if weight is None else G[x][y].get(weight, 1)
        return 0

    def mw(x, y):
        return a(x, y) + a(y, x) if G.is_directed() else a(x, y)

    def nbrs(x):
        return set(nx.all_neighbors(G, x)) - {x}

    result = {}
    for u in G:
        Nu = nbrs(u)
        tot_u = sum(mw(u, w) for w in Nu)
        es = 0.0
        for v in Nu:
            max_v = max(mw(v, k) for k in nbrs(v))
            red = sum(mw(u, w) / tot_u * mw(v, w) / max_v for w in Nu - {v})
            es += 1 - red
        result[u] = es
    return result


def test_weighted_undirected_triangle_closed_form():
    # Hand-computed from Burt's formula:
    #   e(a) = 1/3 + 2/3 = 1
    #   e(b) = 1/4 + (1 - 1/4 * 2/3) = 13/12
    #   e(c) = (1 - 3/5 * 1/2) + (1 - 2/5 * 1/3) = 47/30
    G = nx.Graph()
    G.add_weighted_edges_from([("a", "b", 1), ("a", "c", 2), ("b", "c", 3)])
    es = nx.effective_size(G, weight="weight")
    expected = {"a": 1.0, "b": 13 / 12, "c": 47 / 30}
    for n, val in expected.items():
        assert es[n] == pytest.approx(val, rel=1e-12)


def _directed_weighted():
    G = nx.DiGraph()
    G.add_weighted_edges_from(
        [(0, 1, 3), (1, 2, 1), (2, 0, 5), (0, 3, 2), (3, 1, 4), (2, 3, 1), (1, 0, 2)]
    )
    return G, "weight"


def _directed_unweighted_mixed_reciprocity():
    # Reciprocated ties have mutual weight 2, one-way ties 1, so row maxima differ.
    G = nx.DiGraph([(0, 1), (1, 0), (1, 2), (2, 3), (3, 0), (0, 2), (3, 1), (1, 3)])
    return G, None


def _undirected_weighted():
    G = nx.Graph()
    G.add_weighted_edges_from(
        [(0, 1, 1.5), (0, 2, 4), (1, 2, 0.5), (2, 3, 2), (3, 4, 7), (1, 4, 1), (0, 4, 3)]
    )
    return G, "weight"


@pytest.mark.parametrize(
    "make_graph",
    [_directed_weighted, _directed_unweighted_mixed_reciprocity, _undirected_weighted],
)
def test_whole_graph_matches_reference_and_per_node_path(make_graph):
    G, weight = make_graph()
    expected = burt_effective_size(G, weight=weight)
    whole = nx.effective_size(G, weight=weight)  # sparse-matrix path
    per_node = nx.effective_size(G, nodes=list(G), weight=weight)  # loop path
    for n in G:
        assert whole[n] == pytest.approx(expected[n], rel=1e-12)
        assert per_node[n] == pytest.approx(expected[n], rel=1e-12)
