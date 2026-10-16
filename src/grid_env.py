"""
Core environment for multi-agent self-healing smart grid experiments.
Built on the standard IEEE 33-bus radial distribution test feeder
(Baran & Wu, 1989), as provided by pandapower (case33bw), which already
includes the five standard normally-open tie-switches used throughout
the distribution network reconfiguration literature.
"""
import numpy as np
import pandapower as pp
import pandapower.networks as pn
import copy

TIE_LINES = [32, 33, 34, 35, 36]  # indices of the 5 normally-open tie lines in case33bw
NORMAL_LINES = list(range(32))     # the 32 normally-closed sectionalizing lines

# Zone assignment: partition the 33 buses into 5 agent zones, each zone
# roughly corresponding to the branch of the feeder tree that a given
# tie-switch can reconnect. Zone 0 = the substation-adjacent backbone.
ZONE_OF_BUS = {
    0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1, 8: 2, 9: 2, 10: 2,
    11: 2, 12: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 1, 19: 1,
    20: 1, 21: 1, 22: 3, 23: 3, 24: 3, 25: 4, 26: 4, 27: 4, 28: 4,
    29: 4, 30: 4, 31: 4, 32: 4,
}
N_ZONES = 5


def build_base_net():
    net = pn.case33bw()
    return net


def get_load_by_bus(net):
    loads = np.zeros(len(net.bus))
    for _, row in net.load.iterrows():
        loads[int(row.bus)] += row.p_mw
    return loads


def energized_buses(net):
    """Return the set of bus indices electrically connected to the
    external grid (slack), given current line in_service status."""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(net.bus.index)
    for _, row in net.line.iterrows():
        if row.in_service:
            G.add_edge(int(row.from_bus), int(row.to_bus))
    for _, row in net.switch.iterrows():
        if row.closed and row.et == 'b':
            G.add_edge(int(row.bus), int(row.element))
    slack_bus = int(net.ext_grid.bus.iloc[0])
    if slack_bus not in G:
        return set()
    return set(nx.node_connected_component(G, slack_bus))


def has_cycle(net):
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(net.bus.index)
    edges = []
    for _, row in net.line.iterrows():
        if row.in_service:
            edges.append((int(row.from_bus), int(row.to_bus)))
    G.add_edges_from(edges)
    return G.number_of_edges() >= G.number_of_nodes() - nx.number_connected_components(G) + 1 \
        if G.number_of_edges() > 0 else False


def is_radial(net):
    """Check that every connected component of the in-service line graph
    is a tree (no loops) -- distribution feeders must remain radial."""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(net.bus.index)
    for _, row in net.line.iterrows():
        if row.in_service:
            e = (int(row.from_bus), int(row.to_bus))
            if G.has_edge(*e):
                return False  # parallel edge -> immediate loop
            G.add_edge(*e)
    for comp in nx.connected_components(G):
        sub = G.subgraph(comp)
        if sub.number_of_edges() > sub.number_of_nodes() - 1:
            return False
    return True


def try_restoration(base_net, faulted_line, tie_actions):
    """Simulate opening `faulted_line`, then closing the tie lines listed
    in tie_actions (a list of line indices from TIE_LINES). Returns
    (feasible, restored_load_mw, net_after) where feasibility requires
    radiality, power-flow convergence, voltage in [0.9, 1.1] pu, and line
    loading <= 100%."""
    net = copy.deepcopy(base_net)
    net.line.at[faulted_line, 'in_service'] = False
    for t in tie_actions:
        net.line.at[t, 'in_service'] = True

    if not is_radial(net):
        return False, 0.0, net

    try:
        pp.runpp(net, enforce_q_lims=True)
    except Exception:
        return False, 0.0, net

    if not net['converged']:
        return False, 0.0, net

    vmin, vmax = net.res_bus.vm_pu.min(), net.res_bus.vm_pu.max()
    max_loading = net.res_line.loading_percent.max() if len(net.res_line) else 0.0
    energized = energized_buses(net)
    loads = get_load_by_bus(net)
    restored = sum(loads[b] for b in energized)
    total = loads.sum()

    feasible = (vmin >= 0.90) and (vmax <= 1.10) and (max_loading <= 100.0)
    return feasible, restored, net


def total_load(net):
    return get_load_by_bus(net).sum()


def downstream_deenergized_buses(base_net, faulted_line):
    """Buses that lose power purely from the fault, before any restoration."""
    net = copy.deepcopy(base_net)
    net.line.at[faulted_line, 'in_service'] = False
    all_buses = set(net.bus.index)
    return all_buses - energized_buses(net)
