from Sampler import Sampler
import numpy as np
import time

class NumpySampler(Sampler):
    """
    Class is currently not working, don't use
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        self.result_arr = np.random.zipf(self.skew, self.samples)
        self.generator = (item for item in self.result_arr)

    def sample(self) -> int:
        try:
            return next(self.generator)
        except StopIteration:
            return None

    def benchmark(self) -> int:
        start = time.perf_counter()
        for i in range(self.samples):
            self.sampler[i]
        end = time.perf_counter()
        return (end - start) * 1_000  # Convert to milliseconds