# -*- coding: utf-8 -*-
"""Functions for visualizing results on graphs of topologies
"""
from __future__ import division
import os
import argparse

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


def plot_deployment_strategies_cache_hits(resultset, plotdir, topology, rsn_cache_ratio=1.0):
    """Plot RSN fresheness against deployment strategies
    """
    
    # Pyplot parameters
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    
    deployments = ['CACHE_ALL_RSN_ALL']
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xparam'] = ('joint_cache_rsn_placement', 'name')
    desc['xvals'] = deployments
    desc['xticks'] = [DEPLOYMENT_LEGEND[d] for d in deployments]
    desc['placement'] = [2, 2]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'joint_cache_rsn_placement': {'rsn_cache_ratio': rsn_cache_ratio}}
    desc['ymetrics'] = 2 *  [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                             ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['ycondnames'] = 4*[('strategy', 'name')]
    desc['ycondvals'] = 2*['LIRA_LCE'] + 2*['LIRA_CHOICE']
    desc['errorbar'] = True
    desc['legend_loc'] = 'lower right' # 'upper right'
    desc['legend_args'] = {'ncol': 2} 
    desc['ymax'] = 0.16
    desc['plotempty'] = True
    desc['legend'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): 'On-path, LCE',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): 'Off-path, LCE',
                      (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): 'On-path, choice',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): 'Off-path, choice'}
    
    desc['bar_color'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): 'red',
                      (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): 'blue',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): 'red'}

    desc['bar_hatch'] = {(('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_LCE'): None,
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_LCE'): None,
                      (('CACHE_HIT_RATIO', 'MEAN_ON_PATH'), 'LIRA_DFIB'): '//',
                      (('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'), 'LIRA_DFIB'): '//'}
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



def plot_rsn_sizing_graphs(resultset, plotdir, topology, strategy, deployment):
    """Plot cache hit ratio vs RSN hit ratio"""
    # Name mappings for file names
    s_name = {'LIRA_LCE': 'lce', 'LIRA_CHOICE': 'choice'}
    # Plot attributes
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 6
    rsn_cache_ratios = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'C-FIB/cache size ratio'
    desc['xparam'] = ('joint_cache_rsn_placement', 'rsn_cache_ratio')
    desc['xvals'] = rsn_cache_ratios
    desc['xticks'] = [r"%s" % r for r in rsn_cache_ratios]
    desc['filter'] = {'topology': {'name': 'ROCKET_FUEL', 'asn': topology},
                      'joint_cache_rsn_placement':{'name': deployment},
                      'strategy': {'name': strategy}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN_ON_PATH'),
                        ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH')]
    desc['errorbar'] = True
    desc['group_width'] = 0.2
    desc['legend_loc'] = 'lower right'
    desc['plotempty'] = True
    desc['placement'] = 'stacked'
    desc['legend'] = {('CACHE_HIT_RATIO', 'MEAN_ON_PATH'): 'On path',
                      ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'): 'Off path'}
    desc['bar_color'] = {('CACHE_HIT_RATIO', 'MEAN_ON_PATH'): '#00006B',
                         ('CACHE_HIT_RATIO', 'MEAN_OFF_PATH'): 'red'}
    desc['ymax'] = 0.16
    desc['bar_hatch'] = None
    plot_bar_chart(resultset, desc, 'hits-chra-%s-%s-%s.pdf'
                   % (str(topology), s_name[strategy], deployment), plotdir)


def plot_multicast(resultset, plotdir):
    """Plot distance to CFIB node"""
    # Pyplot params
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 18
    plt.rcParams['figure.figsize'] = 8, 5
    asn_list = [1221, 1239, 1755, 3257, 3967,  6461]
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
    for topology in [1221, 6461]:
        plot_deployment_strategies_rsn_freshness(resultset, plotdir, topology, rsn_cache_ratio=16.0)
        plot_deployment_strategies_cache_hits(resultset, plotdir, topology, rsn_cache_ratio=16.0)
        for strategy in ['LIRA_CHOICE']:
            plot_rsn_sizing_graphs(resultset, plotdir, topology, strategy, 'CACHE_HIGH_RSN_ALL')
            plot_incremental_deployment_cache_hits(resultset, plotdir, topology, strategy)
    # Not included in the paper        
    plot_multicast(resultset, plotdir)
    
#     for topology in [1221, 1239, 1755, 3257, 3967,  6461]:
#         for rsn_cache_ratio in [1.0, 2.0, 4.0, 8.0, 16.0]:
#             plot_deployment_strategies_rsn_freshness(resultset, plotdir, topology, rsn_cache_ratio)
#             plot_deployment_strategies_cache_hits(resultset, plotdir, topology, rsn_cache_ratio)
#         for deployment in ['CACHE_HIGH_RSN_HIGH', 'CACHE_HIGH_RSN_ALL', 'CACHE_ALL_RSN_HIGH', 'CACHE_ALL_RSN_ALL']:
#             plot_rsn_sizing_graphs(resultset, plotdir, topology, 'LIRA_LCE', deployment)
#             plot_rsn_sizing_graphs(resultset, plotdir, topology, 'LIRA_CHOICE', deployment)
#         plot_deployment_strategies_cache_hits_ccn_comparison(resultset, plotdir, topology, 'CACHE_ALL_RSN_HIGH')
#         renormalize_rsn_freshness(resultset)
#         for strategy in ('LIRA_LCE', 'LIRA_CHOICE'):
#             plot_incremental_deployment_freshness(resultset, plotdir, topology, strategy)
#             plot_incremental_deployment_cache_hits(resultset, plotdir, topology, strategy)
#             plot_incremental_deployment_cache_hits_off_path(resultset, plotdir, topology, strategy)



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
    # Create dir if not existsing
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    # Plot graphs
    print('Plotting results')
    plot_paper_graphs(resultset, plotdir)
    print('Exit. Plots were saved in directory %s' % os.path.abspath(plotdir))

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

