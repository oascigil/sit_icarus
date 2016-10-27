# -*- coding: utf-8 -*-
"""Functions for visualizing results on graphs of topologies
"""
from __future__ import division
import os
import argparse

import sys #Onur

import matplotlib.pyplot as plt

from icarus.registry import RESULTS_READER
from icarus.results.plot import plot_bar_chart, plot_lines


# Legend for deployment strategies
DEPLOYMENT_LEGEND = {
   'CACHE_HIGH_NO_RSN':   r'$\left(C_{H}, F_{0}\right)$',
   'CACHE_HIGH_RSN_HIGH': r'$\left(C_{H}, F_{H}\right)$',
   'CACHE_HIGH_RSN_ALL':  r'$\left(C_{H}, F_{A}\right)$',
   'CACHE_HIGH_RSN_LOW':  r'$\left(C_{H}, F_{L}\right)$',
   'CACHE_ALL_NO_RSN':    r'$\left(C_{A}, F_{0}\right)$',
   'CACHE_ALL_RSN_HIGH':  r'$\left(C_{A}, F_{H}\right)$',
   'CACHE_ALL_RSN_ALL':   r'$\left(C_{A}, F_{A}\right)$',
                       }
STRATEGY_LEGEND = {
   'NDN':        r'$\left(NDN\right)$',
   'LIRA_LCE':   r'$\left(LIRA\right)$',
   'LIRA_BC':    r'$\left(BC\right)$',
   'LIRA_DFIB':  r'$\left(DFIB\right)$',
   'NRR':        r'$\left(NRR\right)$', 
                  }

STRATEGY_STYLE = {
         'LIRA_DFIB':             'b--p',
         'LIRA_BC':      'c--<',
         'LIRA_LCE':  'g--*',
                }
def plot_deployment_strategies_rsn_freshness(resultset, plotdir, topology, rsn_cache_ratio=1.0):
    """Plot RSN fresheness against deployment strategies
    """
    
    # Pyplot parameters
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    deployments = ['CACHE_HIGH_RSN_ALL', 'CACHE_HIGH_RSN_HIGH',
                   'CACHE_ALL_RSN_ALL',  'CACHE_ALL_RSN_HIGH']
    desc = {}
    desc['ylabel'] = 'C-FIB freshness'
    desc['xparam'] = ('joint_cache_rsn_placement', 'name')
    desc['xvals'] = deployments
    desc['xticks'] = [DEPLOYMENT_LEGEND[d] for d in deployments]
    desc['placement'] = [3, 3]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'joint_cache_rsn_placement': {'rsn_cache_ratio': rsn_cache_ratio}}
    desc['ymetrics'] = 2 * [('CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'), ('CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'), ('CONTROL_PLANE', 'MEAN_RSN_THREE_HOP')]
    desc['ycondnames'] = 6*[('strategy', 'name')]
    desc['ycondvals'] = 3*['LIRA_LCE'] + 3*['LIRA_CHOICE']
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper left' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    desc['plotempty'] = True
    desc['ymax'] = 0.12
    desc['legend'] = {(('CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'), 'LIRA_LCE'): '1 hop, LCE',
                      (('CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'), 'LIRA_LCE'): '2 hops, LCE',
                      (('CONTROL_PLANE', 'MEAN_RSN_THREE_HOP'), 'LIRA_LCE'): '3 hops, LCE',
                      (('CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'), 'LIRA_CHOICE'): '1 hop, choice',
                      (('CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'), 'LIRA_CHOICE'): '2 hops, choice',
                      (('CONTROL_PLANE', 'MEAN_RSN_THREE_HOP'), 'LIRA_CHOICE'): '3 hops, choice'}
    
    desc['bar_color'] = {(('CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'), 'LIRA_LCE'): 'blue',
                      (('CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'), 'LIRA_LCE'): 'red',
                      (('CONTROL_PLANE', 'MEAN_RSN_THREE_HOP'), 'LIRA_LCE'): 'yellow',
                      (('CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'), 'LIRA_CHOICE'): 'blue',  # #00006B
                      (('CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'), 'LIRA_CHOICE'): 'red',
                      (('CONTROL_PLANE', 'MEAN_RSN_THREE_HOP'), 'LIRA_CHOICE'): 'yellow'}

    desc['bar_hatch'] = {(('CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'), 'LIRA_LCE'): None,
                      (('CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'), 'LIRA_LCE'): None,
                      (('CONTROL_PLANE', 'MEAN_RSN_THREE_HOP'), 'LIRA_LCE'): None,
                      (('CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'), 'LIRA_CHOICE'): '//',
                      (('CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'), 'LIRA_CHOICE'): '//',
                      (('CONTROL_PLANE', 'MEAN_RSN_THREE_HOP'), 'LIRA_CHOICE'): '//'}
    plot_bar_chart(resultset, desc, 'strategies-freshness-%s-rsn-ratio-%s.pdf'
                   % (str(topology), str(rsn_cache_ratio)), plotdir)

def plot_overhead(resultset, plotdir, topology, rsn_cache_ratio):
    # Pyplot parameters
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5

    # TODO
    strategies = ['LIRA_BC', 'LIRA_DFIB', 'NDN', 'NRR']
    desc = {}
    desc['ylabel'] = 'Overhead (hops)'
    desc['xparam'] = ('strategy', 'name')
    desc['xvals'] = strategies #deployments
    desc['xticks'] = [STRATEGY_LEGEND[d] for d in strategies]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'joint_cache_rsn_placement': {'rsn_cache_ratio': rsn_cache_ratio}}
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('OVERHEAD', 'MEAN')]
    desc['ycondnames'] = [('joint_cache_rsn_placement', 'name')]
    desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] 
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['line_style'] = STRATEGY_STYLE
    desc['plotempty'] = False
    
    plot_bar_chart(resultset, desc, 'OVERHEAD_T=%s@A=%s.pdf'
               % (str(topology), str(rsn_cache_ratio)), plotdir)

def plot_latency(resultset, plotdir, topology, rsn_cache_ratio):
    """Plot forwarding strategy against latency
    """
    
    # Pyplot parameters
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5

    strategies = ['LIRA_BC', 'LIRA_DFIB', 'NDN', 'NRR']
    desc = {}
    desc['ylabel'] = 'Latency (ms)'
    desc['xparam'] = ('strategy', 'name')
    desc['xvals'] = strategies #deployments
    desc['xticks'] = [STRATEGY_LEGEND[d] for d in strategies]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'joint_cache_rsn_placement': {'rsn_cache_ratio': rsn_cache_ratio}}
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('LATENCY', 'MEAN')]
    desc['ycondnames'] = [('joint_cache_rsn_placement', 'name')]
    desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] 
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['line_style'] = STRATEGY_STYLE
    desc['plotempty'] = False
    #desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'On-path',
     #                 (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'Off-path'}
    
    #desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'blue',
     #                 (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'red'}
      #                (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): 'blue',
       #               (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): 'red'}

    #desc['bar_hatch'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): None,
     #                 (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): None,
      #                (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): '//',
       #               (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): '//'}
    plot_bar_chart(resultset, desc, 'LATENCY_T=%s@A=%s.pdf'
               % (str(topology), str(rsn_cache_ratio)), plotdir)

