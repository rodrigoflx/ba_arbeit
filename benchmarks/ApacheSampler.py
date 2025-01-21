import jpype
import jpype.imports
from sortedcontainers import SortedDict

from Sampler import Sampler

class ApacheSampler(Sampler):
    """
    "ApacheCommon"'s RJI sampler wrapper
    """
    def __init__(self, n : int, samples: int, skew : float):
        super().__init__(n, samples, skew)

        if not jpype.isJVMStarted():
            raise RuntimeError("JVM not started. Call jpype.startJVM() before creating a ApacheSampler object")

        ApacheRunner = jpype.JClass("zipf.zipfianRunner.ZipfianRunner", initialize=False)
        self.gen = ApacheRunner(0, self.n, self.skew)

    def sample(self) -> int:       
        return self.gen.sample()

    def benchmark(self):
        return self.gen.benchmark(self.samples)