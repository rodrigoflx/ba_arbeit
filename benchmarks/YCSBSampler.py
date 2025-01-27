import jpype
import jpype.imports
from jpype.types import *

from sortedcontainers import SortedDict

from Sampler import Sampler
from matplotlib import pyplot as plt
import pandas as pd

from definitions import ROOT_DIR

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


if __name__ == "__main__":
    dict = SortedDict()
    jpype.startJVM(
        jvmpath="/usr/lib/jvm/default-java/lib/server/libjvm.so",
        classpath=[ROOT_DIR + "/jar/YCSB-Runner.jar"]) 
    sampler = YCSBSampler(1000, 10000, 1.1)
    for _ in range(10000):
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

    jpype.shutdownJVM()