def plot_cachehitsVStimeout(resultset, plotdir, topology, timeouts):
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'Expiration'
    desc['xparam'] = ('strategy', 'rsn_timeout')
    desc['xvals'] = timeouts #strategies #deployments
    desc['xticks'] = [r"%s" % r for r in timeouts]
    desc['placement'] = [2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology}}

    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                             ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 2*[('joint_cache_rsn_placement', 'name')]
    desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] + ['CACHE_ALL_RSN_ALL']
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    # desc['ymax'] = 0.80
    desc['plotempty'] = True
    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'On-path',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'Off-path'}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'red'}
    plot_bar_chart(resultset, desc, 'cache-hits-%s-time-out.pdf'
                   % (str(topology)), plotdir)


def plot_satrateVSextraquota(resultset, plotdir, topology, caching_probabilities, quota):
    """Plot sat. rate against extra quota and caching probability (only applicable to DFIB method)
    """
    
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    desc = {}
    desc['xlabel'] = 'Probability of caching'
    desc['ylabel'] = 'Request satisfaction rate'
    desc['xparam'] = ('strategy', 'p')
    desc['xvals'] = caching_probabilities #strategies #deployments
    desc['xticks'] = [r"%s" % r for r in caching_probabilities]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'extra_quota': quota}}
    desc['ymetrics'] = [('SAT_RATE', 'MEAN')]
    #desc['ycondnames'] = [('joint_cache_rsn_placement', 'name')]
    #desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] 
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['plotempty'] = False
    plot_bar_chart(resultset, desc, 'SatisfactionRate-%s-extra-quota-%s.pdf'
               % (str(topology), str(quota)), plotdir)


def plot_overheadVSextraquota(resultset, plotdir, topology, caching_probabilities, quota):
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    desc = {}
    desc['ylabel'] = 'Overhead'
    desc['xlabel'] = 'Probability of caching'
    desc['xparam'] = ('strategy', 'p')
    desc['xvals'] = caching_probabilities #strategies #deployments
    desc['xticks'] = [r"%s" % r for r in caching_probabilities]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'extra_quota': quota}}
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('OVERHEAD', 'MEAN')]
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['plotempty'] = False
    plot_bar_chart(resultset, desc, 'Overhead-%s-extra-quota-%s.pdf'
                   % (str(topology), str(quota)), plotdir)

def plot_cachehitsVSextraquota(resultset, plotdir, topology, caching_probabilities, quota):
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'Probability of caching'
    desc['xparam'] = ('strategy', 'p')
    desc['xvals'] = caching_probabilities #strategies #deployments
    desc['xticks'] = [r"%s" % r for r in caching_probabilities]
    desc['placement'] = [2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'extra_quota': quota}}
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                             ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 2*[('joint_cache_rsn_placement', 'name')]
    desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] + ['CACHE_ALL_RSN_ALL']
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    # desc['ymax'] = 0.80
    desc['plotempty'] = True
    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'On-path',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'Off-path'}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'red'}
    plot_bar_chart(resultset, desc, 'cache-hits-%s-extra-quota-%s.pdf'
                   % (str(topology), str(quota)), plotdir)


def plot_cachehitsVSfreshness(resultset, plotdir, topology, fresh_intervals):
    
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 12
    plt.rcParams['figure.figsize'] = 8, 5
    
    desc = {}
    desc['xlabel'] = 'Freshness threshold'
    desc['ylabel'] = 'Cache hit ratio'
    desc['xparam'] = ('strategy', 'rsn_fresh')
    desc['xvals'] = fresh_intervals #strategies #deployments
    desc['xticks'] = [r"%s" % r for r in fresh_intervals]
    desc['placement'] = [2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'name': 'LIRA_BC_HYBRID'} }
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                             ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 2*[('joint_cache_rsn_placement', 'name')]
    desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] + ['CACHE_ALL_RSN_ALL']
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    desc['ymax'] = 0.60
    desc['plotempty'] = True
    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'On-path',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'Off-path'}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'black',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'red'}
    plot_bar_chart(resultset, desc, '3_cachehits-freshness-%s.pdf'
                   % (str(topology)), plotdir)

def plot_satrateVSfreshness(resultset, plotdir, topology, fresh_intervals, quota):
    """Plot RSN freshness threshold against satisfaction rate (only applicable to DFIB method)
    """
    
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    desc = {}
    desc['xlabel'] = 'Freshness threshold'
    desc['ylabel'] = 'Sat. Rate '
    desc['xparam'] = ('strategy', 'rsn_fresh')
    desc['xvals'] = fresh_intervals #strategies #deployments
    desc['xticks'] = [r"%s" % r for r in fresh_intervals]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'extra_quota': quota}}
    desc['ymetrics'] = [('SAT_RATE', 'MEAN')]
    #desc['ycondnames'] = [('joint_cache_rsn_placement', 'name')]
    #desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] 
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['plotempty'] = False
    plot_bar_chart(resultset, desc, 'SAT_RATE_T=%s@A=%s.pdf'
               % (str(topology), str(quota)), plotdir)


def  plot_latencyVSfreshness(resultset, plotdir, topology, fresh_intervals):
    """PLOT RSN freshness threshold against cache hits
    """

    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 12
    plt.rcParams['figure.figsize'] = 8, 5
    
    desc = {}
    desc['xlabel'] = 'Freshness threshold'
    desc['ylabel'] = 'Latency (ms)'
    desc['xparam'] = ('strategy', 'rsn_fresh')
    desc['xvals'] = fresh_intervals #strategies #deployments
    desc['xticks'] = [r"%s" % r for r in fresh_intervals]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'name':  'LIRA_BC_HYBRID'}}
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('LATENCY', 'MEAN')]
    #desc['ycondnames'] = [('joint_cache_rsn_placement', 'name')]
    #desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] 
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['plotempty'] = False
    desc['bar_color'] = {('LATENCY', 'MEAN') : 'red'}
    plot_bar_chart(resultset, desc, '3_latency-%s.pdf'
               % (str(topology)), plotdir)


