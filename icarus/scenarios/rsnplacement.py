"""Strategies for placing RSN tables in nodes
"""
from __future__ import division
import networkx as nx
from icarus.util import iround
from cacheplacement import uniform_consolidated_cache_placement
from icarus.registry import register_rsn_placement, register_joint_cache_rsn_placement


__all__ = [
    'uniform_consolidated_rsn_placement',
    'cache_all_rsn_all_placement', 
    'cache_all_rsn_high_placement',
    'cache_all_rsn_low_placement',
    'cache_high_rsn_all_placement',
    'cache_high_rsn_high_placement',
    'cache_high_rsn_low_placement',
    'cache_low_rsn_all_placement',
    'cache_low_rsn_high_placement',
    'cache_low_rsn_low_placement',
    'incremental_cache_rsn_placement'
           ]

@register_rsn_placement('CONSOLIDATED')
def uniform_consolidated_rsn_placement(topology, rsn_budget, spread=0.5,
                                       metric_dict=None, target='top',
                                       **kwargs):
    """Consolidate caches in nodes with top centrality.
    
    Differently from other cache placement strategies that place cache space
    to all nodes but proportionally to their centrality, this strategy places
    caches of all the same size in a set of selected nodes.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a cache,
        if it is 0, only the node with the highest/lowest centrality is
        assigned a cache.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    target : ("top" | "bottom"), optional
        The subsection of the ranked node to deploy caches on.
    """
    if spread < 0 or spread > 1:
        raise ValueError('spread factor must be between 0 and 1')
    if target not in ('top', 'bottom'):
        raise ValueError('tagrget argument must be either "top" or "bottom"')
    if metric_dict is None:
        metric_dict = nx.betweenness_centrality(topology)
    
    icr_candidates = topology.graph['icr_candidates']
    nodes = sorted(icr_candidates, key=lambda k: metric_dict[k])
    if target == 'top':
        nodes = list(reversed(nodes))
    # cutoff node must be at least one otherwise, if spread is too low, no
    # nodes would be selected
    cutoff = max(1, iround(spread*len(nodes)))
    target_nodes = nodes[:cutoff]
    rsn_size = iround(rsn_budget/len(target_nodes))
    if rsn_size == 0:
        return
    for v in target_nodes:
        topology.node[v]['stack'][1]['rsn_size'] = rsn_size
        
@register_joint_cache_rsn_placement('CACHE_ALL_RSN_ALL')
def cache_all_rsn_all_placement(topology, cache_budget, rsn_budget, **kwargs):
    """Jointly assign caches and RSN tables to all candidate nodes.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget, spread=1.0)
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=1.0)

@register_joint_cache_rsn_placement('CACHE_ALL_RSN_HIGH')
def cache_all_rsn_high_placement(topology, cache_budget, rsn_budget,
                                 rsn_spread=0.5, metric_dict=None, **kwargs):
    """Jointly assign caches and RSN tables with caches in all candidate nodes
    and RSN tables in nodes with top centralities.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_spread : float [0, 1], optional
        The spread factor. The greater it is the more the RSN budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned an RSN table, if it is 0.5, 50% of candidates are assigned an
        RSN table, if it is 0, only the node with the highest/lowest centrality
        is assigned an RSN table.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=1.0,
                                         metric_dict=metric_dict, target='top')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=rsn_spread,
                                         metric_dict=metric_dict, target='top')



