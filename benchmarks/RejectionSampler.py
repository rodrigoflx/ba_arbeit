from Sampler import Sampler
import ctypes
import pandas as pd 
import matplotlib.pyplot as plt 
from collections import Counter

from definitions import ROOT_DIR

# Load the shared library
lib = ctypes.CDLL(ROOT_DIR + '/shared/rejection_sampler.so')

SamplerHandle = ctypes.POINTER(ctypes.c_char)

lib.create_sampler.argtypes = [ctypes.c_long, ctypes.c_double, ctypes.c_long]
lib.sample.argtypes = [SamplerHandle]
lib.destroy_sampler.argtypes = [SamplerHandle]

lib.create_sampler.restype = SamplerHandle
lib.sample.restype = ctypes.c_long

class LibWrapper:
    def __init__(self, n, skew):
        self.sampler = lib.create_sampler(n, skew, 102)

    def sample(self) -> int:
        return lib.sample(self.sampler)

    def destroy(self) -> None:
        lib.destroy_sampler(self.sampler)

    def benchmark(self, samples) -> int:
        return lib.benchmark(self.sampler, samples)

class RejectionSampler(Sampler):
    """
    Wrapper for my base sampler
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        self.sampler = LibWrapper(n, skew)
    
    def sample(self):
        return self.sampler.sample()

    def benchmark(self):
        return self.sampler.benchmark(self.samples)


if __name__ == "__main__":
    n = 1000
    samples = 10 * n
    a = 1.1

    dict = Counter()
    sampler = RejectionSampler(n, samples, a)
    
    for _ in range(samples):
        sample = sampler.sample()
        if sample in dict:
            dict[sample] += 1
        else:
            dict[sample] = 1 

    samples = pd.DataFrame(sorted(dict.items()), columns=['Value', 'Frequency'])

    # Plot histogram of values based on frequency
    plt.bar(samples["Value"], samples["Frequency"], log=True)
    plt.title("Zipfian Distribution")
    plt.xlabel("Value")
    plt.ylabel("Frequency (log scale)")
    plt.show()