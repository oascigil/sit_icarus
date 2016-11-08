# -*- coding: utf-8 -*-
"""Traffic workloads

Every traffic workload to be used with Icarus must be modelled as an iterable
class, i.e. a class with at least an __init__ method (through which it is
initialized, with values taken from the configuration file) and an __iter__
method that is called to return a new event.

Each workload must expose the 'contents' attribute which is an iterable of
all content identifiers. This is need for content placement
"""
import random
import csv

import networkx as nx

from icarus.tools import TruncatedZipfDist
from icarus.registry import register_workload

__all__ = [
        'StationarySitWorkload',
        'StationaryWorkload',
        'GlobetraffWorkload',
        'TraceDrivenWorkload'
           ]

@register_workload('STATIONARY_SIT')
class StationarySitWorkload(object):
    """This function is adapted to work for the SIT experiments. The only 
    difference from STATIONARY is that it generated disconnection events after
    a specified amount of warm-up time interval.
"""
    def __init__(self, topology, n_contents, alpha, beta=0, rate=12.0,
                    n_warmup=10**5, n_measured=4*10**5, seed=None, disconnection_rate=1.0, **kwargs):
        if alpha < 0:
            raise ValueError('alpha must be positive')
        if beta < 0:
            raise ValueError('beta must be positive')
        self.receivers = [v for v in topology.nodes_iter()
                     if topology.node[v]['stack'][0] == 'receiver']
        self.zipf = TruncatedZipfDist(alpha, n_contents)
        self.n_contents = n_contents
        self.contents = range(1, n_contents + 1)
        self.n_connected = 0
        num_receviers = len(topology.receivers())
        # Variable to keep track of connections for each receiver:
        self.connections = [dict() for x in range(num_receviers)]
        # Variable to keep track of the requested content during warmup (to print info)
        self.requested_content = {}
        self.receivers_list = list(topology.receivers())
        self.alpha = alpha
        self.rate = rate
        self.n_warmup = n_warmup
        self.n_measured = n_measured
        random.seed(seed)
        self.beta = beta
        self.disconnection_rate = disconnection_rate
        if beta != 0:
            degree = nx.degree(topology)
            self.receivers = sorted(self.receivers, key=lambda x: degree[iter(topology.edge[x]).next()], reverse=False)
            self.receiver_dist = TruncatedZipfDist(beta, len(self.receivers))
        
    def __iter__(self):
        req_counter = 0
        t_event = 0.0
        # Initialization (i.e., warmup) period:
        while req_counter < self.n_warmup:
            t_event += (random.expovariate(self.rate))
            if self.beta == 0:
                receiver = random.choice(self.receivers)
            else:
                receiver = self.receivers[self.receiver_dist.rv()-1]
        
            content = int(self.zipf.rv())
            self.requested_content[content] = True
            log = (req_counter >= self.n_warmup)
            event = {'receiver': receiver, 'content': content, 'log': log}
            yield (t_event, event)
            req_counter += 1
            self.n_connected += 1

            # Keep track of connections
            receiver_index = self.receivers_list.index(receiver)
            receiver_conns = self.connections[receiver_index]
            if content in receiver_conns.keys():
                receiver_conns[content] += 1
            else: 
                receiver_conns[content] = 1

        t_disconnect = t_event
        print "The number of content requested during warmup is " + repr(len(self.requested_content.keys())) + " for zipf parameter: " + repr(self.alpha)

        while req_counter < self.n_warmup + self.n_measured:
            t_event += (random.expovariate(self.rate))
            
            while t_disconnect < t_event and self.n_connected > 0:
                if self.beta == 0:
                    receiver = random.choice(self.receivers)
                else:
                    receiver = self.receivers[self.receiver_dist.rv()-1]
                content = -1
                log = (req_counter >= self.n_warmup)
                event = {'receiver': receiver, 'content': content, 'log': log, 'connections': self.connections}
                yield (t_event, event)
                t_disconnect += random.expovariate(self.disconnection_rate*self.n_connected)
                self.n_connected -= 1

            if self.beta == 0:
                receiver = random.choice(self.receivers)
            else:
                receiver = self.receivers[self.receiver_dist.rv()-1]
            content = int(self.zipf.rv())
            log = (req_counter >= self.n_warmup)
            event = {'receiver': receiver, 'content': content, 'log': log, 'connections': self.connections}
            self.n_connected += 1
            yield (t_event, event)
            # Keep track of connections
            receiver_index = self.receivers_list.index(receiver)
            receiver_conns = self.connections[receiver_index]
            if content in receiver_conns.keys():
                receiver_conns[content] += 1
            else: 
                receiver_conns[content] = 1
            req_counter += 1

        raise StopIteration()

