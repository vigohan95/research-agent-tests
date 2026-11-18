"""Regression tests: effective_size must not depend on whether ``nodes`` is passed.

Expected values are worked out by hand from Burt's definition

    ES(i) = sum_{j in N(i)} (1 - sum_{q != i, j} p_iq * m_jq)

where p_iq is the mutual weight of i and q divided by the sum of i's mutual
weights, and m_jq is the mutual weight of j and q divided by j's largest
mutual weight.
"""

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


def _weighted_undirected():
    G = nx.Graph()
    G.add_weighted_edges_from([(0, 1, 1), (0, 2, 2), (1, 2, 3), (0, 3, 1)])
    return G


def _unweighted_directed():
    D = nx.DiGraph()
    D.add_edges_from([(0, 1), (0, 2), (1, 0), (2, 1)])
    return D


def _weighted_directed():
    D = nx.DiGraph()
    D.add_weighted_edges_from([(0, 1, 2), (0, 2, 1), (1, 0, 3), (2, 1, 1)])
    return D


# Hand-computed reference values.
WEIGHTED_UNDIRECTED = {0: 9 / 4, 1: 13 / 12, 2: 47 / 30, 3: 1.0}
UNWEIGHTED_DIRECTED = {0: 7 / 6, 1: 7 / 6, 2: 1.0}
WEIGHTED_DIRECTED = {0: 17 / 15, 1: 17 / 15, 2: 1.0}


@pytest.mark.parametrize("pass_nodes", [False, True])
def test_effective_size_weighted_undirected(pass_nodes):
    G = _weighted_undirected()
    kwargs = {"nodes": list(G)} if pass_nodes else {}
    result = nx.effective_size(G, weight="weight", **kwargs)
    assert result == pytest.approx(WEIGHTED_UNDIRECTED)


@pytest.mark.parametrize("pass_nodes", [False, True])
def test_effective_size_unweighted_directed(pass_nodes):
    D = _unweighted_directed()
    kwargs = {"nodes": list(D)} if pass_nodes else {}
    result = nx.effective_size(D, **kwargs)
    assert result == pytest.approx(UNWEIGHTED_DIRECTED)


@pytest.mark.parametrize("pass_nodes", [False, True])
def test_effective_size_weighted_directed(pass_nodes):
    D = _weighted_directed()
    kwargs = {"nodes": list(D)} if pass_nodes else {}
    result = nx.effective_size(D, weight="weight", **kwargs)
    assert result == pytest.approx(WEIGHTED_DIRECTED)


def test_effective_size_unweighted_undirected_unchanged():
    # Borgatti's simplified formula: n - 2t/n for the ego network.
    G = _weighted_undirected()
    expected = {0: 3 - 2 / 3, 1: 1.0, 2: 1.0, 3: 1.0}
    assert nx.effective_size(G) == pytest.approx(expected)
    assert nx.effective_size(G, nodes=list(G)) == pytest.approx(expected)
