# -*- coding: utf-8 -*-
"""This module contains performance metrics loggers
"""
from __future__ import division
import collections
import random

from icarus.registry import register_data_collector
from icarus.tools import cdf
from icarus.util import Tree, inheritdoc

import numpy as np


__all__ = [
    'DataCollector',
    'CollectorProxy',
    'CacheHitRatioCollector',
    'AbsorptionCollector',
    'LinkLoadCollector',
    'LatencyCollector',
    'PathStretchCollector',
    'ControlPlaneCollector',
    'OverheadCollector',
    'TestCollector'
           ]


class DataCollector(object):
    """Object collecting notifications about simulation events and measuring
    relevant metrics.
    """
    
    def __init__(self, view, **params):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            An instance of the network view
        params : keyworded parameters
            Collector parameters
        """
        self.view = view
    
    def start_session(self, timestamp, receiver, content):
        """Notifies the collector that a new network session started.
        
        A session refers to the retrieval of a content from a receiver, from
        the issuing of a content request to the delivery of the content.
        
        Parameters
        ----------
        timestamp : int
            The timestamp of the event
        receiver : any hashable type
            The receiver node requesting a content
        content : any hashable type
            The content identifier requested by the receiver
        """
        pass
    
    def cache_hit(self, node):
        """Reports that the requested content has been served by the cache at
        node *node*.
        
        Parameters
        ----------
        node : any hashable type
            The node whose cache served the content
        """
        pass

    def cache_miss(self, node):
        """Reports that the cache at node *node* has been looked up for 
        requested content but there was a cache miss.
        
        Parameters
        ----------
        node : any hashable type
            The node whose cache served the content
        """
        pass

    def server_hit(self, node):
        """Reports that the requested content has been served by the server at
        node *node*.
        
        Parameters
        ----------
        node : any hashable type
            The server node which served the content
        """
        pass
    
    def request_hop(self, u, v, main_path=True):
        """Reports that a request has traversed the link *(u, v)*
        
        Parameters
        ----------
        u : any hashable type
            Origin node
        v : any hashable type
            Destination node
        main_path : bool
            If True, indicates that link link is on the main path that will
            lead to hit a content. It is normally used to calculate latency
            correctly in multicast cases.
        """
        pass
    
    def content_hop(self, u, v, main_path=True):
        """Reports that a content has traversed the link *(u, v)*
        
        Parameters
        ----------
        u : any hashable type
            Origin node
        v : any hashable type
            Destination node
        main_path : bool
            If True, indicates that this link is being traversed by content
            that will be delivered to the receiver. This is needed to
            calculate latency correctly in multicast cases
        """
        pass
    
    def end_session(self, success=True):
        """Reports that the session is closed, i.e. the content has been
        successfully delivered to the receiver or a failure blocked the 
        execution of the request
        
        Parameters
        ----------
        success : bool, optional
            *True* if the session was completed successfully, *False* otherwise
        """
        pass
    
    def evict_item(self, item):
        """Reports that an item is evicted from a cache
        """
        pass

    def put_item(self, item):
        """Reports that an item is placed in to a cache
        """
        pass

    def results(self):
        """Returns the aggregated results measured by the collector.
        
        Returns
        -------
        results : dict
            Dictionary mapping metric with results.
        """
        pass

# Note: The implementation of CollectorProxy could be improved to avoid having
# to rewrite almost identical methods, for example by playing with __dict__
# attribute. However, it was implemented this way to make it more readable and 
# easier to understand.
class CollectorProxy(DataCollector):
    """This class acts as a proxy for all concrete collectors towards the
    network controller.
    
    An instance of this class registers itself with the network controller and
    it receives notifications for all events. This class is responsible for
    dispatching events of interests to concrete collectors.
    """
    
    EVENTS = ('start_session', 'end_session', 'cache_hit', 'cache_miss', 'server_hit',
              'evict_item', 'put_item', 'request_hop', 'content_hop', 'results')
    
    def __init__(self, view, collectors):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            An instance of the network view
        collector : list of DataCollector
            List of instances of DataCollector that will be notified of events
        """
        self.view = view
        self.collectors = {e: [c for c in collectors if e in type(c).__dict__]
                           for e in self.EVENTS}
    
    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        for c in self.collectors['start_session']:
            c.start_session(timestamp, receiver, content)
    
    @inheritdoc(DataCollector)
    def cache_hit(self, node):
        for c in self.collectors['cache_hit']:
            c.cache_hit(node)

    @inheritdoc(DataCollector)
    def cache_miss(self, node):
        for c in self.collectors['cache_miss']:
            c.cache_miss(node)

    @inheritdoc(DataCollector)
    def server_hit(self, node):
        for c in self.collectors['server_hit']:
            c.server_hit(node)
    
    @inheritdoc(DataCollector)
    def evict_item(self, item):
        for c in self.collectors['evict_item']:
            c.evict_item(item)
    
    @inheritdoc(DataCollector)
    def put_item(self, item):
        for c in self.collectors['put_item']:
            c.put_item(item)

    @inheritdoc(DataCollector)
    def request_hop(self, u, v, main_path=True):
        for c in self.collectors['request_hop']:
            c.request_hop(u, v, main_path)
    
    @inheritdoc(DataCollector)
    def content_hop(self, u, v, main_path=True):
        for c in self.collectors['content_hop']:
            c.content_hop(u, v, main_path)
    
    @inheritdoc(DataCollector)
    def end_session(self, success=True):
        for c in self.collectors['end_session']:
            c.end_session(success)
    
    @inheritdoc(DataCollector)
    def results(self):
        return Tree(**{c.name: c.results() for c in self.collectors['results']})


