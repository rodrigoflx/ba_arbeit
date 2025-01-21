#ifndef BASE_SAMPLER_HPP
#define BASE_SAMPLER_HPP

#include <random>

/**
 * Base implementation of the sampler using rejection sampling.
 */
class base_sampler {
public:
    base_sampler(long range, double skew, long seed)
        : range(range), skew(skew), seed(seed), gen(seed) {
        _t = (std::pow(range, 1 - skew) - skew) / (1 - skew);
    }

    long sample() {
        std::uniform_real_distribution<> uniform_dist(0.0, 1.0);

        while (true) {
            double invB = bInvCdf(uniform_dist(gen), skew, _t);
            long sampleX = static_cast<long>(invB + 1);
            double yRand = uniform_dist(gen);

            double ratioTop = std::pow(sampleX, -skew);
            double ratioBottom = sampleX <= 1 ? 1 / _t : std::pow(invB, -skew) / _t;
            double rat = (ratioTop) / (ratioBottom * _t);

            if (yRand < rat) {
                return sampleX;
            }
        }
    }

private:
    double bInvCdf(double p, double skew, double t) {
        return (p * t <= 1) ? (p * t) : std::pow((p * t) * (1 - skew) + skew, 1 / (1 - skew));
    }

    long range;
    double skew;
    long seed;
    double _t;
    std::mt19937 gen;
};

#endif
