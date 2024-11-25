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
4. DBBench
5. H-Store
6. "zipf" library in Rust
7. MSLS
8. RocksDB

These generators are evaluated using the following criteria
-  Accuracy (w.r.t. to Apache Commons as a baseline) - L2 distance over buckets
-  Speed (a benchmark standard will be defined later)
-  Presence of artifacts/bugs, e.g.
    - Systematic Trends which are not present in a Zipfian distribution
    - Missing buckets