@register_data_collector('LINK_LOAD')
class LinkLoadCollector(DataCollector):
    """Data collector measuring the link load
    """
    
    def __init__(self, view, sr=10):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            The network view instance
        sr : int
            Size ratio. The average ratio between the size of the content data
            and the request data. For example, if sr = x, then it means that
            the average size of a content is x times the size of a request.
        """
        self.view = view
        self.req_count = collections.defaultdict(int)
        self.cont_count = collections.defaultdict(int)
        if sr <= 0:
            raise ValueError('sr must be positive')
        self.sr = sr
        self.t_start = -1
        self.t_end = 1
    
    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        if self.t_start < 0:
            self.t_start = timestamp
        self.t_end = timestamp
    
    @inheritdoc(DataCollector)
    def request_hop(self, u, v, main_path=True):
        self.req_count[(u, v)] += 1
    
    @inheritdoc(DataCollector)
    def content_hop(self, u, v, main_path=True):
        self.cont_count[(u, v)] += 1
    
    @inheritdoc(DataCollector)
    def results(self):
        duration = self.t_end - self.t_start
        link_loads = dict((link, (self.req_count[link] + self.sr*self.cont_count[link])/duration) 
                          for link in self.req_count)
        link_loads_int = dict((link, load)
                              for link, load in link_loads.iteritems()
                              if self.view.link_type(*link) == 'internal')
        link_loads_ext = dict((link, load)
                              for link, load in link_loads.iteritems()
                              if self.view.link_type(*link) == 'external')
        mean_load_int = sum(link_loads_int.values())/len(link_loads_int)
        mean_load_ext = sum(link_loads_ext.values())/len(link_loads_ext)
        return Tree({'MEAN_INTERNAL':     mean_load_int, 
                     'MEAN_EXTERNAL':     mean_load_ext,
                     'PER_LINK_INTERNAL': link_loads_int,
                     'PER_LINK_EXTERNAL': link_loads_ext})

@register_data_collector('ABS')
class AbsorptionCollector(DataCollector):
    """Data collector measuring the absorption rate and times, 
    i.e., the ratio of the content absorbed (disappeared from the network) 

    """
    def __init__(self, view):
        """Constructor

        Parameters
        ----------
        view : NetworkView
            The network view instance
        """
        self.view = view
        self.absorbtion_times = 0.0
        self.num_absorbed = 0
        self.time = 0.0
        self.content_count = {}
    
    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        self.time = timestamp

    @inheritdoc(DataCollector)
    def put_item(self, item):
        if item not in self.content_count.keys():
            self.content_count[item] = 1
        else:
            self.content_count[item] += 1
        
    @inheritdoc(DataCollector)
    def evict_item(self, item):
        if item in self.content_count.keys():
            self.content_count[item] -= 1
            if self.content_count[item] is 0:
                self.absorbtion_times += self.time
                self.num_absorbed += 1
         
    @inheritdoc(DataCollector)
    def results(self):
        results = Tree(**{'NUM_ABS': self.num_absorbed})
        results['MEAN_ABS_TIME'] = self.absorbtion_times/len(self.content_count.keys())

        return results

@register_data_collector('SAT_RATE')
class SatisfactionRateCollector(DataCollector):
    """Data collector measuring the sat. rate, i.e., the ratio of requests 
    that fetch content.

    """
    def __init__(self, view):
        """Constructor

        Parameters
        ----------
        view : NetworkView
            The network view instance
        """
        self.view = view
        self.sess_count = 0
        self.num_sat_req = 0.0
        self.server_hits = 0.0
        self.cache_hits = 0.0
        self.hit_indicator = False # a cache/server hit occured in a session to only count the first occurence
    
    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        self.hit_indicator = False 
        self.sess_count += 1
    
    @inheritdoc(DataCollector)
    def cache_hit(self, node):
        if self.hit_indicator is False:
            self.hit_indicator = True
            self.num_sat_req += 1
            self.cache_hits += 1

    @inheritdoc(DataCollector)
    def server_hit(self, node):
        if self.hit_indicator is False:
            self.hit_indicator = True
            self.num_sat_req += 1
            self.server_hits += 1
    
    @inheritdoc(DataCollector)
    def results(self):
        sat_rate = self.num_sat_req/self.sess_count
        results = Tree(**{'MEAN': sat_rate})
        results['MEAN_SERVER_HIT'] = self.server_hits/self.sess_count 
        results['MEAN_CACHE_HIT'] = self.cache_hits/self.sess_count

        return results

@register_data_collector('OVERHEAD')
class OverheadCollector(DataCollector):
    """Data collector measuring the overhead, i.e., number of data packets
    forwarded on all links averaged over the number of sessions.
    """

    def __init__(self, view):
        """Constructor

        Parameters
        ----------
        view : NetworkView
            The network view instance
        """
        self.view = view
        self.num_data = 0.0
        self.sess_count = 0
        self.satisfied_conn = 0 # sessions during which content is returned
        self.is_sat = False

    @inheritdoc(DataCollector)
    def content_hop(self, u, v, main_path=True):
        self.num_data += 1
        if self.is_sat is False:
            self.is_sat is True
            self.satisfied_conn += 1
    
    @inheritdoc(DataCollector)
    def cache_hit(self, node):
        if self.is_sat is False:
            self.is_sat is True
            self.satisfied_conn += 1

    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        self.sess_count += 1
        self.is_sat = False
    
    @inheritdoc(DataCollector)
    def results(self):
        results = Tree({'MEAN': self.num_data/self.satisfied_conn})
        
        return results

@register_data_collector('LATENCY')
class LatencyCollector(DataCollector):
    """Data collector measuring latency, i.e. the delay taken to delivery a
    content.
    """
    
    def __init__(self, view, cdf=False):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            The network view instance
        cdf : bool, optional
            If *True*, also collects a cdf of the latency
        """
        self.cdf = cdf
        self.view = view
        self.req_latency = 0.0
        self.sess_count = 0
        self.latency = 0.0
        self.server_latency = 100 # Additional max. latency (penalty) for retrieving content from server 
        self.hit_indicator = False
        self.content_recvd = False # indicator set to True when receiver gets the content
        if cdf:
            self.latency_data = collections.deque()
    
    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        self.receiver = receiver
        self.sess_count += 1
        self.sess_latency = 0.0
        self.hit_indicator = False
        self.content_recvd = False
        self.source = self.view.content_source(content)
    
    @inheritdoc(DataCollector)
    def request_hop(self, u, v, main_path=True):
        if main_path:
            if not self.hit_indicator:
                self.sess_latency += self.view.link_delay(u, v)
    
    @inheritdoc(DataCollector)
    def cache_hit(self, node):
        self.hit_indicator = True

    @inheritdoc(DataCollector)
    def content_hop(self, u, v, main_path=True):
        if not self.content_recvd:
            if u is self.source:
                self.sess_latency += random.random()*self.server_latency
            else:
                self.sess_latency += self.view.link_delay(u, v)
        if v is self.receiver:
            self.content_recvd = True

    @inheritdoc(DataCollector)
    def end_session(self, success=True):
        if not success:
            return
        if self.cdf:
            self.latency_data.append(self.sess_latency)
        self.latency += self.sess_latency
    
    @inheritdoc(DataCollector)
    def results(self):
        results = Tree({'MEAN': self.latency/self.sess_count})
        if self.cdf:
            results['CDF'] = cdf(self.latency_data) 
        return results