def plot_deployment_strategies_cache_hits(resultset, plotdir, topology, rsn_cache_ratio):
    """Plot RSN size against deployment strategies
    """
    
    # Pyplot parameters
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    strategies = ['LIRA_BC', 'LIRA_DFIB', 'NDN', 'NRR']
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xparam'] = ('strategy', 'name')
    desc['xvals'] = strategies #deployments
    desc['xticks'] = [STRATEGY_LEGEND[d] for d in strategies]
    desc['placement'] = [2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'joint_cache_rsn_placement': {'rsn_cache_ratio': rsn_cache_ratio}}
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                             ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 2*[('joint_cache_rsn_placement', 'name')]
    desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] + ['CACHE_ALL_RSN_ALL']
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    desc['ymax'] = 0.80
    desc['plotempty'] = True
    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'On-path',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'Off-path'}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'red'}
      #                (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): 'blue',
       #               (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): 'red'}

    #desc['bar_hatch'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): None,
     #                 (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): None,
      #                (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): '//',
       #               (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): '//'}
    plot_bar_chart(resultset, desc, 'strategies-cache-hits-%s-rsn-ratio-%s.pdf'
                   % (str(topology), str(rsn_cache_ratio)), plotdir)


def plot_deployment_strategies_cache_hits_ccn_comparison(resultset, plotdir, topology, deployment):
    """Plot RSN fresheness against deployment strategies
    """
    # Pyplot parameters
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    network_rsn = [0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9]
    desc = {}
    desc['xlabel'] = 'Strategy'
    desc['ylabel'] = 'Cache hit ratio'
    desc['xparam'] = ('joint_cache_rsn_placement', 'network_rsn')
    desc['xvals'] = network_rsn
    desc['placement'] = [2, 2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'joint_cache_rsn_placement': {'name': deployment}}
    desc['ymetrics'] = 2 *  [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                             ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 4*[('strategy', 'name')]
    desc['ycondvals'] = 2*['LIRA_LCE'] + 2*['LIRA_CHOICE']
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    desc['plotempty'] = True
    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): 'On-path, LCE',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): 'Off-path, LCE',
                      (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_CHOICE'): 'On-path, choice',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_CHOICE'): 'Off-path, choice'}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): 'red',
                      (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_CHOICE'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_CHOICE'): 'red'}

    desc['bar_hatch'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): None,
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): None,
                      (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_CHOICE'): '//',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_CHOICE'): '//'}
    plot_bar_chart(resultset, desc, 'strategies-cache-hits-ccn-%s-%s.pdf'
                   % (str(topology), str(deployment)), plotdir)

def plot_incremental_deployment_freshness(resultset, plotdir, topology, strategy):
    """Plot the incremental node deplyoment graph"""
    # name mappings
    s_name = {'LIRA_LCE': 'lce', 'LIRA_CHOICE': 'choice'}
    
    # Pyplot params
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5

    deployment = 'INCREMENTAL'

    incremental_rsn_ratios = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, \
                              0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
    incremental_cache_ratios = [0.25, 0.50, 0.75, 1.0]

    desc = {}
    desc['ylabel'] = 'C-FIB freshness'
    desc['xlabel'] = 'C-FIB nodes ratio'
    desc['xparam'] = ('joint_cache_rsn_placement', 'rsn_node_ratio')
    desc['xvals'] = incremental_rsn_ratios
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'name': strategy},
                      'joint_cache_rsn_placement': {'name': deployment}}
    desc['ymetrics'] = [('CONTROL_PLANE', 'NORM_MEAN_RSN_ALL')] * len(incremental_cache_ratios)
    desc['ycondnames'] = [('joint_cache_rsn_placement', 'cache_node_ratio')] * len(incremental_cache_ratios)
    desc['ycondvals'] = incremental_cache_ratios    
    desc['line_style'] = {0.25: '-b+', 0.50: '-gx', 0.75: '--r+', 1.0: '--cx'}
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right'
    desc['plot_args'] = {'linewidth': 2, 'elinewidth': 2, 'markeredgewidth': 2}
    desc['plotempty'] = True
    desc['legend'] = {x: str(x) for x in desc['ycondvals']}
    filename = 'freshness-incremental-%s-%s.pdf' % (str(topology), s_name[strategy])
    plot_lines(resultset, desc, filename, plotdir)

def plot_incremental_deployment_cache_hits(resultset, plotdir, topology, strategy):
    """Plot the incremental node deplyoment graph"""
    # name mappings
    s_name = {'LIRA_LCE': 'lce', 'LIRA_CHOICE': 'choice'}
    
    # Pyplot params
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5

    deployment = 'INCREMENTAL'

    incremental_rsn_ratios = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, \
                              0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
    incremental_cache_ratios = [0.25, 0.50, 0.75, 1.0]

    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'C-FIB nodes ratio'
    desc['xparam'] = ('joint_cache_rsn_placement', 'rsn_node_ratio')
    desc['xvals'] = incremental_rsn_ratios
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'name': strategy},
                      'joint_cache_rsn_placement': {'name': deployment}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(incremental_cache_ratios)
    desc['ycondnames'] = [('joint_cache_rsn_placement', 'cache_node_ratio')] * len(incremental_cache_ratios)
    desc['ycondvals'] = incremental_cache_ratios    
    desc['line_style'] = {0.25: '-b+', 0.50: '-gx', 0.75: '--r+', 1.0: '--cx'}
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right'
    desc['legend_args'] = {'ncol': 4} 
    desc['plot_args'] = {'linewidth': 2, 'elinewidth': 2, 'markeredgewidth': 2}
    desc['plotempty'] = True
    desc['legend'] = {x: str(x) for x in desc['ycondvals']}
    filename = 'cache-hits-incremental-%s-%s.pdf' % (str(topology), s_name[strategy])
    plot_lines(resultset, desc, filename, plotdir)


def plot_incremental_deployment_cache_hits_off_path(resultset, plotdir, topology, strategy):
    """Plot the incremental node deplyoment graph"""
    # name mappings
    s_name = {'LIRA_LCE': 'lce', 'LIRA_CHOICE': 'choice'}
    
    # Pyplot params
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5

    deployment = 'INCREMENTAL'

    incremental_rsn_ratios = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, \
                              0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
    incremental_cache_ratios = [0.25, 0.50, 0.75, 1.0]

    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'C-FIB nodes ratio'
    desc['xparam'] = ('joint_cache_rsn_placement', 'rsn_node_ratio')
    desc['xvals'] = incremental_rsn_ratios
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'strategy': {'name': strategy},
                      'joint_cache_rsn_placement': {'name': deployment}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')] * len(incremental_cache_ratios)
    desc['ycondnames'] = [('joint_cache_rsn_placement', 'cache_node_ratio')] * len(incremental_cache_ratios)
    desc['ycondvals'] = incremental_cache_ratios    
    desc['line_style'] = {0.25: '-b+', 0.50: '-gx', 0.75: '--r+', 1.0: '--cx'}
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right'
    desc['plot_args'] = {'linewidth': 2, 'elinewidth': 2, 'markeredgewidth': 2}
    desc['plotempty'] = True
    desc['legend'] = {x: str(x) for x in desc['ycondvals']}
    filename = 'cache-hits-off-path-incremental-%s-%s.pdf' % (str(topology), s_name[strategy])
    plot_lines(resultset, desc, filename, plotdir)


