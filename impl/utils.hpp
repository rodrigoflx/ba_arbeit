#include <iostream>
#include <cmath>
#include <vector>

// Precomputed Bernoulli numbers for approximation
const std::vector<double> B = {
    1.0, -0.5, 1.0 / 6.0, 0.0, -1.0 / 30.0, 0.0, 1.0 / 42.0, 0.0, -1.0 / 30.0
};

// Factorial function
long long factorial(int n) {
    long long result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// Hurwitz Zeta function approximation using Euler-Maclaurin formula
double hurwitz_zeta(double s, double a, int n = 8) {
    if (a <= 0.0 || s <= 1.0) {
        throw std::invalid_argument("Invalid input: a must be > 0 and s must be > 1.");
    }

    // \sum_{k=0}^{n-1} 1 / (a + k)^s
    double sum1 = 0.0;
    for (int k = 0; k < n; ++k) {
        sum1 += 1.0 / std::pow(a + k, s);
    }

    // (a + n)^(1-s) / (s - 1)
    double term2 = std::pow(a + n, 1.0 - s) / (s - 1.0);

    // -1 / (2 * (a + n)^s)
    double term3 = -1.0 / (2.0 * std::pow(a + n, s));

    // \sum_{k=1}^{\infty} B_{2k} / (2k)! * (s + 2k - 2) \prod_{j=0}^{2k-2} / (a + n)^(s + 2k - 2)
    double term4 = 0.0;
    for (int k = 1; k < B.size(); ++k) {
        double Bk = B[k * 2]; // Only even-indexed Bernoulli numbers are nonzero
        if (Bk == 0.0) continue;

        double factor = Bk / factorial(2 * k);
        double power = std::pow(a + n, s + 2 * k - 2);
        term4 += factor * (s + 2 * k - 2) / power;

        // Stop if the contribution becomes negligible
        if (std::abs(factor / power) < 1e-15) {
            break;
        }
    }

    return sum1 + term2 + term3 + term4;
}