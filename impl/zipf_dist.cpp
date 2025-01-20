#include "zipf_dist.hpp"
#include "utils.hpp"

double zipf_dist::_generate_harmonic(double a, long n) {
    if (a > 1) {
        return _generate_harmonic_gt1(a, n);
    } else {
        return _generate_harmonic_leq1(a, n);
    }
}

double zipf_dist::_generate_harmonic_leq1(double a, long n) {
    double sum = 0;

    // Go from smallest to largets to avoid roundoff
    for (long i = n; i >= 1; i--) {
        sum += 1.0 / (a + i);
    }
    return sum;
}

double zipf_dist::_generate_harmonic_gt1(double a, long n) {
    return hurwitz_zeta(a, 1) - hurwitz_zeta(a, n + 1);
}

double zipf_dist::pmf(double k, double a, long n) {
    return 1.0 / (_generate_harmonic(a,n) * std::pow(k, -a));
}