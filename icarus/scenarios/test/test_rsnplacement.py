import sys
if sys.version_info[:2] >= (2, 7):
    import unittest
else:
    try:
        import unittest2 as unittest
    except ImportError:
        raise ImportError("The unittest2 package is needed to run the tests.") 
del sys
import fnss

import icarus.scenarios as rsnplacement

def small_line_topology():
    topology = fnss.line_topology(7)
    fnss.add_stack(topology, 0, 'receiver')
    fnss.add_stack(topology, 1, 'router')
    fnss.add_stack(topology, 2, 'router')
    fnss.add_stack(topology, 3, 'router')
    fnss.add_stack(topology, 4, 'router')
    fnss.add_stack(topology, 5, 'router')
    fnss.add_stack(topology, 6, 'source')
    topology.graph['icr_candidates'] = [2, 3]
    return topology

def large_line_topology():
    topology = fnss.line_topology(11)
    fnss.add_stack(topology, 0, 'receiver')
    for i in range(1, 10):
        fnss.add_stack(topology, i, 'router')
    topology.graph['icr_candidates'] = [2, 3, 4, 5]
    return topology

class TestIncremental(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass    
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cache_all_rsn_all(self):
        topology = small_line_topology()
        rsnplacement.cache_all_rsn_all_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {2: 20, 3: 20})
        self.assertEqual(rsn_size, {2: 20, 3: 20})

    def test_cache_all_rsn_high(self):
        topology = small_line_topology()
        rsnplacement.cache_all_rsn_high_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {2: 20, 3: 20})
        self.assertEqual(rsn_size, {3: 40})

    def test_cache_all_rsn_low(self):
        topology = small_line_topology()
        rsnplacement.cache_all_rsn_low_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {2: 20, 3: 20})
        self.assertEqual(rsn_size, {2: 40})

    def test_cache_high_rsn_all(self):
        topology = small_line_topology()
        rsnplacement.cache_high_rsn_all_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {3: 40})
        self.assertEqual(rsn_size, {2: 20, 3: 20})
        
    def test_cache_high_rsn_high(self):
        topology = small_line_topology()
        rsnplacement.cache_high_rsn_high_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {3: 40})
        self.assertEqual(rsn_size, {3: 40})
        
    def test_cache_high_rsn_low(self):
        topology = small_line_topology()
        rsnplacement.cache_high_rsn_low_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {3: 40})
        self.assertEqual(rsn_size, {2: 40})

    def test_cache_low_rsn_all(self):
        topology = small_line_topology()
        rsnplacement.cache_low_rsn_all_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {2: 40})
        self.assertEqual(rsn_size, {2: 20, 3: 20})
        
    def test_cache_low_rsn_high(self):
        topology = small_line_topology()
        rsnplacement.cache_low_rsn_high_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {2: 40})
        self.assertEqual(rsn_size, {3: 40})
        
    def test_cache_low_rsn_low(self):
        topology = small_line_topology()
        rsnplacement.cache_low_rsn_low_placement(topology, 40, 40)
        cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'cache_size' in topology.node[v]['stack'][1]}
        rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                      for v in topology.nodes()
                      if 'stack' in topology.node[v] and
                      'rsn_size' in topology.node[v]['stack'][1]}
        self.assertEqual(cache_size, {2: 40})
        self.assertEqual(rsn_size, {2: 40})

    def test_incremental(self):
        # Dict mapping (cache_node_ratio, rsn_node_ratio) : (cache_depl, rsn_depl)
        cache_deployment = {0: {}, 0.5: {5: 30}, 1.0: {5: 30, 4: 30}}
        rsn_deployment = {0: {}, 0.25: {5: 15}, 0.5: {5: 15, 4: 15},
                          0.75: {5: 15, 4: 15, 3: 15},
                          1: {5: 15, 4: 15, 3: 15, 2: 15}}
        for cache_node_ratio, expected_caches in cache_deployment.items():
            for rsn_node_ratio, expected_rsn in rsn_deployment.items():
                topology = large_line_topology()
                rsnplacement.incremental_cache_rsn_placement(topology,
                                                             cache_budget=60,
                                                             rsn_budget=60, 
                                                             cache_node_ratio=cache_node_ratio,
                                                             rsn_node_ratio=rsn_node_ratio
                                                             )
                cache_size = {v: topology.node[v]['stack'][1]['cache_size']
                              for v in topology.nodes()
                              if 'stack' in topology.node[v] and
                              'cache_size' in topology.node[v]['stack'][1]}
                rsn_size = {v: topology.node[v]['stack'][1]['rsn_size']
                              for v in topology.nodes()
                              if 'stack' in topology.node[v] and
                              'rsn_size' in topology.node[v]['stack'][1]}
                self.assertEqual(cache_size, expected_caches)
                self.assertEqual(rsn_size, expected_rsn)

        