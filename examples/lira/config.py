# -*- coding: utf-8 -*-
"""This module contains all configuration information used to run simulations
"""
from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

# GENERAL SETTINGS

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = 'OBJECT'

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported 
RESULTS_FORMAT = 'PICKLE'

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 3

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icaurs/execution/collectors.py
DATA_COLLECTORS = ['CONTROL_PLANE', 'CACHE_HIT_RATIO', 'LATENCY']


# This is a base experiment configuration with all the parameters that won't
# change across experiments of the same campaign
base = Tree()
base['network_model'] = Tree()
base['desc'] = "Base experiment"    # Description shown during execution

# Default experiment parameters
CACHE_POLICY = 'LRU'
ALPHA = 0.8
N_CONTENTS = 3*10**5
N_WARMUP = 2*10**5
N_MEASURED = 4*10**5
REQ_RATE = 12

N_CONTENTS = 3*10
N_WARMUP = 2*10**2
N_MEASURED = 4*10**2
REQ_RATE = 10

default = Tree()
default['workload'] = {
    'name':      'STATIONARY',
    'alpha':      ALPHA,
    'n_contents': N_CONTENTS,
    'n_warmup':   N_WARMUP,
    'n_measured': N_MEASURED,
    'rate':       REQ_RATE
                       }
default['content_placement']['name'] = 'UNIFORM'
default['cache_policy']['name'] = CACHE_POLICY

# Instantiate experiment queue
EXPERIMENT_QUEUE = deque()

# C-FIB size sensitivity
base = copy.deepcopy(default)
network_cache = 0.95
base['topology']['name'] = 'ROCKET_FUEL'
base['topology']['source_ratio'] = 0.1
base['topology']['ext_delay'] = 34
base['joint_cache_rsn_placement'] = {'network_cache': network_cache}
for joint_cache_rsn_placement in ['CACHE_HIGH_RSN_HIGH', 'CACHE_HIGH_RSN_ALL', 'CACHE_ALL_RSN_HIGH', 'CACHE_ALL_RSN_ALL']:
    for asn in [1221, 1239, 1755, 3257, 3967,  6461]:
        for rsn_cache_ratio in [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]:
            for strategy in ['LIRA_LCE', 'LIRA_CHOICE']:
                experiment = copy.deepcopy(base)
                experiment['topology']['asn'] = asn
                experiment['strategy']['name'] = strategy
                experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
                experiment['joint_cache_rsn_placement']['network_rsn'] = rsn_cache_ratio * network_cache
                experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = rsn_cache_ratio
                experiment['desc'] = "RSN size sensitivity -> RSN/cache ratio: %s" % str(rsn_cache_ratio)
                EXPERIMENT_QUEUE.append(experiment)
 
# CCN comparison
# Let's assume that each cache entry corresponds, in size to 30 RSN entries
# Gradually remove some cache entries and replace them with an equal amount of
# memory in C-FIB entries
base = copy.deepcopy(default)
network_cache = 0.01
base['topology']['name'] = 'ROCKET_FUEL'
base['topology']['source_ratio'] = 0.1
base['topology']['ext_delay'] = 34
for joint_cache_rsn_placement in ['CACHE_ALL_RSN_HIGH']: # ['CACHE_HIGH_RSN_HIGH', 'CACHE_HIGH_RSN_ALL', 'CACHE_ALL_RSN_HIGH', 'CACHE_ALL_RSN_ALL']:
    for asn in [1221, 1239, 1755, 3257, 3967,  6461]:
        for network_cache, network_rsn in [(0.02, 0), (0.0195, 0.15), (0.019, 0.30), (0.0185, 0.45), (0.018, 0.60), (0.0175, 0.75), (0.0170, 0.90)]:
            for strategy in ['LIRA_LCE', 'LIRA_CHOICE']:
                experiment = copy.deepcopy(base)
                experiment['topology']['asn'] = asn
                experiment['strategy']['name'] = strategy
                experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
                experiment['joint_cache_rsn_placement']['network_cache'] = network_cache
                experiment['joint_cache_rsn_placement']['network_rsn'] = network_rsn
                experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = network_rsn/network_cache
                experiment['desc'] = "RSN size sensitivity -> RSN: %s, cache: %s " % (str(network_rsn), str(network_cache))
                EXPERIMENT_QUEUE.append(experiment)


# Incremental deployment experiment
base = copy.deepcopy(default)
base['topology']['name'] = 'ROCKET_FUEL'
base['topology']['source_ratio'] = 0.1
base['topology']['ext_delay'] = 34
base['joint_cache_rsn_placement'] = {'name': 'INCREMENTAL',
                                     'network_cache': 0.01,
                                     'network_rsn': 0.16}
for rsn_node_ratio in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, \
                       0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]:
    for cache_node_ratio in [0.25, 0.50, 0.75, 1.0]:
        for asn in [1221, 6461]: #[1221, 1239, 1755, 3257, 3967,  6461]:
            for strategy in ['LIRA_CHOICE']:
                experiment = copy.deepcopy(base)
                experiment['topology']['asn'] = asn
                experiment['strategy']['name'] = strategy
                experiment['joint_cache_rsn_placement']['cache_node_ratio'] = cache_node_ratio
                experiment['joint_cache_rsn_placement']['rsn_node_ratio'] = rsn_node_ratio
                experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = rsn_node_ratio/cache_node_ratio
                experiment['desc'] = "Incremental deployment -> cache node ratio: %s, RSN node ratio: %s" % (str(cache_node_ratio), str(rsn_node_ratio))
                EXPERIMENT_QUEUE.append(experiment)
 

# Cache deployment strategies
base = copy.deepcopy(default)
base['joint_cache_rsn_placement'] = {'network_cache': 0.01,
                                     'network_rsn': 0.01}
base['topology']['name'] = 'ROCKET_FUEL'
base['topology']['source_ratio'] = 0.1
base['topology']['ext_delay'] = 34
for joint_cache_rsn_placement in ['CACHE_HIGH_RSN_HIGH', 'CACHE_HIGH_RSN_ALL', 'CACHE_ALL_RSN_HIGH', 'CACHE_ALL_RSN_ALL']:
    for strategy in ['LIRA_LCE', 'LIRA_CHOICE']:
        for asn in [1221, 1239, 1755, 3257, 3967,  6461]:
            experiment = copy.deepcopy(base)
            experiment['topology']['asn'] = asn
            experiment['strategy']['name'] = strategy
            experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
            experiment['desc'] = "Deployment strategies -> deployment: %s, topology: %s, strategy: %s" % (joint_cache_rsn_placement, asn, strategy)
            EXPERIMENT_QUEUE.append(experiment)
