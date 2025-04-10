# Bachelor Thesis, Rodrigo Felix Forno, WS2425
This repository contains the source code of the experiments, implementation and the thesis document (written in LaTeX)

## Table of Contents
1. Experiments
2. Implementation
3. LaTeX Code

### Experiments
One of the goals of the thesis is to make a comparative analysis of the most common generators for sampling a Zipfian distribution. For this, we evaluate the following implementations:
1. FIO
2. YCSB
3. Apache Commons
4. Sysbench

These generators are evaluated using the following criteria
-  Accuracy
    - Kolmogorov-Smirnov distance (KSD)
    - Total Variation Distance (TVD)
    - Ratio between empirical and theoretical probability functions for the Zipfian
- Performance
    - Throughput in variates per second

Accuracy:
1. Run 'sample_zipf' with the desired generator and the distribution parameters (Try `sample_zipf --help`)
2. With the resulting CSV (other file formats are not directly supported, but can be generated from `sample_zipf`),
it is possible to run `accuracy_zipf` with the appropriate parameters to yield TVD and KSD
3. To get the ratio graph, run `RScript r_scripts/normalized_graph.r' with the appropriate arguments

To do it in a single shot for multiple samplers, it's possible to use the bash scripts provided `run_zipf_then_acc.sh`

To evaluate performance, please refer to the thesis PDF to see the comands used. Alternatively, one could run the `macrobenchmark` command. 
The results, however, can suffer from systematic biases, as discussed in the thesis paper.

### Implementation
The implementations in C++ can be found under the impl folder, it consists of the following algorithms:
1. Rejection Sampling
2. Rejection-Inversion Sampling
3. Condensed Table Lookup (Marsaglia)

To change between versions, modify line `12` of the Makefile with the appropriate number. Then just run `make` in the same directory.
Resulting will be a shared library file, which can be used in the main benchmark code contained in `benchmark`.

### Latex Code for the Thesis
The code is based on the `tum-latex-template` and was setup as suggested in the original repo. Further packages were added, but all contained 
in a standard instalation of a 'pdflatex'. To compile, follow the instructions contained in the original repo.


