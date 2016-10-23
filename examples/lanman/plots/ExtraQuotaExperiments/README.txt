
This folder contains experiments for various Rocketfuel topologies extracted from
latency information. 3 metrics are used: Latency, Overhead and Satisfaction Rate. 
A separate plot is provided for each metric for extra quota values: 1, 2, 3, 4, 5, and 6.
Each plot provides a separate bar for different freshness thresholds of 1, 2, 3 ... 10
seconds.  

The parameters used in all the experiments provided in this folder are given below:

probability of caching: 0.20
freshness threshold varies: 1, 2, 3, 4, 5,... seconds
expiration threshold: 30 seconds
Extra Quota varies: 
fan out: 2 (at each hop top-2 freshest entries are selected)
on path hint: enabled   

Rocketfuel Topologies based on latencies:

    +------+---------------------+-------+--------+-------+-------------------+
    | ASN  | Name                | Span  | Region | Nodes | Lrgst conn. comp. |  Links
    +======+=====================+=======+========+=======+===================+
    | 1221 | Telstra (Australia) | world | AUS    |  108  |        104        |   153
    | 1239 | Sprintlink (US)     | world | US     |  315  |        315        |   972
    | 1755 | EBONE (Europe)      | world | Europe |   87  |         87        |   161
    | 3257 | Tiscali (Europe)    | world | Europe |  161  |        161        |   328
    | 3967 | Exodus (US)         | world | US     |   79  |         79        |   147
    | 6461 | Abovenet (US)       | world | US     |  141  |        138        |   376
    +------+---------------------+-------+--------+-------+-------------------+