@register_joint_cache_rsn_placement('CACHE_ALL_RSN_LOW')
def cache_all_rsn_low_placement(topology, cache_budget, rsn_budget,
                                 rsn_spread=0.5, metric_dict=None, **kwargs):
    """Jointly assign caches and RSN tables with caches in all candidate nodes
    and RSN tables in nodes with bottom centralities.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_spread : float [0, 1], optional
        The spread factor. The greater it is the more the RSN budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned an RSN table, if it is 0.5, 50% of candidates are assigned an
        RSN table, if it is 0, only the node with the highest/lowest centrality
        is assigned an RSN table.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=1.0,
                                         metric_dict=metric_dict, target='top')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=rsn_spread,
                                         metric_dict=metric_dict, target='bottom')

@register_joint_cache_rsn_placement('CACHE_HIGH_RSN_ALL')
def cache_high_rsn_all_placement(topology, cache_budget, rsn_budget,
                                 cache_spread=0.5, metric_dict=None, **kwargs):
    """Jointly assign caches and RSN tables with caches in nodes with top
    centralities and RSN tables in all candidate nodes.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    cache_spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a
        cache, if it is 0, only the node with the highest/lowest centrality
        is assigned a cache.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=cache_spread,
                                         metric_dict=metric_dict, target='top')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=1.0)
    
@register_joint_cache_rsn_placement('CACHE_HIGH_RSN_HIGH')
def cache_high_rsn_high_placement(topology, cache_budget, rsn_budget,
                                  cache_spread=0.5, rsn_spread=0.5,
                                  metric_dict=None, **kwargs):
    """Jointly assign caches and RSN tables in nodes with top centralities.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    cache_spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a
        cache, if it is 0, only the node with the highest/lowest centrality
        is assigned a cache.
    rsn_spread : float [0, 1], optional
        The spread factor. The greater it is the more the RSN budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned an RSN table, if it is 0.5, 50% of candidates are assigned an
        RSN table, if it is 0, only the node with the highest/lowest centrality
        is assigned an RSN table.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=cache_spread,
                                         metric_dict=metric_dict, target='top')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=rsn_spread,
                                         metric_dict=metric_dict, target='top')

@register_joint_cache_rsn_placement('CACHE_HIGH_RSN_LOW')
def cache_high_rsn_low_placement(topology, cache_budget, rsn_budget,
                                  cache_spread=0.5, rsn_spread=0.5,
                                  metric_dict=None, **kwargs):
    """Jointly assign caches in nodes with top centralities and RSN tables in
    nodes with bottom centralities.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    cache_spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a
        cache, if it is 0, only the node with the highest/lowest centrality
        is assigned a cache.
    rsn_spread : float [0, 1], optional
        The spread factor. The greater it is the more the RSN budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned an RSN table, if it is 0.5, 50% of candidates are assigned an
        RSN table, if it is 0, only the node with the highest/lowest centrality
        is assigned an RSN table.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=cache_spread,
                                         metric_dict=metric_dict, target='top')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=rsn_spread,
                                         metric_dict=metric_dict, target='bottom')

@register_joint_cache_rsn_placement('CACHE_LOW_RSN_ALL')
def cache_low_rsn_all_placement(topology, cache_budget, rsn_budget,
                                 cache_spread=0.5, metric_dict=None, **kwargs):
    """Jointly assign caches and RSN tables with caches in nodes with low
    centralities and RSN tables in all candidate nodes.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    cache_spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a
        cache, if it is 0, only the node with the highest/lowest centrality
        is assigned a cache.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=cache_spread,
                                         metric_dict=metric_dict, target='bottom')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=1.0)
    
@register_joint_cache_rsn_placement('CACHE_LOW_RSN_HIGH')
def cache_low_rsn_high_placement(topology, cache_budget, rsn_budget,
                                  cache_spread=0.5, rsn_spread=0.5,
                                  metric_dict=None, **kwargs):
    """Jointly assign caches in nodes with bottom centralities and RSN tables
    in nodes with top centralities.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    cache_spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a
        cache, if it is 0, only the node with the highest/lowest centrality
        is assigned a cache.
    rsn_spread : float [0, 1], optional
        The spread factor. The greater it is the more the RSN budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned an RSN table, if it is 0.5, 50% of candidates are assigned an
        RSN table, if it is 0, only the node with the highest/lowest centrality
        is assigned an RSN table.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=cache_spread,
                                         metric_dict=metric_dict, target='bottom')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=rsn_spread,
                                         metric_dict=metric_dict, target='top')