@register_data_collector('CACHE_HIT_RATIO')
class CacheHitRatioCollector(DataCollector):
    """Collector measuring the cache hit ratio, i.e. the portion of content
    requests served by a cache.
    """
    
    def __init__(self, view, user_hits = True, off_path_hits=False, per_node=False, content_hits=False):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            The NetworkView instance
        off_path_hits : bool, optional
            If *True* also records cache hits from caches not on located on the
            shortest path. This metric may be relevant only for some strategies
        content_hits : bool, optional
            If *True* also records cache hits per content instead of just
            globally
        """
        self.view = view
        self.user_hits = user_hits
        self.off_path_hits = off_path_hits
        self.per_node = per_node
        self.cont_hits = content_hits
        self.sess_count = 0
        self.cache_hits = 0
        self.serv_hits = 0
        self.hit_indicator = False # To determine a cache hit occured in a session to only count the first occurence
        if off_path_hits:
            self.off_path_hit_count = 0
        if user_hits:
            self.num_user_hits = 0
        if per_node:
            self.per_node_cache_hits = collections.defaultdict(int)
            self.per_node_server_hits = collections.defaultdict(int)
        if content_hits:
            self.curr_cont = None
            self.cont_cache_hits = collections.defaultdict(int)
            self.cont_serv_hits = collections.defaultdict(int)

    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        self.hit_indicator = False 
        self.sess_count += 1
        if self.off_path_hits:
            source = self.view.content_source(content)
            self.curr_path = self.view.shortest_path(receiver, source)
        if self.cont_hits:
            self.curr_cont = content
    
    @inheritdoc(DataCollector)
    def cache_hit(self, node):
        if self.hit_indicator is False:
            self.hit_indicator = True
            self.cache_hits += 1
            if self.user_hits:
                if node in self.view.topology().receivers():
                    self.num_user_hits += 1
            if self.off_path_hits and node not in self.curr_path:
                self.off_path_hit_count += 1
            if self.cont_hits:
                self.cont_cache_hits[self.curr_cont] += 1
            if self.per_node:
                self.per_node_cache_hits[node] += 1

    @inheritdoc(DataCollector)
    def server_hit(self, node):
        self.serv_hits += 1
        if self.cont_hits:
            self.cont_serv_hits[self.curr_cont] += 1
        if self.per_node:
            self.per_node_server_hits[node] += 1
    
    @inheritdoc(DataCollector)
    def results(self):
        n_sess = self.cache_hits + self.serv_hits
        hit_ratio = self.cache_hits/self.sess_count 
        results = Tree(**{'MEAN': hit_ratio})
        if self.off_path_hits:
            results['MEAN_OFF_PATH'] = self.off_path_hit_count/n_sess
            results['MEAN_ON_PATH'] = results['MEAN'] - results['MEAN_OFF_PATH']
        if self.cont_hits:
            cont_set = set(self.cont_cache_hits.keys() + self.cont_serv_hits.keys())
            cont_hits=dict((self.cont_cache_hits[i]/(self.cont_cache_hits[i] + self.cont_serv_hits[i])) 
                            for i in cont_set)
            results['PER_CONTENT'] = cont_hits
        if self.user_hits:
            results['MEAN_USER_HITS'] = (1.0*self.num_user_hits)/self.sess_count
            results['MEAN_NETWORK_HITS'] = (1.0*(self.cache_hits-self.num_user_hits))/self.sess_count
        if self.per_node:
            for v in self.per_node_cache_hits:
                self.per_node_cache_hits[v] /= n_sess
            for v in self.per_node_server_hits:
                self.per_node_server_hits[v] /= n_sess    
            results['PER_NODE_CACHE_HIT_RATIO'] = self.per_node_cache_hits
            results['PER_NODE_SERVER_HIT_RATIO'] = self.per_node_server_hits
        return results

@register_data_collector('PATH_STRETCH')
class PathStretchCollector(DataCollector):
    """Collector measuring the path stretch, i.e. the ratio between the actual
    path length and the shortest path length.
    """
    
    def __init__(self, view, cdf=False):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            The network view instance
        cdf : bool, optional
            If *True*, also collects a cdf of the path stretch
        """
        self.view = view
        self.cdf = cdf
        self.req_path_len = collections.defaultdict(int)
        self.cont_path_len = collections.defaultdict(int)
        self.sess_count = 0
        self.mean_req_stretch = 0.0
        self.mean_cont_stretch = 0.0
        self.mean_stretch = 0.0
        if self.cdf:
            self.req_stretch_data = collections.deque()
            self.cont_stretch_data = collections.deque()
            self.stretch_data = collections.deque()
    
    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        self.receiver = receiver
        self.source = self.view.content_source(content)
        self.req_path_len = 0
        self.cont_path_len = 0
        self.sess_count += 1

    @inheritdoc(DataCollector)
    def request_hop(self, u, v, main_path=True):
        self.req_path_len += 1
    
    @inheritdoc(DataCollector)
    def content_hop(self, u, v, main_path=True):
        self.cont_path_len += 1
    
    @inheritdoc(DataCollector)
    def end_session(self, success=True):
        if not success:
            return
        req_sp_len = len(self.view.shortest_path(self.receiver, self.source))
        cont_sp_len = len(self.view.shortest_path(self.source, self.receiver))
        req_stretch = self.req_path_len/req_sp_len
        cont_stretch = self.cont_path_len/cont_sp_len
        stretch = (self.req_path_len + self.cont_path_len)/(req_sp_len + cont_sp_len)
        self.mean_req_stretch += req_stretch
        self.mean_cont_stretch += cont_stretch
        self.mean_stretch += stretch
        if self.cdf:
            self.req_stretch_data.append(req_stretch)
            self.cont_stretch_data.append(cont_stretch)
            self.stretch_data.append(stretch)
            
    @inheritdoc(DataCollector)
    def results(self):
        results = Tree({'MEAN': self.mean_stretch/self.sess_count,
                        'MEAN_REQUEST': self.mean_req_stretch/self.sess_count,
                        'MEAN_CONTENT': self.mean_cont_stretch/self.sess_count})
        if self.cdf:
            results['CDF'] = cdf(self.stretch_data)
            results['CDF_REQUEST'] = cdf(self.req_stretch_data)
            results['CDF_CONTENT'] = cdf(self.cont_stretch_data)
        return results
    

