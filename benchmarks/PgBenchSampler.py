from Sampler import Sampler
import ctypes

from sortedcontainers import SortedDict

from definitions import ROOT_DIR
import pandas as pd
import matplotlib.pyplot as plt

# Load the shared library
lib = ctypes.CDLL(ROOT_DIR + '/shared/pg_wrapper.so')

lib.zipf_create.argtypes = [ctypes.c_int]
lib.zipf_create.restype = ctypes.c_void_p

lib.zipf_sample.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_double]
lib.zipf_sample.restype = ctypes.c_long

lib.zipf_benchmark.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_double]
lib.zipf_benchmark.restype = ctypes.c_long

class PgBenchSampler(Sampler):
    def __init__(self, n, samples, skew):
        self.n = n
        self.skew = skew
        self.samples = samples
        self.sampler = lib.zipf_create(10)

    def sample(self) -> int:
        return lib.zipf_sample(self.sampler, self.n, self.skew)

    def benchmark(self) -> int:
        return lib.zipf_benchmark(self.sampler, self.n, self.samples, self.skew)


if __name__ == "__main__":
    n = 1000
    samples = 10 * n
    a = 1.1

    dict = SortedDict()
    sampler = PgBenchSampler(n, samples, a)
    
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