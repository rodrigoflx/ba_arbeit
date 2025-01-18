from Sampler import Sampler
from sortedcontainers import SortedDict

import ctypes
from ctypes import c_void_p, c_long, c_double

from definitions import ROOT_DIR

# Load the shared library
zipf_lib = ctypes.CDLL(ROOT_DIR + '/shared/lean_sampler.so')

# Define function signatures
zipf_lib.zipf_create.argtypes = [c_long, c_double, ctypes.c_ulong]
zipf_lib.zipf_create.restype = c_void_p

zipf_lib.zipf_destroy.argtypes = [c_void_p]
zipf_lib.zipf_destroy.restype = None

zipf_lib.zipf_sample.argtypes = [c_void_p]
zipf_lib.zipf_sample.restype = c_long


class LeanStoreSampler(Sampler):
    """
    Wrapper for the RJI sampler from Gabriel
    """

    def __init__(self, n: int, samples: int, skew: float):
        super().__init__(n, samples, skew)
        self.sampler = zipf_lib.zipf_create(self.n, self.skew, 10)

    def sample(self) -> int:
        return zipf_lib.zipf_sample(self.sampler)
    
    def __del__(self):
        zipf_lib.zipf_destroy(self.sampler)