"""
def plot_first_experiments(resultset, plotdir, topology, strategy, probabilities, extra_quotas):
    # Plot cache-hit (on-, off-path) for different extra-quota, probability pairs
    # Plot attributes
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'Extra Quota, Probability'
    desc['xparam'] = ('strategy', 'extra_quota')
    desc['xvals'] = probabilities
    desc['xticks'] = [r"%s" % r for r in probabilities]
    desc['placement'] = len(extra_quotas)*[2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology}, 
                      'strategy': {'name': strategy}}
    # ymetrics, ycondnames and ycondvals must have the same length
    desc['ymetrics'] = len(extra_quotas)*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 2*len(extra_quotas)*[('strategy','extra_quota')]
    desc['ycondvals'] = [extra_quotas[i//2] for i in range(len(extra_quotas)*2)]
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    #desc['legend_args'] = {'ncol': 2} 
    desc['ymax'] = 0.80

    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 0.0): 'On-path, Extra quota 0',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 0.0): 'Off-path, Extra quota 0 ',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 1.0): 'On-path, Extra quota 1',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 1.0): 'Off-path, Extra quota 1 ',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 2.0): 'On-path, Extra quota 2',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 2.0): 'Off-path, Extra quota 2 ',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 3.0): 'On-path, Extra quota 3',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 3.0): 'Off-path, Extra quota 3 ',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 4.0): 'On-path, Extra quota 4',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 4.0): 'Off-path, Extra quota 4 ',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 5.0): 'On-path, Extra quota 5',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 5.0): 'Off-path, Extra quota 5 '}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 0.0): 'blue',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 0.0): 'red',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 1.0): 'blue',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 1.0): 'red',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 2.0): 'blue',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 2.0): 'red',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 3.0): 'blue',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 3.0): 'red',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 4.0): 'blue',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 4.0): 'red',
    (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 5.0): 'blue',
                     (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 5.0): 'red'}
    
    
    plot_bar_chart(resultset, desc, '%s-first-experiments-chr-%s.pdf'
                   % (str(topology), str(strategy)), plotdir)

"""

def plot_first_experiments(resultset, plotdir, topology, strategy, probabilities, extra_quota):
    #Plot cache-hit (on-, off-path) for different extra-quota, probability pairs
    # Plot attributes
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'Probability'
    desc['xparam'] = ('strategy', 'p')
    desc['xvals'] = probabilities
    desc['xticks'] = [r"%s" % r for r in probabilities]
    desc['placement'] = [2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology}, 
                      'strategy': {'name': strategy}, 
                      'strategy': {'extra_quota': extra_quota}}
    # ymetrics, ycondnames and ycondvals must have the same length
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    #desc['ycondnames'] = 2*len(extra_quotas)*[('strategy','extra_quota')]
    #desc['ycondvals'] = [extra_quotas[i//2] for i in range(len(extra_quotas)*2)]
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    desc['ymax'] = 0.80
    desc['legend'] = {('CACHE_HIT_RATIO', 'MEAN_ON_PATH'): 'On-path',
                      ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'): 'Off-path'}
    
    desc['bar_color'] = {('CACHE_HIT_RATIO', 'MEAN_ON_PATH'): 'blue',
                      ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'): 'red'}
    plot_bar_chart(resultset, desc, '%s-first-experiments-chr-%s-%s.pdf'
                   % (str(topology), str(strategy), str(extra_quota)), plotdir)


def plot_rsn_sizing_cachehits(resultset, plotdir, topology, strategies, rsn_cache_ratios):
    """Plot cache hit ratio vs RSN hit ratio"""
    # Plot attributes
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'C-FIB/cache size ratio'
    desc['xparam'] = ('joint_cache_rsn_placement', 'rsn_cache_ratio')
    desc['xvals'] = rsn_cache_ratios
    desc['xticks'] = [r"%s" % r for r in rsn_cache_ratios]
    desc['placement'] = [len(strategies)]*len(rsn_cache_ratios)
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology}}
    # desc['ymetrics'] = 2*[('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
    #                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                             ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 2*[('joint_cache_rsn_placement', 'name')]
    desc['ycondvals'] = ['CACHE_ALL_RSN_ALL'] + ['CACHE_ALL_RSN_ALL']
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    desc['ymax'] = 0.80
    desc['plotempty'] = True
    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'On-path',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'Off-path'}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'CACHE_ALL_RSN_ALL'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'CACHE_ALL_RSN_ALL'): 'red'}
      #                (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): 'blue',
       #               (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): 'red'}

    #desc['bar_hatch'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): None,
     #                 (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): None,
      #                (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): '//',
       #               (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): '//'}
    plot_bar_chart(resultset, desc, 'rsnsizing-cache-hits-%s-rsn-ratio.pdf'
                   % (str(topology)), plotdir)



def plot_multicast(resultset, plotdir):
    """Plot distance to CFIB node"""
    # Pyplot params
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    asn_list = [3257]
    node_ratios = [i/20 for i in range(21)]
    desc = {}
    desc['ylabel'] = 'Average hops'
    desc['xlabel'] = 'C-FIB nodes ratio'
    desc['xparam'] = ('node_ratio',)
    desc['xvals'] = node_ratios
    desc['ymetrics'] = [('avg_hops',)] * len(asn_list)
    desc['ycondnames'] = [('asn',)] * len(asn_list)
    desc['ycondvals'] = asn_list    
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper right'
    desc['plot_args'] = {'linewidth': 2, 'elinewidth': 2, 'markeredgewidth': 2}
    desc['plotempty'] = True
    desc['legend'] = {x: str(x) for x in desc['ycondvals']}
    filename = 'avg-hops-multicast.pdf'
    plot_lines(resultset, desc, filename, plotdir)

def renormalize_rsn_freshness(resultset):
    """Add a new metric in the resultset which is an RSN freshness renormalized
    to the RSN size of the case where RSN/cache ratio is 1
    """
    for parameters, results in resultset:
        rsn_node_ratio = parameters.getval(['joint_cache_rsn_placement', 'rsn_node_ratio'])
        if rsn_node_ratio is None:
            continue
        zero_hop_freshness = results.getval(['CONTROL_PLANE', 'MEAN_RSN_ZERO_HOP'])
        if zero_hop_freshness is not None:
            results.setval(['CONTROL_PLANE', 'NORM_MEAN_RSN_ZERO_HOP'],
                           zero_hop_freshness*rsn_node_ratio)
        one_hop_freshness = results.getval(['CONTROL_PLANE', 'MEAN_RSN_ONE_HOP'])
        if one_hop_freshness is not None:
            results.setval(['CONTROL_PLANE', 'NORM_MEAN_RSN_ONE_HOP'],
                           one_hop_freshness*rsn_node_ratio)            
        two_hop_freshness = results.getval(['CONTROL_PLANE', 'MEAN_RSN_TWO_HOP'])
        if two_hop_freshness is not None:
            results.setval(['CONTROL_PLANE', 'NORM_MEAN_RSN_TWO_HOP'],
                           two_hop_freshness*rsn_node_ratio)    
        three_hop_freshness = results.getval(['CONTROL_PLANE', 'MEAN_RSN_THREE_HOP'])
        if three_hop_freshness is not None:
            results.setval(['CONTROL_PLANE', 'NORM_MEAN_RSN_THREE_HOP'],
                           three_hop_freshness*rsn_node_ratio)
        all_freshness = results.getval(['CONTROL_PLANE', 'MEAN_RSN_ALL'])
        if all_freshness is not None:
            results.setval(['CONTROL_PLANE', 'NORM_MEAN_RSN_ALL'],
                           all_freshness*rsn_node_ratio)  


