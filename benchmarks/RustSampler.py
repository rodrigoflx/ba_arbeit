from sortedcontainers import SortedDict
from Sampler import Sampler

from zipf_rust import PyZipf

import matplotlib.pyplot as plt
import pandas as pd


class RustSampler(Sampler):
    """
    Wrapper for the rust crate 'zipf'  
    """
    def __init__(self, n, samples, skew):
        super().__init__(n, samples, skew)
        self.sampler = PyZipf(n, skew)

    def sample(self) -> int:
        return self.sampler.sample()

    def benchmark(self) -> int:
        return self.sampler.benchmark(self.samples)


if __name__ == "__main__":
    n = 1000
    samples = 10 * n
    a = 1.1

    dict = SortedDict()
    sampler = PyZipf(n, a)
    
    for _ in range(samples):
        sample = sampler.sample()
        if sample in dict:
            dict[sample] += 1
        else:
            dict[sample] = 1 

    samples = pd.DataFrame(dict.items(), columns=['Value', 'Frequency'])

    # Plot histogram of values based on frequency
    plt.bar(samples["Value"], samples["Frequency"], log=True)
    plt.title("Zipfian Distribution")
    plt.xlabel("Value")
    plt.ylabel("Frequency (log scale)")
    plt.show()