@register_workload('STATIONARY')
class StationaryWorkload(object):
    """This function generates events on the fly, i.e. instead of creating an 
    event schedule to be kept in memory, returns an iterator that generates
    events when needed.
    
    This is useful for running large schedules of events where RAM is limited
    as its memory impact is considerably lower.
    
    These requests are Poisson-distributed while content popularity is
    Zipf-distributed
    
    All requests are mapped to receivers uniformly unless a positive *beta*
    parameter is specified.
    
    If a *beta* parameter is specified, then receivers issue requests at
    different rates. The algorithm used to determine the requests rates for 
    each receiver is the following:
     * All receiver are sorted in decreasing (ONUR: increasing) order of degree of the PoP they
       are attached to. This assumes that all receivers have degree = 1 and are
       attached to a node with degree > 1
     * Rates are then assigned following a Zipf distribution of coefficient
       beta where nodes with higher-degree (ONUR: lower-degree) PoPs have a higher request rate 
    
    Parameters
    ----------
    topology : fnss.Topology
        The topology to which the workload refers
    n_contents : int
        The number of content object
    alpha : float
        The Zipf alpha parameter
    beta : float
        Parameter indicating
    rate : float
        The mean rate of requests per second
    n_warmup : int
        The number of warmup requests (i.e. requests executed to fill cache but
        not logged)
    n_measured : int
        The number of logged requests after the warmup
    
    Returns
    -------
    events : iterator
        Iterator of events. Each event is a 2-tuple where the first element is
        the timestamp at which the event occurs and the second element is a
        dictionary of event attributes.
    """
    def __init__(self, topology, n_contents, alpha, beta=0, rate=12.0,
                    n_warmup=10**5, n_measured=4*10**5, seed=None, **kwargs):
        if alpha < 0:
            raise ValueError('alpha must be positive')
        if beta < 0:
            raise ValueError('beta must be positive')
        self.receivers = [v for v in topology.nodes_iter()
                     if topology.node[v]['stack'][0] == 'receiver']
        self.zipf = TruncatedZipfDist(alpha, n_contents)
        self.n_contents = n_contents
        self.contents = range(1, n_contents + 1)
        self.alpha = alpha
        self.rate = rate
        self.n_warmup = n_warmup
        self.n_measured = n_measured
        random.seed(seed)
        self.beta = beta
        if beta != 0:
            degree = nx.degree(topology)
            self.receivers = sorted(self.receivers, key=lambda x: degree[iter(topology.edge[x]).next()], reverse=False)
            self.receiver_dist = TruncatedZipfDist(beta, len(self.receivers))
        
    def __iter__(self):
        req_counter = 0
        t_event = 0.0
        while req_counter < self.n_warmup + self.n_measured:
            t_event += (random.expovariate(self.rate))
            if self.beta == 0:
                receiver = random.choice(self.receivers)
            else:
                receiver = self.receivers[self.receiver_dist.rv()-1]
            content = int(self.zipf.rv())
            log = (req_counter >= self.n_warmup)
            event = {'receiver': receiver, 'content': content, 'log': log}
            yield (t_event, event)
            req_counter += 1
        raise StopIteration()