def plot_paper_graphs(resultset, plotdir):
    
    """
    topology = 3967
    probabilities = [0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 1.0]
    extra_quotas = [0, 1, 2, 3, 4, 5]
    for strategy in ['LIRA_DFIB', 'LIRA_BC_HYBRID']:
        plot_first_experiments(resultset, plotdir, topology, strategy, probabilities, extra_quotas)

    """

    topology = 3257 #3967
    probabilities = [0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 1.0]
    extra_quotas = [3] #[0, 1, 2, 3, 4, 5]
    for strategy in ['LIRA_DFIB']:
        for extra_quota in extra_quotas:
            plot_first_experiments(resultset, plotdir, topology, strategy, probabilities, extra_quota)


"""
    topology = 3967
    strategy = 'LIRA_DFIB'
    deployment = 'CACHE_ALL_RSN_ALL'
    plot_rsn_sizing_cachehits(resultset, plotdir, topology, strategy, deployment)
    #plot_rsn_sizing_overhead(resultset, plotdir, topology, rsn_cache_ratio)
    #plot_rsn_sizing_latency(resultset, plotdir, topology, rsn_cache_ratio)
"""

""" Comparison of different strategies
    topology = 3967
    for rsn_cache_ratio in [64.0]:
        plot_deployment_strategies_cache_hits(resultset, plotdir, topology, rsn_cache_ratio)
        plot_overhead(resultset, plotdir, topology, rsn_cache_ratio)
        plot_latency(resultset, plotdir, topology, rsn_cache_ratio)
"""

"""
    caching_probabilities = [0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 1.0]
    for topology in [3967]:
        for extra_quota in [-2, -1, 0, 1, 2, 3, 4]:
            plot_cachehitsVSextraquota(resultset, plotdir, topology, caching_probabilities, extra_quota)
            plot_overheadVSextraquota(resultset, plotdir, topology, caching_probabilities, extra_quota)
            plot_satrateVSextraquota(resultset, plotdir, topology, caching_probabilities, extra_quota)
"""
            
"""
    timeouts = [0.1, 0.5, 1.0, 4.0, 10.0, 40.0, 300.0, 100000.0]
    for topology in [3967]:
        plot_cachehitsVStimeout(resultset, plotdir, topology, timeouts)
"""

"""
    fresh_intervals = [4.0]
    for topology in [3967]:
        for extra_quota in [-2, -1, 0, 1, 2, 3]:
            plot_latencyVSfreshness(resultset, plotdir, topology, fresh_intervals, extra_quota)
            plot_cachehitsVSfreshness(resultset, plotdir, topology, fresh_intervals, extra_quota)
            plot_satrateVSfreshness(resultset, plotdir, topology, fresh_intervals, extra_quota)
            # plot_overhead_freshness(resultset, plotdir, topology, fresh_intervals, extra_quota)
"""

def searchDictMultipleCat(lst, category_list, attr_value_pairs, num_pairs, collector, subtype):
    """
    Search the resultset list for a particular [category, attribute, value] parameter such as ['strategy', 'extra_quota', 3]. attr_value_pairs include the key-value pairs.
    and once such a key is found, extract the result for a collector, subtype such as ['CACHE_HIT_RATIO', 'MEAN']

    Returns the result if found in the dictionary lst; otherwise returns None

    """
    result = None
    for l in lst:
        num_match = 0
        for key, val in l[0].items():
            #print key + '-and-' + category + '-\n'
            if key in category_list:
                if (isinstance(val, dict)):
                    for key1, val1 in val.items():
                        for key2, val2 in attr_value_pairs.items():
                            if key1 == key2 and val1 == val2:
                                num_match = num_match + 1
                    if num_match == num_pairs:
                        result = l[1]
                        break
                else:
                    print 'Something is wrong with the search for attr-value pairs\n'
                    return None
        if result is not None:
            break
    
    if result is None:
        print 'Error searched attribute, value pairs:\n' 
        for k, v in attr_value_pairs.items():
            print '[ ' + repr(k) + ' , ' + repr(v) + ' ]  '
        print 'is not found, returning none\n'
        return None
    
    found = None
    for key, val in result.items():
        if key == collector:
            for key1, val1 in val.items():
                if key1 == subtype:
                    found = val1
                    break
            if found is not None:
                break

    if found is None:
        print 'Error searched collector, subtype ' + repr(collector) + ',' + repr(subtype) + 'is not found\n'

    return found

def searchDict(lst, category, attr_value_pairs, num_pairs, collector, subtype):
    """
    Search the resultset list for a particular [category, attribute, value] parameter such as ['strategy', 'extra_quota', 3]. attr_value_pairs include the key-value pairs.
    and once such a key is found, extract the result for a collector, subtype such as ['CACHE_HIT_RATIO', 'MEAN']

    Returns the result if found in the dictionary lst; otherwise returns None

    """
    result = None
    for l in lst:
        for key, val in l[0].items():
            #print key + '-and-' + category + '-\n'
            if key == category:
                if (isinstance(val, dict)):
                    num_match = 0
                    for key1, val1 in val.items():
                        for key2, val2 in attr_value_pairs.items():
                            if key1 == key2 and val1 == val2:
                                num_match = num_match + 1
                    if num_match == num_pairs:
                        result = l[1]
                        break
                else:
                    print 'Something is wrong with the search for attr-value pairs\n'
                    return None
        if result is not None:
            break
    
    if result is None:
        print 'Error searched attribute, value pairs:\n' 
        for k, v in attr_value_pairs.items():
            print '[ ' + repr(k) + ' , ' + repr(v) + ' ]  '
        print 'is not found, returning none\n'
        return None
    
    found = None
    for key, val in result.items():
        if key == collector:
            for key1, val1 in val.items():
                if key1 == subtype:
                    found = val1
                    break
            if found is not None:
                break

    if found is None:
        print 'Error searched collector, subtype ' + repr(collector) + ',' + repr(subtype) + 'is not found\n'

    return found

def printTree(tree, d = 0):
    if (tree == None or len(tree) == 0):
        print "\t" * d, "-"
    else:
        for key, val in tree.items():
            if (isinstance(val, dict)):
                print "\t" * d, key
                printTree(val, d+1)
            else:
                print "\t" * d, key, str(val)

