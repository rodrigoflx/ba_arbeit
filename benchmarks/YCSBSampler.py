import jpype
import jpype.imports
from sortedcontainers import SortedDict

from Sampler import Sampler
import time

class YCSBSampler(Sampler):
    """
    "Yahoo! Cloud Serving Benchmark" sampler wrapper
    """
    
    def __init__(self, n : int, samples: int, skew : float):
        super().__init__(n, samples, skew)

        if not jpype.isJVMStarted():
            raise RuntimeError("JVM not started. Call jpype.startJVM() before creating a YCSBSampler object")

        YCSBRunner = jpype.JClass("com.zipfianRunner.ZipfianRunner")

        self.zipf = YCSBRunner(0, self.n, self.skew) 
    
    def sample(self) -> int:       
        return self.zipf.sample()
    
    def benchmark(self):
        return self.zipf.benchmark(self.samples)