#ifndef RJI_SAMPLER_HPP
#define RJI_SAMPLER_HPP

#include <iostream>
#include <random>

#define TAYLOR_THRESHOLD 1e-8

class rji_sampler {
public:
    rji_sampler(long range, double skew, long seed)
        : range(range), exponent(skew), seed(seed) {
            hIntegralX1 = hIntegral(1.5) - 1;
            hIntegralNumberOfElements = hIntegral(range + 0.5);
            s = 2 - hIntegralInverse(hIntegral(2.5) - h(2));
            dist = std::uniform_real_distribution<double>(hIntegralX1, hIntegralNumberOfElements);
        }

    long sample() {
        while(true) {
            double u = 0;
             u = dist(this->rng);

            double x = hIntegralInverse(u);
            long k = (long)(x + 0.5);

            if (k < 1) {
                k = 1;
            } else if (k > range) {
                k = range;
            }

            if (k - x <= s || u >= hIntegral(k + 0.5) - h(k)) {
                return k;
            }
        }
    }

private:
    long range;
    double exponent;
    long seed;

    /* Private constants related to RJI */
    std::uniform_real_distribution<double> dist;
    std::mt19937_64 rng; 
    double s;
    double r;
    double hIntegralX1;
    double hIntegralNumberOfElements;

    /* Methods for calculating constants */
    inline double hIntegral(const double x) {
        const double logX = std::log(x);
        return helper2((1 - exponent) * logX) * logX;
    }

    inline double h(const double x) {
        return std::exp(-exponent * std::log(x));
    }

    double hIntegralInverse(const double x) {
        double t = x * (1 - exponent);
        if (t < -1) {
            t = -1;
        }
        return std::exp(helper1(t) * x);
    }

    inline static double helper1(const double x) {
        if (std::abs(x) > 1e-8) {
            return std::log1p(x) / x;
        } else {
            return 1 - x * (0.5 - x * (0.33333333333333333 - 0.25 * x));
        }
    }

    inline static double helper2(const double x) {
        if (std::abs(x) > 1e-8) {
            return std::expm1(x) / x;
        } else {
            return 1 + x * 0.5 *(1 + x * 0.33333333333333333 * (1 + 0.25 * x));
        }
    }
};

#endif