def print_strategies_experiments_gnuplot(lst):
    """
    Write cache hits (off- and on-path) for different strategies for various probabilities
    to a file in gnuplot format

    """

    strategies = ['NDN', 'NRR_PROB', 'LIRA_BC']
    probabilities = [0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 1.0]

    filename = 'strategies_cachehits.dat'
    f = open(filename, 'w')

    f.write('# Cachehit for strategies: NDN, NRR_PROB, and BC\n')
    f.write('#\n')
    
    f.write('Strategy\t')
    for strategy in strategies:
        f.write(strategy + 'Off' + '\t')
        f.write(strategy + 'On' + '\t')

    f.write('\n')   

    for probability in probabilities:
        f.write(repr(probability) + '\t')
        for strategy in strategies:
            off = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN_OFF_PATH')
            on = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN_ON_PATH')
            if on is not None and off is not None:
                f.write(repr(off) + '\t')
                f.write(repr(on) + '\t')
        f.write('\n')   
    f.close()                   
 
    # Write Satisfaction rates
    filename = 'strategies_satrate.dat'
    f = open(filename, 'w')
    f.write('# Satisfaction rate for strategies: NDN, NRR_PROB, and BC\n')
    f.write('#\n')
    
    f.write('Strategy\t')
    for strategy in strategies:
        f.write(strategy + '\t')

    f.write('\n')   

    for probability in probabilities:
        f.write(repr(probability) + '\t')
        for strategy in strategies:
            satrate = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'SAT_RATE', 'MEAN')
            if satrate is not None:
                f.write(repr(satrate) + '\t')
        f.write('\n')   
    f.close()                 

    # Write Latencies
    filename = 'strategies_latency.dat'
    f = open(filename, 'w')
    f.write('# Average latency for strategies: NDN, NRR_PROB, and BC\n')
    f.write('#\n')
    
    f.write('Strategy\t')
    for strategy in strategies:
        f.write(strategy + '\t')

    f.write('\n')   

    for probability in probabilities:
        f.write(repr(probability) + '\t')
        for strategy in strategies:
            ltncy = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'LATENCY', 'MEAN')
            if ltncy is not None:
                f.write(repr(ltncy) + '\t')
        f.write('\n')   
    f.close()                   
    
    # Write Overhead
    filename = 'strategies_overhead.dat'
    f = open(filename, 'w')
    f.write('# Average latency for strategies: NDN, NRR_PROB, and BC\n')
    f.write('#\n')
    
    f.write('Strategy\t')
    for strategy in strategies:
        f.write(strategy + '\t')

    f.write('\n')   

    for probability in probabilities:
        f.write(repr(probability) + '\t')
        for strategy in strategies:
            overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'OVERHEAD', 'MEAN')
            if overhead is not None:
                f.write(repr(overhead) + '\t')
        f.write('\n')   
    f.close()                   

def print_satrate_experiments_gnuplot(lst, strategies, probabilities, extra_quotas):
    """
    Write overhead results for different strategies for various probabilities and extra quota values
    to a file in gnuplot format

    """

    for strategy in strategies:
        filename = strategy + '_satrate.dat'
        f = open(filename, 'w')

        f.write('# Average satisfaction rate for strategy ' + strategy + '\n')
        f.write('#\n')
    
        f.write('ExtraQuota\t')
        for extra_quota in extra_quotas:
            f.write(repr(extra_quota) + '\t')

        f.write('\n')   

        for probability in probabilities:
            f.write(repr(probability) + '\t')
            for extra_quota in extra_quotas:
                satrate = searchDict(lst, 'strategy', {'name' : strategy, 'extra_quota' : extra_quota, 'p' : probability}, 3, 'SAT_RATE', 'MEAN')
                if satrate is not None:
                    f.write(repr(satrate) + '\t')
            f.write('\n')   
        f.close()                   

def print_overhead_experiments_gnuplot(lst, strategies, probabilities, extra_quotas):
    """
    Write overhead results for different strategies for various probabilities and extra quota values
    to a file in gnuplot format

    """

    for strategy in strategies:
        filename = strategy + '_overhead.dat'
        f = open(filename, 'w')

        f.write('# Average overhead for strategy ' + strategy + '\n')
        f.write('#\n')
    
        f.write('ExtraQuota\t')
        for extra_quota in extra_quotas:
            f.write(repr(extra_quota) + '\t')

        f.write('\n')   

        for probability in probabilities:
            f.write(repr(probability) + '\t')
            for extra_quota in extra_quotas:
                overhead = searchDict(lst, 'strategy', {'name' : strategy, 'extra_quota' : extra_quota, 'p' : probability}, 3, 'OVERHEAD', 'MEAN')
                if overhead is not None:
                    f.write(repr(overhead) + '\t')
            f.write('\n')   
        f.close()                   
    

def print_latency_experiments_gnuplot(lst, strategies, probabilities, extra_quotas):
    """
    Write latency results for different strategies for various probabilities and extra quota values
    to a file in gnuplot format

    """

    for strategy in strategies:
        filename = strategy + '_latency.dat'
        f = open(filename, 'w')

        f.write('# Average latency for strategy ' + strategy + '\n')
        f.write('#\n')
    
        f.write('ExtraQuota\t')
        for extra_quota in extra_quotas:
            f.write(repr(extra_quota) + '\t')

        f.write('\n')   

        for probability in probabilities:
            f.write(repr(probability) + '\t')
            for extra_quota in extra_quotas:
                ltncy = searchDict(lst, 'strategy', {'name' : strategy, 'extra_quota' : extra_quota, 'p' : probability}, 3, 'LATENCY', 'MEAN')
                if ltncy is not None:
                    f.write(repr(ltncy) + '\t')
            f.write('\n')   
        f.close()                   
    
