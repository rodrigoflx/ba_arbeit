from Sampler import Sampler
import numpy as np

class NumpySampler(Sampler):
    """
    Wrapper for the Numpy sampler from Gabriel
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        self.sampler = np.random.zipf(self.skew, self.samples)

    def sample(self) -> int:
        return self.sampler