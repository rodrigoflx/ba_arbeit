from Sampler import Sampler
from sortedcontainers import SortedDict

import ctypes

from definitions import ROOT_DIR

# Load the shared library
sampler = ctypes.CDLL(ROOT_DIR + '/shared/libsampler.so')

sampler.create_sampler.restype = ctypes.c_void_p
sampler.create_sampler.argtypes = [ctypes.c_long, ctypes.c_double, ctypes.c_long]
sampler.sample.restype = ctypes.c_long
sampler.destroy_sampler.argtypes = [ctypes.c_void_p]

class BaseSampler(Sampler):
    """
    Wrapper for my base sampler
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        self.sampler = sampler.create_sampler(self.n, self.skew, 10)

    def sample(self) -> int:
        return sampler.sample(self.sampler)

    def __del__(self):
        sampler.destroy_sampler(self.sampler)