from Sampler import Sampler
from collections import Counter
from definitions import ROOT_DIR
import matplotlib.pyplot as plt
import pandas as pd 

import ctypes
from ctypes import POINTER, c_uint64, c_double, c_uint, c_bool, Structure, Union

class Taus88_state(Structure):
    _fields_ = [
        ('s1', c_uint),
        ('s2', c_uint),
        ('s3', c_uint),
        ('s4', c_uint)
    ]

class Taus258_state(Structure):
    _fields_ = [
        ('s1', c_uint64),
        ('s2', c_uint64),
        ('s3', c_uint64),
        ('s4', c_uint64),
        ('s5', c_uint64)
    ]


class State(Union):
    _fields_ = [
        ("state32", Taus88_state),
        ("state64", Taus258_state)
    ]

class FRAND_STATE(Structure):
    _anonymous_ = ("u")
    _fields_ = [
        ("use64", c_uint),
        ("u", State)
    ]

class ZipfState(Structure):
    _fields_ = [
        ("nranges", c_uint64),
        ("theta", c_double),
        ("zeta2", c_double),
        ("zetan", c_double),
        ("pareto_pow", c_double),
        ("rand", FRAND_STATE),
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

if __name__ == "__main__":
    n = 10000
    samples = 10 * n
    a = 1.1

    counter = Counter()
    fio_sampler = FIOSampler(n, samples, a)
    
    for _ in range(samples):
        fio_sample = fio_sampler.sample()
        if fio_sample in counter:
            counter[fio_sample] += 1
        else:
            counter[fio_sample] = 1 

    sorted_values = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    
    df = pd.DataFrame([{'rank': rank, 'frequency': freq} for rank, (value, freq) in enumerate(sorted_values)])

    plt.bar(df["rank"], df["frequency"], log=True)
    plt.title("Zipfian Distribution")
    plt.xlabel("Value")
    plt.ylabel("Frequency (log scale)")
    plt.show()