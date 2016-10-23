"""Generate LIRA multicast results"""

from __future__ import division

import networkx as nx
import fnss
import icarus


def avg_cfib_distance(topology, node_ratio, sp=None):
    """Return average distance between a receiver and a C-FIB node over all
    receiver-source pairs of the topology.
    """
    if sp is None:
        sp = nx.all_pairs_dijkstra_path(topology)
    centr = nx.betweenness_centrality(topology, weight='weight')
    icr_candidates = topology.graph['icr_candidates']
    rsn_nodes = sorted(icr_candidates, key=lambda x: centr[x], reverse=True)
    rsn_nodes = set(rsn_nodes[:int(node_ratio*len(icr_candidates))])
    
    sources = topology.sources()
    receivers = topology.receivers()
    
    dist = 0
    for r in receivers:
        for s in sources:
            for i, v in enumerate(sp[r][s]):
                if v in rsn_nodes:
                    dist += i
                    break
            else:
                dist += i
    
    return dist/(len(receivers)*len(sources))

def main():
    asn_list = [1221, 1239, 1755, 3257, 3967,  6461]
    node_ratios = [i/20 for i in range(21)]
    rs = icarus.results.ResultSet()
    print("asn,ratio,hops")
    for asn in asn_list:
        topology = icarus.scenarios.topology_generic_rocketfuel_latency(asn, 0.1, 34)
        sp = nx.all_pairs_dijkstra_path(topology)
        for node_ratio in node_ratios:
            avg_hops = avg_cfib_distance(topology, node_ratio, sp)
            rs.add({'asn': asn, 'node_ratio': node_ratio}, {'avg_hops': avg_hops})
            print("%d,%f,%f" % (asn, node_ratio, avg_hops))
    icarus.results.write_results_pickle(rs, 'multicast.pickle')

if __name__ == '__main__':
    main()