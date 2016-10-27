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
N_PROCESSES = cpu_count()/2

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = 'OBJECT'

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported 
RESULTS_FORMAT = 'PICKLE'

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 1

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icaurs/execution/collectors.py
DATA_COLLECTORS = ['ABS', 'CACHE_HIT_RATIO', 'OVERHEAD']

# Strategy that will be executed during warm-up phase
WARMUP_STRATEGY = 'NDN'

#Probability of caching
CACHING_PROBABILITY = 0.1

# This is a base experiment configuration with all the parameters that won't
# change across experiments of the same campaign
base = Tree()
base['network_model'] = Tree()
base['desc'] = "Base experiment"    # Description shown during execution

# Default experiment parameters
CACHE_POLICY = 'LRU'
# Alpha determines content selection (Zipf parameter)
ALPHA = 0.7
# Beta determines the zipf parameter determining how sources are selected
BETA = 0.9
# Number of content objects
N_CONTENTS = 10**4
# Number of content requests generated to prepopulate the caches
# These requests are not logged
N_WARMUP = 60*60*10 # 60 minutes
# Number of content requests generated after the warmup and logged
# to generate results. 
N_MEASURED = 3*60*60*10 # three hours
# Number of requests per second (over the whole network)
REQ_RATE = 10

# Limit of scope for scoped flooding 
SCOPE_LIMIT = 2
# Cache storage size of the entire network (routers) in terms of percentage of content population
NETWORK_CACHE = 0.90 # 0.01
# Rate of disconnections per user (e.g., 0.01 means each user stays in the network for 100 secs on average)
DISCONNECTION_RATE = 0.0025
TOPOLOGY = 3257
RSN_CACHE_RATIO = 64

default = Tree()
default['workload'] = {
    'name':      'STATIONARY_SIT',
    'alpha':      ALPHA,
    'n_contents': N_CONTENTS,
    'n_warmup':   N_WARMUP,
    'n_measured': N_MEASURED,
    'rate':       REQ_RATE,
    'disconnection_rate': 0.01
    # 'beta':       BETA
                       }
default['content_placement']['name'] = 'UNIFORM'
default['cache_policy']['name'] = CACHE_POLICY

# Instantiate experiment queue
EXPERIMENT_QUEUE = deque()

# C-FIB size sensitivity

