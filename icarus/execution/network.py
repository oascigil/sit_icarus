# -*- coding: utf-8 -*-
"""Network Model-View-Controller (MVC)
"""
import logging

import networkx as nx
import fnss

from icarus.registry import CACHE_POLICY
from icarus.models import keyval_cache
from icarus.util import path_links

__all__ = [
    'NetworkModel',
    'NetworkView',
    'NetworkController'
          ]

logger = logging.getLogger('orchestration')

def symmetrify_paths(shortest_paths):
    for u in shortest_paths:
        for v in shortest_paths[u]:
            shortest_paths[u][v] = list(reversed(shortest_paths[v][u]))
    return shortest_paths

class NetworkView(object):
    
    def __init__(self, model):
        """Constructor
        
        Parameters
        ----------
        model : NetworkModel
            The network model instance
        """
        if not isinstance(model, NetworkModel):
            raise ValueError('The model argument must be an instance of '
                             'NetworkModel')
        self.model = model
    
    def content_locations(self, k):
        """Return a set of all current locations of a specific content.
        
        This include both persistent content sources and temporary caches. 
        
        Parameters
        ----------
        k : any hashable type
            The content identifier
        
        Returns
        -------
        nodes : set
            A set of all nodes currently storing the given content
        """
        loc = set(v for v in self.model.cache if self.model.cache[v].has(k))
        loc.add(self.content_source(k))
        return loc
    
    def content_source(self, k):
        """Return the node identifier where the content is persistently stored.
        
        Parameters
        ----------
        k : any hashable type
            The content identifier
        
        Returns
        -------
        node : any hashable type
            The node persistently storing the given content
        """
        return self.model.content_source[k]
        
    def shortest_path(self, s, t):
        """Return the shortest path from *s* to *t*
        
        Parameters
        ----------
        s : any hashable type
            Origin node
        t : any hashable type
            Destination node
        
        Returns
        -------
        shortest_path : list
            List of nodes of the shortest path (origin and destination
            included)
        """
        return self.model.shortest_path[s][t]
    
    def all_pairs_shortest_paths(self):
        """Return all pairs shortest paths
        
        Return
        ------
        all_pairs_shortest_paths : dict of lists
            Shortest paths between all pairs
        """
        return self.model.shortest_path

    def link_type(self, u, v):
        """Return the type of link *(u, v)*.
        
        Type can be either *internal* or *external*
        
        Parameters
        ----------
        u : any hashable type
            Origin node
        v : any hashable type
            Destination node
        
        Returns
        -------
        link_type : str
            The link type
        """
        return self.model.link_type[(u, v)]
    
    def link_delay(self, u, v):
        """Return the delay of link *(u, v)*.
        
        Parameters
        ----------
        u : any hashable type
            Origin node
        v : any hashable type
            Destination node
        
        Returns
        -------
        delay : float
            The link delay
        """
        return self.model.link_delay[(u, v)]
    
    def topology(self):
        """Return the network topology
        
        Returns
        -------
        topology : fnss.Topology
            The topology object
        
        Notes
        -----
        The topology object returned by this method must not be modified by the
        caller. This object can only be modified through the NetworkController.
        Changes to this object will lead to inconsistent network state.
        """
        return self.model.topology

    def cache_nodes(self, size=False):
        """Returns a list of nodes with caching capability
        
        Parameters
        ----------
        size: bool, opt
            If *True* return dict mapping nodes with size
        
        Returns
        -------
        cache_nodes : list or dict
            If size parameter is False or not specified, it is a list of nodes
            with caches. Otherwise it is a dict mapping nodes with a cache
            and their size.
        """
        return self.model.cache_size if size else list(self.model.cache_size.keys())
    
    def has_cache(self, node):
        """Check if a node has a content cache.
        
        Parameters
        ----------
        node : any hashable type
            The node identifier
            
        Returns
        -------
        has_cache : bool,
            *True* if the node has a cache, *False* otherwise
        """
        return node in self.model.cache

    def cache_lookup(self, node, content):
        """Check if the cache of a node has a content object, without changing
        the internal state of the cache.
        
        This method is meant to be used by data collectors to calculate
        metrics. It should not be used by strategies to look up for contents
        during the simulation. Instead they should use
        NetworkController.get_content
        
        Parameters
        ----------
        node : any hashable type
            The node identifier
        content : any hashable type
            The content identifier
            
        Returns
        -------
        has_content : bool
            *True* if the cache of the node has the content, *False* otherwise.
            If the node does not have a cache, return *None*
        """
        if node in self.model.cache:
            return self.model.cache[node].has(content)

    def cache_dump(self, node):
        """Returns the dump of the content of a cache in a specific node
        
        Parameters
        ----------
        node : any hashable type
            The node identifier
            
        Returns
        -------
        dump : list
            List of contents currently in the cache
        """
        if node in self.model.cache:
            return self.model.cache[node].dump()

    def rsn_nodes(self, size=False):
        """Returns a list of nodes with an RSN table
        
        Parameters
        ----------
        size: bool, opt
            If *True* return dict mapping nodes with size
                
        Returns
        -------
        rsn_nodes : list or dict
            If size parameter is False or not specified, it is a list of nodes
            with RSN tables. Otherwise it is a dict mapping nodes with an RSN
            table and their size.
        """
        return self.model.rsn_size if size else list(self.model.rsn_size.keys())
    
    def has_rsn_table(self, node):
        """Check if a node has an RSN table
        
        Parameters
        ----------
        node : any hashable type
            The node identifier
            
        Returns
        -------
        has_rsn_table : bool,
            *True* if the node has an RSN table, *False* otherwise
        """
        return node in self.model.rsn
    
    def rsn_lookup(self, node, content):
        """Check if the RSN table of a node has a content object, without
        changing the internal state of the table.
        
        This method is meant to be used by data collectors to calculate
        metrics. It should not be used by strategies to look up for entries
        during the simulation. Instead they should use
        NetworkController.get_rsn
        
        Parameters
        ----------
        node : any hashable type
            The node identifier
        content : any hashable type
            The content identifier
            
        Returns
        -------
        has_cache : bool,
            *True* if the node has a cache, *False* otherwise
        """
        if node in self.model.rsn:
            return self.model.rsn[node].value(content)
    
    def rsn_dump(self, node):
        """Returns the dump of the content of the RSN table in a specific node
        
        Parameters
        ----------
        node : any hashable type
            The node identifier
            
        Returns
        -------
        dump : list
            List of entries currently in the RSN
        """
        if node in self.model.rsn:
            return self.model.rsn[node].dump()
        