@register_data_collector('CONTROL_PLANE')
class ControlPlaneCollector(DataCollector):
    """Collector measuring various performance metrics of the control plane.
    
    In particular this collector analyzes overheads of various routing tables.
    """
    
    def __init__(self, view, t_poll=1000, cdf=True):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            The network view instance
        """
        self.view = view
        self.t_poll = t_poll
        self.cdf = cdf
        self.sess_count = 1
        self.rsn_hit_ratio = [collections.deque() for _ in range(4)]


    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        if self.sess_count % self.t_poll == 0:
            # Inspect RSN freshness
            hit_ratio = np.zeros(4)
            # number of RSN tables used, i.e. on nodes traversed by traffic
            n_active_rsn = 0
            for rsn_node in self.view.rsn_nodes():
                rsn_dump = self.view.rsn_dump(rsn_node)
                per_node_hits = np.zeros(4)
                for content, next_hop in rsn_dump:
                    if self.view.cache_lookup(rsn_node, content):
                        per_node_hits[0] += 1
                    elif self.view.cache_lookup(next_hop, content):
                        per_node_hits[1] += 1
                    else:
                        next_hop = self.view.rsn_lookup(next_hop, content)
                        if next_hop is not None:
                            if self.view.cache_lookup(next_hop, content):
                                per_node_hits[2] += 1
                            else:
                                next_hop = self.view.rsn_lookup(next_hop, content)
                                if next_hop is not None:
                                    if self.view.cache_lookup(next_hop, content):
                                        per_node_hits[3] += 1
                # at this stage I have the number of hits coming from 1, 2 or 3 hops away
                # if the node investigated had an RSN with at least one entry
                if len(rsn_dump) > 0:
                    n_active_rsn += 1
                    hit_ratio += per_node_hits/len(rsn_dump)
            for i in range(4):
                rsn_hit_ratio = hit_ratio[i]/n_active_rsn if n_active_rsn > 0 else 0
                self.rsn_hit_ratio[i].append(rsn_hit_ratio)
        self.sess_count += 1

            
    @inheritdoc(DataCollector)
    def results(self):
        results = Tree({
           'MEAN_RSN_ZERO_HOP':     np.mean(self.rsn_hit_ratio[0]),
           'MEAN_RSN_ONE_HOP':      np.mean(self.rsn_hit_ratio[1]),
           'MEAN_RSN_TWO_HOP':      np.mean(self.rsn_hit_ratio[2]),
           'MEAN_RSN_THREE_HOP':    np.mean(self.rsn_hit_ratio[3]),
                  })
        results['MEAN_RSN_ALL'] = results['MEAN_RSN_ZERO_HOP'] + \
                                  results['MEAN_RSN_ONE_HOP'] + \
                                  results['MEAN_RSN_TWO_HOP'] + \
                                  results['MEAN_RSN_THREE_HOP']  
        if self.cdf:
            results.update({
               'CDF_RSN_ZERO_HOP':      cdf(self.rsn_hit_ratio[0]),
               'CDF_RSN_ONE_HOP':       cdf(self.rsn_hit_ratio[1]),
               'CDF_RSN_TWO_HOP':       cdf(self.rsn_hit_ratio[2]),
               'CDF_RSN_THREE_HOP':     cdf(self.rsn_hit_ratio[3]),
                           })
        return results
    

@register_data_collector('TEST')
class TestCollector(DataCollector):
    """Collector used for test cases only.
    """
    
    def __init__(self, view):
        """Constructor
        
        Parameters
        ----------
        view : NetworkView
            The network view instance
        output : stream
            Stream on which debug collector writes
        """
        self.view = view
    
    @inheritdoc(DataCollector)
    def start_session(self, timestamp, receiver, content):
        self.session = dict(timestamp=timestamp, receiver=receiver,
                            content=content, cache_misses=[],
                            request_hops=[], content_hops=[])

    @inheritdoc(DataCollector)
    def cache_hit(self, node):
        self.session['serving_node'] = node
    
    @inheritdoc(DataCollector)
    def cache_miss(self, node):
        self.session['cache_misses'].append(node)

    @inheritdoc(DataCollector)
    def server_hit(self, node):
        self.session['serving_node'] = node

    @inheritdoc(DataCollector)
    def request_hop(self, u, v, main_path=True):
        self.session['request_hops'].append((u, v))
    
    @inheritdoc(DataCollector)
    def content_hop(self, u, v, main_path=True):
        self.session['content_hops'].append((u, v))
    
    @inheritdoc(DataCollector)
    def end_session(self, success=True):
        self.session['success'] = success
    
    def session_summary(self):
        """Return a summary of latest session
        
        Returns
        -------
        session : dict
            Summary of session
        """
        return self.session

    