def print_first_experiment_data_gnuplot(lst):
    """
    Print Gnuplot data for the first experiments: impact of caching probaility on the satisfaction and overhead when network is disconnected.

    """
    probabilities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    scopes = [1, 2, 100]
    fan_outs = [1, 100]

    for strategy in ['NDN_SIT']:
        filename = strategy + '_first.dat'
        f = open(filename, 'w')

        f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
        f.write('#\n')
    
        f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead\n')

        for probability in probabilities:
            f.write(repr(probability) + '\t')
            
            mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN')
            user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
            net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
            overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'OVERHEAD', 'MEAN')

            if mean_hits is not None:
                f.write(repr(mean_hits) + '\t')
            else:
                print 'Error reading mean cache hits'

            if user_hits is not None:
                f.write(repr(user_hits) + '\t')
            else:
                print 'Error reading user cache hits'

            if net_hits is not None:    
                f.write(repr(net_hits) + '\t')
            else:
                print 'Error reading network cache hits'

            if overhead is not None:
                f.write(repr(overhead) + '\t')
            else:
                print 'Error reading overhead'
            f.write('\n')
        f.close()                   
        
    # First experiments
    for strategy in ['SIT_ONLY']:
        for fan_out in fan_outs:
            filename = ""
            if fan_out is 1:
                filename += strategy
                filename += "_ONE_first"
                filename += '.dat'
            else:
                filename += strategy
                filename += "_ALL_first"
                filename += '.dat'

            f = open(filename, 'w')

            f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
            f.write('#\n')
    
            f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead\n')

            for probability in probabilities:
                f.write(repr(probability) + '\t')
            
                mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'CACHE_HIT_RATIO', 'MEAN')
                user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
                net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
                overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'OVERHEAD', 'MEAN')

                if mean_hits is not None:
                    f.write(repr(mean_hits) + '\t')
                else:
                    print 'Error reading mean cache hits'

                if user_hits is not None:
                    f.write(repr(user_hits) + '\t')
                else:
                    print 'Error reading user cache hits'

                if net_hits is not None:    
                    f.write(repr(net_hits) + '\t')
                else:
                    print 'Error reading network cache hits'

                if overhead is not None:
                    f.write(repr(overhead) + '\t')
                else:
                    print 'Error reading overhead'
                f.write('\n')
            f.close()   # for each fanout                
    
    # First experiments
    for strategy in ['SIT_WITH_SCOPED_FLOODING']:
        for fan_out in fan_outs:
            for scope in scopes:
                if scope is 100:
                    continue
                filename = ""
                if fan_out is 1:
                    filename += strategy
                    filename += "_scope_%s" % (str(scope))
                    filename += "_ONE"
                    filename += "_first"
                    filename += '.dat'
                else:
                    filename += strategy
                    filename += "_scope_%s" % (str(scope))
                    filename += "_ALL"
                    filename += "_first"
                    filename += '.dat'
                f = open(filename, 'w')

                f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
                f.write('#\n')
    
                f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead\n')

                for probability in probabilities:
                    mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'CACHE_HIT_RATIO', 'MEAN')
                    user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
                    net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
                    overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'OVERHEAD', 'MEAN')
                    f.write(repr(probability) + '\t')

                    if mean_hits is not None:
                        f.write(repr(mean_hits) + '\t')
                    else:
                        print 'Error reading mean cache hits'

                    if user_hits is not None:
                        f.write(repr(user_hits) + '\t')
                    else:
                        print 'Error reading user cache hits'

                    if net_hits is not None:    
                        f.write(repr(net_hits) + '\t')
                    else:
                        print 'Error reading network cache hits'

                    if overhead is not None:
                        f.write(repr(overhead) + '\t')
                    else:
                        print 'Error reading overhead'
                    f.write('\n')
                f.close()   # for each scope

    # First experiments
    for strategy in ['SCOPED_FLOODING']:
        for scope in scopes:
            filename = ""
            filename += strategy
            filename += "_scope_%s" % (str(scope))
            filename += "_first"
            filename += '.dat'
            f = open(filename, 'w')

            f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
            f.write('#\n')
    
            f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead\n')

            for probability in probabilities:
                mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'CACHE_HIT_RATIO', 'MEAN')
                user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
                net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
                overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'OVERHEAD', 'MEAN')
                f.write(repr(probability) + '\t')

                if mean_hits is not None:
                    f.write(repr(mean_hits) + '\t')
                else:
                    print 'Error reading mean cache hits'

                if user_hits is not None:
                    f.write(repr(user_hits) + '\t')
                else:
                    print 'Error reading user cache hits'

                if net_hits is not None:    
                    f.write(repr(net_hits) + '\t')
                else:
                    print 'Error reading network cache hits'

                if overhead is not None:
                    f.write(repr(overhead) + '\t')
                else:
                    print 'Error reading overhead'
                f.write('\n')
            f.close()   # for each scope

def print_second_experiment_data_gnuplot(lst):
    """
    Print Gnuplot data for the second experiments: impact of DFIB size on cache hits on different strategies
    """
    network_cache = [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5]
    scopes = [1, 2, 100]
    fan_outs = [1, 100]

    for strategy in ['NDN_SIT']:
        filename = strategy + '_second.dat'
        f = open(filename, 'w')

        f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
        f.write('#\n')
    
        f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead')

        for probability in probabilities:
            f.write(repr(probability) + '\t')
            
            mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN')
            user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
            net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
            overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability}, 2, 'OVERHEAD', 'MEAN')

            if mean_hits is not None:
                f.write(repr(mean_hits) + '\t')
            else:
                print 'Error reading mean cache hits'

            if user_hits is not None:
                f.write(repr(user_hits) + '\t')
            else:
                print 'Error reading user cache hits'

            if net_hits is not None:    
                f.write(repr(net_hits) + '\t')
            else:
                print 'Error reading network cache hits'

            if overhead is not None:
                f.write(repr(overhead) + '\t')
            else:
                print 'Error reading overhead'
        f.close()                   
        
    # Second experiments
    for strategy in ['SIT_ONLY']:
        for fan_out in fan_outs:
            filename = ""
            if fan_out is 1:
                filename += strategy
                filename += "ONE_second"
                filename += '.dat'
            else:
                filename += strategy
                filename += "ALL_second"
                filename += '.dat'

            f = open(filename, 'w')

            f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
            f.write('#\n')
    
            f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead')

            for probability in probabilities:
                f.write(repr(probability) + '\t')
            
                mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'CACHE_HIT_RATIO', 'MEAN')
                user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
                net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
                overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out}, 3, 'OVERHEAD', 'MEAN')

                if mean_hits is not None:
                    f.write(repr(mean_hits) + '\t')
                else:
                    print 'Error reading mean cache hits'

                if user_hits is not None:
                    f.write(repr(user_hits) + '\t')
                else:
                    print 'Error reading user cache hits'

                if net_hits is not None:    
                    f.write(repr(net_hits) + '\t')
                else:
                    print 'Error reading network cache hits'

                if overhead is not None:
                    f.write(repr(overhead) + '\t')
                else:
                    print 'Error reading overhead'
            f.close()   # for each fanout                
    
    # Second experiments
    for strategy in ['SIT_WITH_SCOPED_FLOODING']:
        for fan_out in fan_outs:
            for scope in scopes:
                filename = ""
                if fan_out is 1:
                    filename += strategy
                    filename += "_scope_%s" % (str(scope))
                    filename += "_ONE"
                    filename += "_second"
                    filename += '.dat'
                else:
                    filename += strategy
                    filename += "_scope_%s" % (str(scope))
                    filename += "_ONE"
                    filename += "_second"
                    filename += '.dat'
                f = open(filename, 'w')

                f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
                f.write('#\n')
    
                f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead')

                for probability in probabilities:
                    mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'CACHE_HIT_RATIO', 'MEAN')
                    user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
                    net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
                    overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'fan_out' : fan_out, 'scope' : scope}, 4, 'OVERHEAD', 'MEAN')
                    f.write(repr(probability) + '\t')

                    if mean_hits is not None:
                        f.write(repr(mean_hits) + '\t')
                    else:
                        print 'Error reading mean cache hits'

                    if user_hits is not None:
                        f.write(repr(user_hits) + '\t')
                    else:
                        print 'Error reading user cache hits'

                    if net_hits is not None:    
                        f.write(repr(net_hits) + '\t')
                    else:
                        print 'Error reading network cache hits'

                    if overhead is not None:
                        f.write(repr(overhead) + '\t')
                    else:
                        print 'Error reading overhead'
                f.close()   # for each scope

    # Second experiments
    for strategy in ['SCOPED_FLOODING']:
        for scope in scopes:
            filename = ""
            filename += strategy
            filename += "_scope_%s" % (str(scope))
            filename += "_second"
            filename += '.dat'
            f = open(filename, 'w')

            f.write('# Satisfaction and Overhead for strategy ' + strategy + '\n')
            f.write('#\n')
    
            f.write('# Probability\tMeanHits\tUserHits\tNetworkHits\tOverhead')

            for probability in probabilities:
                mean_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'CACHE_HIT_RATIO', 'MEAN')
                user_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'CACHE_HIT_RATIO', 'MEAN_USER_HITS')
                net_hits = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'CACHE_HIT_RATIO', 'MEAN_NETWORK_HITS')
                overhead = searchDict(lst, 'strategy', {'name' : strategy, 'p' : probability, 'scope' : scope}, 3, 'OVERHEAD', 'MEAN')
                f.write(repr(probability) + '\t')

                if mean_hits is not None:
                    f.write(repr(mean_hits) + '\t')
                else:
                    print 'Error reading mean cache hits'

                if user_hits is not None:
                    f.write(repr(user_hits) + '\t')
                else:
                    print 'Error reading user cache hits'

                if net_hits is not None:    
                    f.write(repr(net_hits) + '\t')
                else:
                    print 'Error reading network cache hits'

                if overhead is not None:
                    f.write(repr(overhead) + '\t')
                else:
                    print 'Error reading overhead'
            f.close()   # for each scope
    

