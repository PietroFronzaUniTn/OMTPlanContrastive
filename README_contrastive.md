# OMTPlan: Optimal Planning Modulo Theories

OMTPlan provides a Python framework for cost-optimal planning in numeric domains.


## Obtaining OMTPlan

Clone the OMTPlan repository in your favourite folder.
	
	git clone https://github.com/PietroFronzaUniTn/OMTPlanContrastive


## Dependencies

To run OMTPlan, make sure you have the following on your machine

* Python 3
* [Z3](https://github.com/Z3Prover/z3) (4.8.6) and its Python API. Make sure you add z3 Python bindings to your Python search path.
* [NetworkX](https://networkx.github.io/) (as simple as `pip install networkx`)
* the [VAL](https://github.com/KCL-Planning/VAL) plan validation software. [Here](http://www.fast-downward.org/SettingUpVal) you can find some instructions to help you set it up. 
Once built, add the *validate* binary to  the `/bin` folder.
* [Unified-planning](https://github.com/aiplan4eu/unified-planning).
* [Runlim](https://github.com/arminbiere/runlim) for testing the solution with time limitation on the execution.



Already provided within this repo are the following external modules

* A modified version of the [Temporal Fast Downward](http://gki.informatik.uni-freiburg.de/tools/tfd/) Python parser.



## Using OMTPlan


###### Translating to SMT-LIB with time limit execution
To produce an SMT-LIB encoding of the bounded planning problem with some constraints over the execution time limit, type, e.g.,

	../runlim/runlim -r real_time_limit_bound -t time_limit_bound ./omtplan -smt -linear -translate bound problem.pddl


###### Some contrastive examples

You can find some experiments for the contrastive explanation in [pddl_examples](/pddl_examples), under each folder mentioned in the paper there will be a directory called "experiments" which contains the experiments for certain planning instances.

The experiments run in the paper are collected in the file [experiments_commands](/experiments_commands.txt).
To launch all the experiments used to test the solution run the following command with all the dependencies installed:

	./experiments.bash experiments_commands.txt