@register_joint_cache_rsn_placement('CACHE_LOW_RSN_LOW')
def cache_low_rsn_low_placement(topology, cache_budget, rsn_budget,
                                  cache_spread=0.5, rsn_spread=0.5,
                                  metric_dict=None, **kwargs):
    """Jointly assign caches and RSN tables in nodes with bottom centralities.
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
    cache_spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a
        cache, if it is 0, only the node with the highest/lowest centrality
        is assigned a cache.
    rsn_spread : float [0, 1], optional
        The spread factor. The greater it is the more the RSN budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned an RSN table, if it is 0.5, 50% of candidates are assigned an
        RSN table, if it is 0, only the node with the highest/lowest centrality
        is assigned an RSN table.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=cache_spread,
                                         metric_dict=metric_dict, target='bottom')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=rsn_spread,
                                         metric_dict=metric_dict, target='bottom')


@register_joint_cache_rsn_placement('INCREMENTAL')
def incremental_cache_rsn_placement(topology, cache_budget, rsn_budget,
                                    cache_node_ratio, rsn_node_ratio,
                                    target_cache_spread=0.5, target_rsn_spread=1,
                                    metric_dict=None, **kwargs):
    """Jointly assign caches and RSN tables in nodes with top centralities.
    Differently from other deployment strategies, this strategy allows to
    produce partial deployments, in which only part of the nodes are assigned
    an RSN or a cache with respect to the final deployment objective.
    
    This deployment works as follows. Given target_cache_budget, target_rsn_budget,
    target_cache_spread and target_rsn_spread, a target deployment strategy is
    defined. Now, selecting appropriate values of cache_node_ratio and
    rsn_node_ratio it is possible to select a proportion of nodes of the target
    deployment on which to deploy caches or RSN tables.
    
    For example, if cache_node_ratio = 0.3, then caches are deployed only on
    the top 30% nodes (intended to be caches at completion of deployment)
    ranked by centrality.
    
    Notice that per-node cache and RSN size is fixed, so in partial deployment
    scenarios cache and RSN space is reduced accordingly. So, in the example
    above, the overall cache size would be 30% of the cache_budget.   
    
    Parameters
    ----------
    topology : Topology
        The topology object
    cache_budget : int
        The cumulative cache budget (in number of entries across the network)
        at complete deployment
    rsn_budget : int
        The cumulative cache budget (in number of entries across the network)
        at complete deployment
    cache_spread : float [0, 1], optional
        The spread factor. The greater it is the more the cache budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned a cache, if it is 0.5, 50% of candidates are assigned a
        cache, if it is 0, only the node with the highest/lowest centrality
        is assigned a cache.
    cache_node_ratio: float [0, 1]
        The portion of target caching nodes (with topmost centrality) to
        deploy caches on 
    rsn_node_ratio: float [0, 1]
        The portion of target RSN nodes (with topmost centrality) to deploy
        RSN tables on
    rsn_spread : float [0, 1], optional
        The spread factor. The greater it is the more the RSN budget is
        spread among nodes. For example, if it is 1, all candidate nodes are
        assigned an RSN table, if it is 0.5, 50% of candidates are assigned an
        RSN table, if it is 0, only the node with the highest/lowest centrality
        is assigned an RSN table.
    metric_dict : dict, optional
        A dictionary with the values of the centrality metric according to
        which nodes are selected, keyed by node.
        If not specified, betweenness centrality is used.
    """
    cache_budget = cache_node_ratio * cache_budget
    cache_spread = cache_node_ratio * target_cache_spread
    rsn_budget = rsn_node_ratio * rsn_budget
    rsn_spread = rsn_node_ratio * target_rsn_spread
    uniform_consolidated_cache_placement(topology, cache_budget,
                                         spread=cache_spread,
                                         metric_dict=metric_dict, target='top')
    uniform_consolidated_rsn_placement(topology, rsn_budget, spread=rsn_spread,
                                         metric_dict=metric_dict, target='top')