class NetworkModel(object):
    """Models the internal state of the network
    """
    
    def __init__(self, topology, cache_policy, shortest_path=None):
        """Constructors
        
        Parameters
        ----------
        topology : fnss.Topology
            The topology object
        cache_policy : dict or Tree
            cache policy descriptor. It has the name attribute which identify
            the cache policy name and keyworded arguments specific to the
            policy
        shortest_path : dict of dict, optional
            The all-pair shortest paths of the network
        """
        # Filter inputs
        if not isinstance(topology, fnss.Topology):
            raise ValueError('The topology argument must be an instance of '
                             'fnss.Topology or any of its subclasses.')
        
        # Shortest paths of the network
        self.shortest_path = shortest_path if shortest_path is not None \
                             else symmetrify_paths(nx.all_pairs_dijkstra_path(topology))
        
        # Network topology
        self.topology = topology
        
        # Dictionary mapping each content object to its source
        # dict of location of contents keyed by content ID
        self.content_source = {}
        
        # Dictionary of cache sizes keyed by node
        self.cache_size = {}
        
        # Dictionary of RSN table sizes keyed by node
        self.rsn_size = {}
        
        # Dictionary of link types (internal/external)
        self.link_type = nx.get_edge_attributes(topology, 'type')
        self.link_delay = fnss.get_delays(topology)
        # Instead of this manual assignment, I could have converted the
        # topology to directed before extracting type and link delay but that
        # requires a deep copy of the topology that can take long time if
        # many content source mappings are included in the topology
        if not topology.is_directed():
            for (u, v), link_type in self.link_type.items():
                self.link_type[(v, u)] = link_type
            for (u, v), delay in self.link_delay.items():
                self.link_delay[(v, u)] = delay
                
        # Initialize attributes
        receiver_cache_size = 0
        for node in topology.nodes_iter():
            stack_name, stack_props = fnss.get_stack(topology, node)
            if stack_name == 'router':
                if 'cache_size' in stack_props:
                    self.cache_size[node] = stack_props['cache_size']
                if 'rsn_size' in stack_props:
                    self.rsn_size[node] = stack_props['rsn_size']
            elif stack_name == 'source':
            # Onur: adding the following check and indent the following 3 lines after if
                if 'contents' in stack_props:
                    contents = stack_props['contents']
                    for content in contents:
                        self.content_source[content] = node
            # Onur:
            elif stack_name == 'receiver':
                if 'cache_size' in stack_props:
                    receiver_cache_size = stack_props['cache_size']
                    self.cache_size[node] = stack_props['cache_size']
            #
        if receiver_cache_size == 0:
            print "Receiver has no cache"
        else:
            print "Receiver cache size is set to ", receiver_cache_size
        if any(c < 1 for c in self.cache_size.values()):
            logger.warn('Some content caches have size equal to 0. '
                          'I am setting them to 1 and run the experiment anyway')
            for node in self.cache_size:
                if self.cache_size[node] < 1:    
                    self.cache_size[node] = 1
        if any(c < 1 for c in self.rsn_size.values()):
            logger.warn('Some RSN tables have size equal to 0. '
                          'I am setting them to 1 and run the experiment anyway')
            for node in self.rsn_size:
                if self.rsn_size[node] < 1:    
                    self.rsn_size[node] = 1
                    
        policy_name = cache_policy['name']
        policy_args = {k: v for k, v in cache_policy.items() if k != 'name'}
        # The actual cache and RSN objects storing the content

        self.cache = {node: CACHE_POLICY[policy_name](self.cache_size[node], **policy_args)
                          for node in self.cache_size}
        
        # RSN and cache must have the same cache eviction policy
        self.rsn = {node: keyval_cache(CACHE_POLICY[policy_name](size, **policy_args))
                        for node, size in self.rsn_size.iteritems()}



