import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zipf

def generate_zipfian(domain, s):
    """
    Generate the theoretical probabilities of a Zipfian distribution using scipy.stats.

    Parameters:
    - domain: The range of integers in the Zipfian distribution (1, 2, ..., n).
    - s: The exponent parameter for the Zipfian distribution.

    Returns:
    - probabilities: List of probabilities for each value in the domain.
    """
    # Compute the theoretical Zipfian probabilities
    probabilities = zipf.pmf(domain, s)
    return probabilities

def plot_zipfian(domain, probabilities):
    """
    Plot the theoretical Zipfian probabilities.

    Parameters:
    - domain: The range of integers in the Zipfian distribution (1, 2, ..., n).
    - probabilities: The theoretical Zipfian probabilities.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(domain, probabilities, label="Theoretical Zipfian", marker='o', linestyle='-', color='blue')
    plt.xlabel("Value")
    plt.ylabel("Probability")
    plt.title("Theoretical Zipfian Distribution")
    plt.grid()
    plt.legend()
    plt.show()

# Parameters
n = 100 # Maximum value in the domain
s = 2.1 # Exponent parameter
domain = np.arange(1, n + 1)

# Generate theoretical probabilities
theoretical_probs = generate_zipfian(domain, s)

# Plot the theoretical Zipfian distribution
plot_zipfian(domain, theoretical_probs)


