from Sampler import Sampler
import ctypes
from sortedcontainers import SortedDict

from definitions import ROOT_DIR

# Load the shared library
lib = ctypes.CDLL(ROOT_DIR + '/shared/libsampler.so')

SamplerHandle = ctypes.POINTER(ctypes.c_char)

lib.create_sampler.argtypes = [ctypes.c_long, ctypes.c_double, ctypes.c_long]
lib.sample.argtypes = [SamplerHandle]
lib.destroy_sampler.argtypes = [SamplerHandle]

lib.create_sampler.restype = SamplerHandle
lib.sample.restype = ctypes.c_long

class LibWrapper:
    def __init__(self, n, skew):
        self.sampler = lib.create_sampler(n, skew, 10)

    def sample(self) -> int:
        return lib.sample(self.sampler)

    def destroy(self) -> None:
        lib.destroy_sampler(self.sampler)

    def benchmark(self, samples) -> int:
        return lib.benchmark(self.sampler, samples)

class BaseSampler(Sampler):
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