class NetworkController(object):
    """Network controller"""
    
    def __init__(self, model):
        """Constructor
        
        Parameters
        ----------
        model : NetworkModel
            Instance of the network model
        """
        self.session = None
        self.model = model
        self.collector = None
    
    def attach_collector(self, collector):
        """Attaches a data collector to which all events will be reported.
        
        Parameters
        ----------
        collector : DataCollector
            The data collector
        """
        self.collector = collector
        
    def detach_collector(self):
        """Detaches the data collector.
        """
        self.collector = None
    
    def start_session(self, timestamp, receiver, content, log, counts=None):
        """Instruct the controller to start a new session (i.e. the retrieval
        of a content).
        
        Parameters
        ----------
        timestamp : int
            The timestamp of the event
        receiver : any hashable type
            The receiver node requesting a content
        content : any hashable type
            The content identifier requested by the receiver
        log : bool
            *True* if this session needs to be reported to the collector,
            *False* otherwise
        """
        self.session = dict(timestamp=timestamp,
                            receiver=receiver,
                            content=content,
                            log=log)
        if counts is None and self.collector is not None and self.session['log']:
            self.collector.start_session(timestamp, receiver, content)
        elif self.collector is not None and self.session['log']:
            self.collector.start_session(timestamp, receiver, content, counts) 
    
    def forward_request_path(self, s, t, path=None, main_path=True):
        """Forward a request from node *s* to node *t* over the provided path.
                
        Parameters
        ----------
        s : any hashable type
            Origin node
        t : any hashable type
            Destination node
        path : list, optional
            The path to use. If not provided, shortest path is used
        """
        if path is None:
            path = self.model.shortest_path[s][t]
        for u, v in path_links(path):
            self.forward_request_hop(u, v)
    
    def forward_content_path(self, u, v, path=None, main_path=True):
        """Forward a content from node *s* to node *t* over the provided path.
                
        Parameters
        ----------
        s : any hashable type
            Origin node
        t : any hashable type
            Destination node
        path : list, optional
            The path to use. If not provided, shortest path is used
        """
        if path is None:
            path = self.model.shortest_path[u][v]
        for u, v in path_links(path):
            self.forward_content_hop(u, v)
    
    def forward_request_hop(self, u, v, main_path=True):
        """Forward a request over link  u -> v.
                
        Parameters
        ----------
        u : any hashable type
            Origin node
        v : any hashable type
            Destination node
        """
        if self.collector is not None and self.session['log']:
            self.collector.request_hop(u, v, main_path)
    
    def forward_content_hop(self, u, v, main_path=True):
        """Forward a content over link  u -> v.
                
        Parameters
        ----------
        u : any hashable type
            Origin node
        v : any hashable type
            Destination node
        """
        if self.collector is not None and self.session['log']:
            self.collector.content_hop(u, v, main_path)
    
    def put_content(self, node):
        """Store content in the specified node.
        
        The node must have a cache stack and the actual insertion of the
        content is executed according to the caching policy. If the caching
        policy has a selective insertion policy, then content may not be
        inserted.
        
        Parameters
        ----------
        node : any hashable type
            The node where the content is inserted
            
        Returns
        -------
        evicted : any hashable type
            The evicted object or *None* if no contents were evicted.
        """
        if node in self.model.cache:
            # if self.session['log']: ONUR: do not check this condition so that 
            # we can report put_item events to the collector during warmup phase
            if not self.model.cache[node].has(self.session['content']) and self.session['log']:
                self.collector.put_item(self.session['content'])

            item = self.model.cache[node].put(self.session['content'])

            if item is not None and self.session['log']:
                self.collector.evict_item(item)

        return item

    def has_content(self, node):
        """Check if the node has the content in its cache or if it is serving.
        Onur: This has the same functionality as the get_content with the exception 
        of reporting to the collector. This is used for warm up strategies to avoid 
        reporting.

        Parameters
        ----------
        node : any hashable type
            The node where the content is retrieved
        
        Returns
        -------
        content : bool
            True if the content is available, False otherwise
        """
        if node in self.model.cache:
            cache_hit = self.model.cache[node].get(self.session['content'])
            if cache_hit:
                if self.session['log']:
                    self.collector.cache_hit(node)
            else:
                if self.session['log']:
                    self.collector.cache_miss(node)
            return cache_hit
        name, props = fnss.get_stack(self.model.topology, node)
        if name == 'source' and self.session['content'] in props['contents']:
            if self.collector is not None and self.session['log']:
                self.collector.server_hit(node)
            return True
        else:
            return False

    def get_content(self, node):
        """Get a content from a server or a cache.

        Parameters
        ----------
        node : any hashable type
            The node where the content is retrieved
        
        Returns
        -------
        content : bool
            True if the content is available, False otherwise
        """
        if node in self.model.cache:
            cache_hit = self.model.cache[node].get(self.session['content'])
            if cache_hit:
                if self.session['log']:
                    self.collector.cache_hit(node)
            else:
                if self.session['log']:
                    self.collector.cache_miss(node)
            return cache_hit
        name, props = fnss.get_stack(self.model.topology, node)
        if name == 'source' and self.session['content'] in props['contents']:
            if self.collector is not None and self.session['log']:
                self.collector.server_hit(node)
            return True
        else:
            return False

    # Onur: added the following method to be able to remove a given content from a given node's cache
    def remove_content_at_node(self, content, node):
        """Remove the content being handled from the cache
        
        Parameters
        ----------
        content : content identifier 
        node : any hashable type
            The node where the cached content is removed

        Returns
        -------
        removed : bool
            *True* if the entry was in the cache, *False* if it was not.
        """

        item = self.model.cache[node].remove(content)

        if self.collector is not None and self.session['log']:
            self.collector.evict_item(content)
        else:
            print "ERROR: in remove_content_at_node, this should not happen!"
            
        return item

    def remove_content(self, node):
        """Remove the content being handled from the cache
        
        Parameters
        ----------
        node : any hashable type
            The node where the cached content is removed

        Returns
        -------
        removed : bool
            *True* if the entry was in the cache, *False* if it was not.
        """
        if node in self.model.cache:
            return self.model.cache[node].remove(self.session['content'])

    def put_rsn(self, node, next_hop, content=None):
        """Store forwarding information in the Recently Served Name (RSN) table
        of the specified node.
        
        The node must have a cache stack and the actual insertion of the
        content is executed according to the caching policy. If the caching
        policy has a selective insertion policy, then content may not be
        inserted.
        
        Parameters
        ----------
        node : any hashable type
            The node where the entry is inserted
        next_hop : any hashable type
            The node towards which the content is forwarded
        content : any hashable type
            The content identifier to insert in the entry. If not specified
            the content being transferred in the session is used
        
        Returns
        -------
        evicted : any hashable type
            The evicted item or *None* if no contents were evicted.
        """
        if node in self.model.rsn:
            content = self.session['content'] if content is None else content
            return self.model.rsn[node].put(content, next_hop)
    
    def get_rsn(self, node, content=None):
        """Get an RSN entry of the content being handled from a given node.

        Parameters
        ----------
        node : any hashable type
            The node where the RSN entry is retrieved
        content : any hashable type
            The content identifier to retrieve. If not specified
            the content being transferred in the session is used
            
        Returns
        -------
        next_hop : any hashable type
            The node towards which the content was forwarded, if in the RSN,
            otherwise *None*
        """
        if node in self.model.rsn:
            content = self.session['content'] if content is None else content
            return self.model.rsn[node].get(content)

    def invalidate_trail(self, trail, content=None):
        """Remove a trail consisting of RSN state at multiple nodes

        Parameters
        ----------
        trail : a list consisting of current and next-hop node identifiers
                a trail must have at least two nodes: originating node and the 
                first-hop off-path router
        """
        content = self.session['content'] if content is None else content
        for hop in range(0, len(trail)-1):
            curr_hop = trail[hop]
            next_hop = trail[hop+1]
            if curr_hop in self.model.rsn:
                rsn_entry = self.model.rsn[curr_hop].value(content)
                if rsn_entry is None:
                    raise ValueError("invalidate_trail: cannot invalidate None")
                else:
                    rsn_entry.delete_nexthop(next_hop)
                    # Remove the RSN entry from the table if there are no nexthops 
                    if not len(rsn_entry.nexthops):
                        self.model.rsn[curr_hop].remove(content)
                        #self.remove_rsn(curr_hopm content)

    def remove_rsn(self, node, content=None):
        """Remove the content being handled from the RSN table
        
        Parameters
        ----------
        node : any hashable type
            The node where the RSN entry is removed

        Returns
        -------
        removed : bool
            *True* if the entry was in the cache, *False* if it was not.
        """
        if node in self.model.rsn:
            content = self.session['content'] if content is None else content
            return self.model.rsn[node].remove(content)

    def end_session(self, success=True):
        """Close a session
        
        Parameters
        ----------
        success : bool, optional
            *True* if the session was completed successfully, *False* otherwise
        """
        if self.collector is not None and self.session['log']:
            self.collector.end_session(success)
        self.session = None

    def remove_link(self, u, v):
        raise NotImplementedError('Method not yet implemented')

    def restore_link(self, u, v):
        raise NotImplementedError('Method not yet implemented')
    
    def remove_node(self, v):
        raise NotImplementedError('Method not yet implemented')
    
    def restore_node(self, v):
        raise NotImplementedError('Method not yet implemented')
    

