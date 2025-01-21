from Sampler import Sampler
import numpy as np
import time

class NumpySampler(Sampler):
    """
    Wrapper for the Numpy sampler from Gabriel
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        self.sampler = np.random.zipf(self.skew, self.samples)

    def sample(self) -> int:
        return self.sampler

    def benchmark(self) -> int:
        start = time.perf_counter()
        for i in range(self.samples):
            self.sampler[i]
        end = time.perf_counter()
        return (end - start) * 1_000  # Convert to milliseconds