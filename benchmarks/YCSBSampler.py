import definitions 
import jpype
import jpype.imports
from sortedcontainers import SortedDict

from Sampler import Sampler


class YCSBSampler(Sampler):
    """
    "Yahoo! Cloud Serving Benchmark" sampler wrapper
    """
    def __init__(self, n : int, samples: int, skew : float):
        super().__init__(n, samples, skew)

        jpype.startJVM(classpath=(definitions.ROOT_DIR + "/jar/YCSB-Runner.jar"))
        from com.zipfianRunner import ZipfianRunner
        self.zipf = ZipfianRunner(0, self.n, self.skew) 
    
    def sample(self) -> int:       
        return self.zipf.sample()
    
    def __del__(self):
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            