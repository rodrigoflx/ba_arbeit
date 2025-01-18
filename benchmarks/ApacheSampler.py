import definitions 
import jpype
import jpype.imports
from sortedcontainers import SortedDict

from Sampler import Sampler


class ApacheCommonRunner(Sampler):
    """
    "ApacheCommon"'s RJI sampler wrapper
    """
    def __init__(self, n : int, samples: int, skew : float):
        super().__init__(n, samples, skew)

        jpype.startJVM(classpath=(definitions.ROOT_DIR + "/jar/ApacheCommonRunner.jar"))
        from zipf.zipfianRunner import ZipfianRunner
        self.gen = ZipfianRunner(0, self.n, self.skew)

    def sample(self) -> int:       
        return self.gen.sample()

    def __del__(self):
        if jpype.isJVMStarted():
            jpype.shutdownJVM()