def plot_third_experiments(resultset, plotdir):
    topology = 3257
    fresh_intervals = [10.0, 30.0, 60.0, 120.0, 180.0, 240.0, 300.0, 600.0, 1200.0]
    plot_cachehitsVSfreshness(resultset, plotdir, topology, fresh_intervals)
    plot_latencyVSfreshness(resultset, plotdir, topology, fresh_intervals) 


def print_fourth_experiment_data(lst):
    topology = 3257
    rsn_timeouts = [5.0, 10.0, 30.0, 60.0, 120.0, 240.0, 360.0, 600.0, 1200.0, 3600.0, 7200.0]
    strategies = ['LIRA_DFIB', 'LIRA_DFIB_OPH', 'LIRA_BC_HYBRID']
    
    filename = '4_cachehits.dat'
    f = open(filename, 'w')

    f.write('# Cachehit for strategies: DFIB, DFIB_OPH, and DFIB_BC_HYBRID\n')
    f.write('#\n')
    
    f.write('Strategy\t')
    for strategy in strategies:
        f.write(strategy + 'Off' + '\t')
        f.write(strategy + 'On' + '\t')

    f.write('\n')   

    for rsn_timeout in rsn_timeouts:
        f.write(repr(rsn_timeout) + '\t')
        for strategy in strategies:
            off = searchDict(lst, 'strategy', {'name' : strategy, 'rsn_timeout' : rsn_timeout}, 2, 'CACHE_HIT_RATIO', 'MEAN_OFF_PATH')
            on = searchDict(lst, 'strategy', {'name' : strategy, 'rsn_timeout' : rsn_timeout}, 2, 'CACHE_HIT_RATIO', 'MEAN_ON_PATH')
            if on is not None and off is not None:
                f.write(repr(off) + '\t')
                f.write(repr(on) + '\t')
        f.write('\n')   
    f.close()

    # Write Latencies
    filename = '4_latency.dat'
    f = open(filename, 'w')

    f.write('# Average latency for strategies: DFIB, DFIB_OPH, and DFIB_BC_HYBRID\n')
    f.write('#\n')

    f.write('Strategy\t')
    for strategy in strategies:
        f.write(strategy + '\t')

    f.write('\n')   
    for rsn_timeout in rsn_timeouts:
        f.write(repr(rsn_timeout) + '\t')
        for strategy in strategies:
            ltncy = searchDict(lst, 'strategy', {'name' : strategy, 'rsn_timeout' : rsn_timeout}, 2, 'LATENCY', 'MEAN')
            if ltncy is not None:
                f.write(repr(ltncy) + '\t')
        f.write('\n')   
    f.close()

    # Write Overhead

    filename = '4_overhead.dat'
    f = open(filename, 'w')

    f.write('# Average overhead for strategies: DFIB, DFIB_OPH, and DFIB_BC_HYBRID\n')
    f.write('#\n')

    f.write('Strategy\t')
    for strategy in strategies:
        f.write(strategy + '\t')

    f.write('\n')   
    for rsn_timeout in rsn_timeouts:
        f.write(repr(rsn_timeout) + '\t')
        for strategy in strategies:
            overhead = searchDict(lst, 'strategy', {'name' : strategy, 'rsn_timeout' : rsn_timeout}, 2, 'OVERHEAD', 'MEAN')
            if overhead is not None:
                f.write(repr(overhead) + '\t')
        f.write('\n')   
    f.close()

def run(resultsfile, plotdir):
    """Run the plot script
    
    Parameters
    ----------
    config : str
        The path of the configuration file
    results : str
        The file storing the experiment results
    plotdir : str
        The directory into which graphs will be saved
    """
    resultset = RESULTS_READER['PICKLE'](resultsfile)
    #Onur: added this BEGIN
    lst = resultset.dump()
    for l in lst:
        print 'PARAMETERS:\n'    
        printTree(l[0])
        print 'RESULTS:\n'
        printTree(l[1])

    print_first_experiment_data_gnuplot(lst)
    #print_second_experiment_data_gnuplot(lst)
    #print_strategies_experiments_gnuplot(lst)
    #print_second_experiment_data(lst)
    #plot_third_experiments(resultset, plotdir)
    #print_fourth_experiment_data(lst)
        
    # Create dir if not existsing
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    # Plot graphs
    print('Plotting results')
    # plot_paper_graphs(resultset, plotdir)
    #print('Exit. Plots were saved in directory %s' % os.path.abspath(plotdir))

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("-r", "--results", dest="results",
                        help='the results file',
                        required=True)
    parser.add_argument("-o", "--output", dest="output",
                        help='the directory where plots will be saved',
                        required=True)
    args = parser.parse_args()
    run(args.results, args.output)

if __name__ == '__main__':
    main()

