from Sampler import Sampler
from sortedcontainers import SortedDict
from definitions import ROOT_DIR

import ctypes
from ctypes import POINTER, c_uint64, c_double, c_uint, c_bool, Structure

class ZipfState(Structure):
    _fields_ = [
        ("nranges", c_uint64),
        ("theta", c_double),
        ("zeta2", c_double),
        ("zetan", c_double),
        ("pareto_pow", c_double),
        ("rand", ctypes.c_uint8 * 16),
        ("rand_off", c_uint64),
        ("disable_hash", c_bool),
    ]

lib = ctypes.CDLL(ROOT_DIR + "/shared/zipf.so")

# Bind zipf_init
lib.zipf_init.argtypes = [POINTER(ZipfState), c_uint64, c_double, c_double, c_uint]
lib.zipf_init.restype = None

# Bind zipf_next
lib.zipf_next.argtypes = [POINTER(ZipfState)]
lib.zipf_next.restype = c_uint64

# Bind pareto_init
lib.pareto_init.argtypes = [POINTER(ZipfState), c_uint64, c_double, c_double, c_uint]
lib.pareto_init.restype = None

# Bind pareto_next
lib.pareto_next.argtypes = [POINTER(ZipfState)]
lib.pareto_next.restype = c_uint64

# Bind zipf_disable_hash
lib.zipf_disable_hash.argtypes = [POINTER(ZipfState)]
lib.zipf_disable_hash.restype = None

# Bind zipf_benchmark
lib.zipf_benchmark.argtypes = [POINTER(ZipfState), c_uint64]
lib.zipf_benchmark.restype = c_uint64


class FIOSampler(Sampler):
    """
    "Flexible I/O Tester" sampler wrapper
    """
    def __init__(self, n: int, samples: int, skew: float):
        super().__init__(n, samples, skew)
        self.zs = ZipfState()
        lib.zipf_init(self.zs, self.n, self.skew, -1, 1)
    
    def sample(self) -> int:
        return lib.zipf_next(self.zs)
    
    def benchmark(self) -> int:
        return lib.zipf_benchmark(self.zs, self.samples)