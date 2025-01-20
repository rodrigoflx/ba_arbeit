from sortedcontainers import SortedDict
from Sampler import Sampler

import ctypes
from ctypes import c_void_p, c_long, c_double

from definitions import ROOT_DIR

# Load the shared library
zipf_lib = ctypes.CDLL(ROOT_DIR + '/shared/sysbench_wrapper.so')

# Define function signatures
zipf_lib.zipf_create.argtypes = [c_long, c_double]
zipf_lib.zipf_create.restype = c_void_p

zipf_lib.zipf_sample.argtypes = []
zipf_lib.zipf_sample.restype = c_long


class SysbenchSampler(Sampler):
    """
    Wrapper for the RJI sampler from Gabriel
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        zipf_lib.zipf_create(self.n, self.skew)

    def sample(self) -> int:
        return zipf_lib.zipf_sample()


if __name__ == "__main__":
    dict = SortedDict()
    sampler = SysbenchSampler(100, 100, 0.8)
    for _ in range(1000):
        dict[sampler.sample()] = dict.get(sampler.sample(), 0) + 1

    print(dict)