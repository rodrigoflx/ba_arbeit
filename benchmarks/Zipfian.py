import math
import matplotlib.pyplot as plt
import numpy as np

class Zipfian():
    def __init__(self, N : int, s : float):
        self.N = N
        self.s = s
        self.Hn = Zipfian.generalizedHarmonic_approx(self.N, self.s)


    @staticmethod
    def generalizedHarmonic(n, s):
        return sum([1 / math.pow(i, s) for i in range(1, n+1)])

    @staticmethod
    def generalizedHarmonic_approx(n, s):
        return (math.pow(n, -s+1) - 1) / (1-s) + 0.5 + math.pow(n,-s) / 2 + s/12 - math.pow(n, -1-s) * s / 12

    def pmf(self, i : int):
        return 1 / math.pow(i, self.s) / self.Hn

    def plot_log_log(self):
        """Plots the PMF of the Zipfian distribution in log-log scale along with the fitted line. The slope should be equal to -s"""
        x = range(1, self.N+1)
        y = [self.pmf(i) for i in x]
        plt.plot(x, y, label='Zipf PMF')
        plt.xscale('log')
        plt.yscale('log')
        log_x = [math.log(i) for i in x]
        log_y = [math.log(p) for p in y]

        slope, intercept = np.polyfit(log_x, log_y, 1)
        
        plt.plot(x, [math.exp(intercept) * i**slope for i in x], label=f'Slope: {slope:.2f}', linestyle='--')
        plt.legend()
        plt.show()

    def plot(self):
        """Plots the PMF of the Zipfian distribution"""
        x = range(1, self.N+1)
        y = [self.pmf(i) for i in x]
        plt.plot(x, y, label='Zipf PMF')
        plt.legend()
        plt.show()

class ValidationZipfian():
    @staticmethod
    def checkNormalization(zipf : Zipfian):
        """Calculates the sum of the PMF of the Zipfian distribution. It should be very near 1"""
        sum = 0
        for i in range(1, zipf.N+1):
            sum += zipf.pmf(i)
        return sum
    
    @staticmethod
    def checkHarmonicNumber(zipf : Zipfian):
        """Calculates the difference between the generalized harmonic number and the approximation"""
        s = zipf.s
        N = zipf.N
        H_n = sum([1 / math.pow(i, s) for i in range(1, N+1)])
        return abs(H_n - zipf.Hn) 

    @staticmethod
    def checkAgainstScipy(zipf: Zipfian):
        """Calculates total variation distance between the PMF of the Zipfian distribution and the scipy implementation"""
        from scipy.stats import zipf as scipy_zipf
        scipy_zipfian_ins = scipy_zipf(zipf.s)
        x = range(1, zipf.N+1)
        y = [zipf.pmf(i) for i in x]
        scipy_y = [scipy_zipfian_ins.pmf(i) for i in x]
        return sum([abs(y[i] - scipy_y[i]) for i in range(zipf.N)]) / zipf.N