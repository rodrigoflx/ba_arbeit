from Sampler import Sampler
import ctypes

from sortedcontainers import SortedDict
from random import randint

from definitions import ROOT_DIR
import pandas as pd
import matplotlib.pyplot as plt

# Load the shared library
lib = ctypes.CDLL(ROOT_DIR + '/shared/rocksdb_wrapper.so')

lib.zipf_create.argtypes = [ctypes.c_double, ctypes.c_uint64]
lib.zipf_create.restype = ctypes.c_void_p

lib.zipf_sample.argtypes = [ctypes.c_void_p, ctypes.c_int64]
lib.zipf_sample.restype = ctypes.c_int64

class RocksDBSampler(Sampler):
    def __init__(self, n, samples, skew):
        self.n = n
        self.samples = samples
        self.sampler = lib.zipf_create(skew, randint(0, 2**32 - 1))

    def sample(self) -> int:
        return lib.zipf_sample(self.sampler, self.n)


if __name__ == "__main__":
    n = 1000
    samples = 10 * n
    a = 0.4

    dict = SortedDict()
    sampler = RocksDBSampler(n, samples, a)
    
    for _ in range(samples):
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