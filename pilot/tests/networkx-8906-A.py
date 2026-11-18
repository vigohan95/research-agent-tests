"""Regression test: effective_size must not depend on whether ``nodes`` is passed.

Burt's effective size of ``u`` is

    e(u) = sum_{v in N(u) - {u}} (1 - sum_{w in N(u)} p_uw * m_vw)

where ``a_uv`` is the mutual weight (weight(u->v) + weight(v->u)),
``p_uw = a_uw / sum_x a_ux`` and ``m_vw = a_vw / max_x a_vx``.

The expected values below are computed with exact rational arithmetic by a
small reference implementation written directly from that definition, which
does not use any networkx code.  Node 0 of the weighted undirected graph was
also checked by hand (163/72).
"""

from fractions import Fraction

import pytest

import networkx as nx


def _reference_effective_size(edges, directed):
    """Burt's effective size from the definition, using exact fractions."""
    w = {}
    nodes = set()
    for u, v, wt in edges:
        nodes |= {u, v}
        w[(u, v)] = Fraction(wt)
        if not directed:
            w[(v, u)] = Fraction(wt)

    def a(u, v):
        return w.get((u, v), 0) + w.get((v, u), 0)

    nbrs = {n: {x for x in nodes if x != n and a(n, x) != 0} for n in nodes}

    def p(u, v):
        return a(u, v) / sum(a(u, x) for x in nbrs[u])

    def m(u, v):
        return a(u, v) / max(a(u, x) for x in nbrs[u])

    return {
        u: sum(1 - sum(p(u, q) * m(v, q) for q in nbrs[u]) for v in nbrs[u])
        for u in nodes
    }


WEIGHTED_UNDIRECTED = [(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 4), (2, 3, 1)]
# Every node has at least one out-edge (no sinks).
WEIGHTED_DIRECTED = [
    (0, 1, 1),
    (0, 2, 2),
    (1, 0, 3),
    (2, 1, 1),
    (2, 3, 2),
    (3, 0, 1),
    (3, 1, 5),
]
UNWEIGHTED_DIRECTED = [(0, 1, 1), (0, 2, 1), (1, 0, 1), (2, 1, 1), (2, 3, 1), (3, 0, 1)]


def test_reference_hand_value():
    # Hand computation for node 0 of WEIGHTED_UNDIRECTED:
    # v=1: 1 - (2/6)(4/4) = 2/3
    # v=2: 1 - (1/6)(4/4) - (3/6)(1/4) = 17/24
    # v=3: 1 - (2/6)(1/3) = 8/9
    ref = _reference_effective_size(WEIGHTED_UNDIRECTED, directed=False)
    assert ref[0] == Fraction(2, 3) + Fraction(17, 24) + Fraction(8, 9)
    assert ref[0] == Fraction(163, 72)


@pytest.mark.parametrize(
    ("edges", "directed", "weight"),
    [
        (WEIGHTED_UNDIRECTED, False, "weight"),
        (WEIGHTED_DIRECTED, True, "weight"),
        (UNWEIGHTED_DIRECTED, True, None),
    ],
)
def test_effective_size_matches_definition(edges, directed, weight):
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_weighted_edges_from(edges)
    expected = _reference_effective_size(edges, directed)

    default = nx.effective_size(G, weight=weight)
    explicit = nx.effective_size(G, nodes=list(G), weight=weight)

    for n in G:
        assert default[n] == pytest.approx(float(expected[n]), abs=1e-12)
        assert explicit[n] == pytest.approx(float(expected[n]), abs=1e-12)
        assert default[n] == pytest.approx(explicit[n], abs=1e-12)


def test_weighted_undirected_known_values():
    G = nx.Graph()
    G.add_weighted_edges_from(WEIGHTED_UNDIRECTED)
    es = nx.effective_size(G, weight="weight")
    assert es[0] == pytest.approx(163 / 72)