@register_workload('GLOBETRAFF')
class GlobetraffWorkload(object):
    """Parse requests from GlobeTraff workload generator
    
    All requests are mapped to receivers uniformly unless a positive *beta*
    parameter is specified.
    
    If a *beta* parameter is specified, then receivers issue requests at
    different rates. The algorithm used to determine the requests rates for 
    each receiver is the following:
     * All receiver are sorted in decreasing order of degree of the PoP they
       are attached to. This assumes that all receivers have degree = 1 and are
       attached to a node with degree > 1
     * Rates are then assigned following a Zipf distribution of coefficient
       beta where nodes with higher-degree PoPs have a higher request rate 
    
    Parameters
    ----------
    topology : fnss.Topology
        The topology to which the workload refers
    content_file : str
        The GlobeTraff content file
    request_file : str
        The GlobeTraff request file
        
    Returns
    -------
    events : iterator
        Iterator of events. Each event is a 2-tuple where the first element is
        the timestamp at which the event occurs and the second element is a
        dictionary of event attributes.
    """
    
    def __init__(self, topology, content_file, request_file, beta=0, **kwargs):
        """Constructor"""
        if beta < 0:
            raise ValueError('beta must be positive')
        self.receivers = [v for v in topology.nodes_iter() 
                     if topology.node[v]['stack'][0] == 'receiver']
        self.n_contents = 0
        with open(content_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for content, popularity, size, app_type in reader:
                self.n_contents = max(self.n_contents, content)
        self.n_contents += 1
        self.contents = range(self.n_contents)
        self.request_file = request_file
        self.beta = beta
        if beta != 0:
            degree = nx.degree(self.topology)
            self.receivers = sorted(self.receivers, key=lambda x: 
                                    degree[iter(topology.edge[x]).next()], 
                                    reverse=True)
            self.receiver_dist = TruncatedZipfDist(beta, len(self.receivers))
        
    def __iter__(self):
        with open(self.request_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for timestamp, content, size in reader:
                if self.beta == 0:
                    receiver = random.choice(self.receivers)
                else:
                    receiver = self.receivers[self.receiver_dist.rv()-1]
                event = {'receiver': receiver, 'content': content, 'size': size}
                yield (timestamp, event)
        raise StopIteration()

@register_workload('TRACE_DRIVEN')
class TraceDrivenWorkload(object):
    """Parse requests from a generic request trace.
    
    This workload requires two text files:
     * a requests file, where each line corresponds to a string identifying
       the content requested
     * a contents file, which lists all unique content identifiers appearing
       in the requests file.
       
    Since the trace do not provide timestamps, requests are scheduled according
    to a Poisson process of rate *rate*. All requests are mapped to receivers
    uniformly unless a positive *beta* parameter is specified.
    
    If a *beta* parameter is specified, then receivers issue requests at
    different rates. The algorithm used to determine the requests rates for 
    each receiver is the following:
     * All receiver are sorted in decreasing order of degree of the PoP they
       are attached to. This assumes that all receivers have degree = 1 and are
       attached to a node with degree > 1
     * Rates are then assigned following a Zipf distribution of coefficient
       beta where nodes with higher-degree PoPs have a higher request rate 
        
    Parameters
    ----------
    topology : fnss.Topology
        The topology to which the workload refers
    reqs_file : str
        The path to the requests file
    contents_file : str
        The path to the contents file
    n_contents : int
        The number of content object (i.e. the number of lines of contents_file)
    n_warmup : int
        The number of warmup requests (i.e. requests executed to fill cache but
        not logged)
    n_measured : int
        The number of logged requests after the warmup
    rate : float
        The network-wide mean rate of requests per second
    beta : float
        Spatial skewness of requests rates
        
    Returns
    -------
    events : iterator
        Iterator of events. Each event is a 2-tuple where the first element is
        the timestamp at which the event occurs and the second element is a
        dictionary of event attributes.
    """
    def __init__(self, topology, reqs_file, contents_file, n_contents,
                 n_warmup, n_measured, rate=12.0, beta=0, **kwargs):
        """Constructor"""
        if beta < 0:
            raise ValueError('beta must be positive')
        
        self.buffering = 64*1024*1024 # Set high buffering to avoid one-line reads
        self.n_contents = n_contents
        self.n_warmup = n_warmup
        self.n_measured = n_measured
        self.reqs_file = reqs_file
        self.rate = rate
        self.receivers = [v for v in topology.nodes_iter() 
                          if topology.node[v]['stack'][0] == 'receiver']
        self.contents = []
        with open(contents_file, 'r', buffering=self.buffering) as f:
            for content in f:
                self.contents.append(content)
        self.beta = beta
        if beta != 0:
            degree = nx.degree(topology)
            self.receivers = sorted(self.receivers, key=lambda x:
                                    degree[iter(topology.edge[x]).next()],
                                    reverse=True)
            self.receiver_dist = TruncatedZipfDist(beta, len(self.receivers))
        
    def __iter__(self):
        req_counter = 0
        t_event = 0.0
        with open(self.reqs_file, 'r', buffering=self.buffering) as f:
            for content in f:
                t_event += (random.expovariate(self.rate))
                if self.beta == 0:
                    receiver = random.choice(self.receivers)
                else:
                    receiver = self.receivers[self.receiver_dist.rv()-1]
                log = (req_counter >= self.n_warmup)
                event = {'receiver': receiver, 'content': content, 'log': log}
                yield (t_event, event)
                req_counter += 1
                if(req_counter >= self.n_warmup + self.n_measured):
                    raise StopIteration()
            raise ValueError("Trace did not contain enough requests")
