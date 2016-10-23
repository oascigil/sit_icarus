# LIRA performance evaluation

This example runs experiments evaluating the performance of the LIRA architecture.

## Run
To run, execute the `run.sh` script.

## How does it work
The `config.py` contains all the configuration for executing experiments and
do plots. The `run.sh` launches the Icarus simulator passing the configuration
file as an argument. The `plotresults.py` file provides functions for plotting
specific results based on `icarus.results.plot` functions.