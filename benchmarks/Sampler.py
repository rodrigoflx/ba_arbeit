from abc import ABC, abstractmethod
from sortedcontainers import SortedDict

class Sampler(ABC):
    """
    Interface wrapper for different sampling backends
    """
    def __init__(self, n : int, samples : int, skew : float):
        self.n = n
        self.samples = samples
        self.skew = skew

    @abstractmethod
    def sample() -> int:
        """
        Sample a Zipfian distribution
        :return: int 
        """
        pass