base = copy.deepcopy(default)
# Total size of network cache as a fraction of content population
base['topology']['name'] = 'ROCKET_FUEL'
base['topology']['source_ratio'] = 1.0
base['topology']['ext_delay'] = 2 # 34
base['topology']['asn'] = TOPOLOGY 
base['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
base['joint_cache_rsn_placement'] = {'network_cache': NETWORK_CACHE}
base['joint_cache_rsn_placement']['rsn_cache_ratio'] = RSN_CACHE_RATIO
base['joint_cache_rsn_placement']['network_rsn'] = RSN_CACHE_RATIO * NETWORK_CACHE
base['warmup_strategy']['name'] = WARMUP_STRATEGY
base['warmup_strategy']['p'] = CACHING_PROBABILITY

"""
1. Cache hit (Satisfaction) rate for different probability
"""

# First Experiments 
for strategy in ['NDN_SIT']:
    for caching_probability in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        experiment = copy.deepcopy(base)
        experiment['workload'] = {
            'name':      'STATIONARY_SIT',
            'alpha':      ALPHA,
            'n_contents': N_CONTENTS,
            'n_warmup':   N_WARMUP,
            'n_measured': N_MEASURED,
            'rate':       REQ_RATE,
            'disconnection_rate': DISCONNECTION_RATE
        }
        experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
        experiment['strategy']['name'] = strategy
        experiment['strategy']['p'] = caching_probability 
        experiment['desc'] = "strategy: %s caching probability: %s" % (str(strategy), str(caching_probability))
        EXPERIMENT_QUEUE.append(experiment)

# First Experiments 
for strategy in ['SIT_ONLY']:
    for fan_out in [1, 100]: # ONE and ALL strategies
       for caching_probability in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      ALPHA,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': DISCONNECTION_RATE
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['strategy']['name'] = strategy
            experiment['strategy']['p'] = caching_probability 
            experiment['strategy']['fan_out'] = fan_out
            experiment['desc'] = "strategy: %s caching probability: %s" % (str(strategy), str(caching_probability))
            EXPERIMENT_QUEUE.append(experiment)

# First Experiments 
for strategy in ['SIT_WITH_SCOPED_FLOODING']:
    for fan_out in [1, 100]: # ONE and ALL strategies
        for scope in [1, 2]:
            for caching_probability in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                experiment = copy.deepcopy(base)
                experiment['workload'] = {
                    'name':      'STATIONARY_SIT',
                    'alpha':      ALPHA,
                    'n_contents': N_CONTENTS,
                    'n_warmup':   N_WARMUP,
                    'n_measured': N_MEASURED,
                    'rate':       REQ_RATE,
                    'disconnection_rate': DISCONNECTION_RATE
                }
                experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
                experiment['topology']['asn'] = TOPOLOGY 
                experiment['strategy']['name'] = strategy
                experiment['strategy']['fan_out'] = fan_out
                experiment['strategy']['scope'] = scope
                experiment['strategy']['p'] = caching_probability 
                experiment['desc'] = "strategy: %s caching probability: %s" % (str(strategy), str(caching_probability))
                EXPERIMENT_QUEUE.append(experiment)

# First Experiments 
for strategy in ['SCOPED_FLOODING']:
    for scope in [1, 2, 100]:
        for caching_probability in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      ALPHA,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': DISCONNECTION_RATE
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['topology']['asn'] = TOPOLOGY 
            experiment['strategy']['name'] = strategy
            experiment['strategy']['scope'] = scope
            experiment['strategy']['p'] = caching_probability 
            experiment['desc'] = "strategy: %s caching probability: %s" % (str(strategy), str(caching_probability))
            EXPERIMENT_QUEUE.append(experiment)


"""
2. The impact of the cache capacity of each router in the performance of the examined resilience strategies.
"""

"""
for strategy in ['NDN_SIT']:
    for network_cache in [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5]:
        experiment = copy.deepcopy(base)
        experiment['workload'] = {
            'name':      'STATIONARY_SIT',
            'alpha':      ALPHA,
            'n_contents': N_CONTENTS,
            'n_warmup':   N_WARMUP,
            'n_measured': N_MEASURED,
            'rate':       REQ_RATE,
            'disconnection_rate': DISCONNECTION_RATE
        }
        experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
        experiment['strategy']['name'] = strategy
        experiment['joint_cache_rsn_placement'] = {'network_cache': network_cache}
        experiment['joint_cache_rsn_placement']['network_rsn'] = RSN_CACHE_RATIO* network_cache  
        experiment['desc'] = "strategy: %s network_cache: %s" % (str(strategy), str(network_cache))
        EXPERIMENT_QUEUE.append(experiment)

# Second experiments
for strategy in ['SIT_ONLY']:
    for fan_out in [1, 100]: # ONE and ALL strategies
        for network_cache in [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5]:
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      ALPHA,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': DISCONNECTION_RATE
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['strategy']['name'] = strategy
            experiment['strategy']['fan_out'] = fan_out
            experiment['joint_cache_rsn_placement'] = {'network_cache': network_cache}
            experiment['joint_cache_rsn_placement']['network_rsn'] = RSN_CACHE_RATIO* network_cache  
            experiment['desc'] = "strategy: %s network_cache: %s" % (str(strategy), str(network_cache))
            EXPERIMENT_QUEUE.append(experiment)

# Second experiments
for strategy in ['SIT_WITH_SCOPED_FLOODING']:
    for network_cache in [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5]:
        for fan_out in [1, 100]: # ONE and ALL strategies
            for scope in [1, 2]:
                experiment = copy.deepcopy(base)
                experiment['workload'] = {
                    'name':      'STATIONARY_SIT',
                    'alpha':      ALPHA,
                    'n_contents': N_CONTENTS,
                    'n_warmup':   N_WARMUP,
                    'n_measured': N_MEASURED,
                    'rate':       REQ_RATE,
                    'disconnection_rate': DISCONNECTION_RATE
                }
                experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
                experiment['strategy']['name'] = strategy
                experiment['strategy']['fan_out'] = fan_out
                experiment['strategy']['scope'] = scope
                experiment['joint_cache_rsn_placement'] = {'network_cache': network_cache}
                experiment['joint_cache_rsn_placement']['network_rsn'] = RSN_CACHE_RATIO* network_cache  
                experiment['desc'] = "strategy: %s network_cache: %s" % (str(strategy), str(network_cache))
                EXPERIMENT_QUEUE.append(experiment)

# Second experiments
for strategy in ['SCOPED_FLOODING']:
    for network_cache in [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5]:
        for scope in [1, 2, 100]: 
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      ALPHA,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': DISCONNECTION_RATE
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['strategy']['name'] = strategy
            experiment['strategy']['scope'] = scope
            experiment['joint_cache_rsn_placement'] = {'network_cache': network_cache}
            experiment['joint_cache_rsn_placement']['network_rsn'] = RSN_CACHE_RATIO* network_cache  
            experiment['desc'] = "strategy: %s network_cache: %s" % (str(strategy), str(network_cache))
            EXPERIMENT_QUEUE.append(experiment)
"""


"""
3. The impact of the disconnection rate of the users in the performance of the examined resilience strategies
"""

"""
for strategy in ['NDN_SIT']:
    for disconnection_rate in [0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.05]:
        experiment = copy.deepcopy(base)
        experiment['workload'] = {
            'name':      'STATIONARY_SIT',
            'alpha':      ALPHA,
            'n_contents': N_CONTENTS,
            'n_warmup':   N_WARMUP,
            'n_measured': N_MEASURED,
            'rate':       REQ_RATE,
            'disconnection_rate': disconnection_rate
        }
        experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
        experiment['strategy']['name'] = strategy
        experiment['desc'] = "strategy: %s disconnection rate: %s" % (str(strategy), str(disconnection_rate))
        EXPERIMENT_QUEUE.append(experiment)

# Third Experiments
for strategy in ['SIT_ONLY']:
    for fan_out in [1, 100]: # ONE and ALL strategies
        for disconnection_rate in [0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.05]:
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      ALPHA,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': disconnection_rate
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['strategy']['name'] = strategy
            experiment['strategy']['fan_out'] = fan_out
            experiment['desc'] = "strategy: %s disconnection rate: %s fan_out: %s" % (str(strategy), str(disconnection_rate), str(fan_out))
            EXPERIMENT_QUEUE.append(experiment)

# Third Experiments
for strategy in ['SIT_WITH_SCOPED_FLOODING']:
    for disconnection_rate in [0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.05]:
        for fan_out in [1, 100]: # ONE and ALL strategies
            for scope in [1, 2]:
                experiment = copy.deepcopy(base)
                experiment['workload'] = {
                    'name':      'STATIONARY_SIT',
                    'alpha':      ALPHA,
                    'n_contents': N_CONTENTS,
                    'n_warmup':   N_WARMUP,
                    'n_measured': N_MEASURED,
                    'rate':       REQ_RATE,
                    'disconnection_rate': disconnection_rate
                }
                experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
                experiment['strategy']['name'] = strategy
                experiment['strategy']['fan_out'] = fan_out
                experiment['strategy']['scope'] = scope
                experiment['desc'] = "strategy: %s disconnection rate: %s fan_out: %s, scope: %s" % (str(strategy), str(disconnection_rate), str(fan_out), str(scope))
                EXPERIMENT_QUEUE.append(experiment)

# Third Experiments
for strategy in ['SCOPED_FLOODING']:
    for disconnection_rate in [0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.05]:
        for scope in [1, 2, 100]:
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      ALPHA,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': disconnection_rate
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['strategy']['name'] = strategy
            experiment['strategy']['scope'] = scope
            experiment['desc'] = "strategy: %s disconnection rate: %s scope: %s" % (str(strategy), str(disconnection_rate), str(fan_out), str(scope))
            EXPERIMENT_QUEUE.append(experiment)

"""


"""
4. The impact of the popularity distribution in the performance of the examined resilience strategies.
"""
"""
# Fourth Experiments
for strategy in ['NDN_SIT']:
    for alpha in [0.00001, 0.5, 0.7, 1.0, 0.5, 1.0, 1.5, 2.0]:
        experiment = copy.deepcopy(base)
        experiment['workload'] = {
            'name':      'STATIONARY_SIT',
            'alpha':      alpha,
            'n_contents': N_CONTENTS,
            'n_warmup':   N_WARMUP,
            'n_measured': N_MEASURED,
            'rate':       REQ_RATE,
            'disconnection_rate': DISCONNECTION_RATE
        }
        experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
        experiment['strategy']['name'] = strategy
        experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = RSN_CACHE_RATIO
        experiment['desc'] = "strategy: %s alpha: %s" % (str(strategy), str(alpha))
        EXPERIMENT_QUEUE.append(experiment)

# Fourth Experiments
for strategy in ['SIT_ONLY']:
    for fan_out in [1, 100]: # ONE and ALL strategies
        for alpha in [0.00001, 0.5, 0.7, 1.0, 0.5, 1.0, 1.5, 2.0]:
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      alpha,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': DISCONNECTION_RATE
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['strategy']['name'] = strategy
            experiment['strategy']['fan_out'] = fan_out
            experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = RSN_CACHE_RATIO
            experiment['desc'] = "strategy: %s alpha: %s" % (str(strategy), str(alpha))
            EXPERIMENT_QUEUE.append(experiment)

# Fourth Experiments
for strategy in ['SIT_WITH_SCOPED_FLOODING']:
    for fan_out in [1, 100]: # ONE and ALL strategies
        for scope in [1, 2]:
            for alpha in [0.00001, 0.5, 0.7, 1.0, 0.5, 1.0, 1.5, 2.0]:
                experiment = copy.deepcopy(base)
                experiment['workload'] = {
                    'name':      'STATIONARY_SIT',
                    'alpha':      alpha,
                    'n_contents': N_CONTENTS,
                    'n_warmup':   N_WARMUP,
                    'n_measured': N_MEASURED,
                    'rate':       REQ_RATE,
                    'disconnection_rate': DISCONNECTION_RATE
                }
                experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
                experiment['strategy']['name'] = strategy
                experiment['strategy']['fan_out'] = fan_out
                experiment['strategy']['scope'] = scope
                experiment['joint_cache_rsn_placement']['network_rsn'] = RSN_CACHE_RATIO* network_cache  
                experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = RSN_CACHE_RATIO
                experiment['desc'] = "strategy: %s alpha: %s" % (str(strategy), str(alpha))
                EXPERIMENT_QUEUE.append(experiment)

# Fourth Experiments
for strategy in ['SCOPED_FLOODING']:
    for scope in [1, 2, 100]:
        for alpha in [0.00001, 0.5, 0.7, 1.0, 0.5, 1.0, 1.5, 2.0]:
            experiment = copy.deepcopy(base)
            experiment['workload'] = {
                'name':      'STATIONARY_SIT',
                'alpha':      alpha,
                'n_contents': N_CONTENTS,
                'n_warmup':   N_WARMUP,
                'n_measured': N_MEASURED,
                'rate':       REQ_RATE,
                'disconnection_rate': DISCONNECTION_RATE
            }
            experiment['joint_cache_rsn_placement']['name'] = 'CACHE_ALL_RSN_ALL_SIT'
            experiment['strategy']['name'] = strategy
            experiment['strategy']['scope'] = scope
            experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = RSN_CACHE_RATIO
            experiment['desc'] = "strategy: %s caching probability: %s" % (str(strategy), str(alpha))
            EXPERIMENT_QUEUE.append(experiment)
"""
