This folder contains experiments for various Rocketfuel topologies extracted from
latency information. Each subfolder contains results for various topologies and 
is named with the AS number of the corresponding topology. Attributes of the topology
is given in the table below. 

The parameters used in all the experiments provided in this folder are given below:

probability of caching: 0.18
freshness threshold: 5 seconds
expiration threshold: 30 seconds
Extra Quota: 3
fan out: 2 (at each hop top-2 freshest entries are selected)
on path hint: enabled   

Rocketfuel Topologies based on latencies

    +------+---------------------+-------+--------+-------+-------------------+
    | ASN  | Name                | Span  | Region | Nodes | Lrgst conn. comp. |   Links
    +======+=====================+=======+========+=======+===================+
    | 1221 | Telstra (Australia) | world | AUS    |  108  |        104        |   153
    | 1239 | Sprintlink (US)     | world | US     |  315  |        315        |   972
    | 1755 | EBONE (Europe)      | world | Europe |   87  |         87        |   161
    | 3257 | Tiscali (Europe)    | world | Europe |  161  |        161        |   328
    | 3967 | Exodus (US)         | world | US     |   79  |         79        |   147
    | 6461 | Abovenet (US)       | world | US     |  141  |        138        |   376
    +------+---------------------+-------+--------+-------+-------------------+

