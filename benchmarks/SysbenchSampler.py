from sortedcontainers import SortedDict
from Sampler import Sampler

import ctypes
from ctypes import c_void_p, c_long, c_double

import matplotlib.pyplot as plt
import pandas as pd

from definitions import ROOT_DIR

# Load the shared library
zipf_lib = ctypes.CDLL(ROOT_DIR + '/shared/sysbench_wrapper.so')

# Define function signatures
zipf_lib.zipf_create.argtypes = [c_long, c_double]
zipf_lib.zipf_create.restype = c_void_p

zipf_lib.zipf_sample.argtypes = []
zipf_lib.zipf_sample.restype = c_long

zipf_lib.zipf_benchmark.argtypes = [c_long]
zipf_lib.zipf_benchmark.restype = c_long


class SysbenchSampler(Sampler):
    """
    Wrapper for the RJI sampler from Gabriel
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        zipf_lib.zipf_create(self.n, self.skew)

    def sample(self) -> int:
        return zipf_lib.zipf_sample()

    def benchmark(self) -> int:
        return zipf_lib.zipf_benchmark(self.samples)


if __name__ == "__main__":
    dict = SortedDict()
    sampler = SysbenchSampler(1000, 10000, 1.1)
    for _ in range(10000):
        sample = sampler.sample()
        if sample in dict:
            dict[sample] += 1
        else:
            dict[sample] = 1 

    samples = pd.DataFrame(dict.items(), columns=['Value', 'Frequency'])

    # Plot histogram of values based on frequency
    plt.bar(samples["Value"], samples["Frequency"], log=True)
    plt.title("Zipfian Distribution")
    plt.xlabel("Value")
    plt.ylabel("Frequency (log scale)")
    plt.show()