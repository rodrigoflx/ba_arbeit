#ifndef BASE_SAMPLER_HPP
#define BASE_SAMPLER_HPP

#include <random>

/**
 * Base implementation of the sampler using rejection sampling, due to Jason Crease (https://jasoncrease.medium.com/rejection-sampling-the-zipf-distribution-6b359792cffa)
 * with optimizations inspired on https://docs.rs/rand_distr/latest/src/rand_distr/zipf.rs.html
 */
class base_sampler {
public:
    base_sampler(long range, double skew, long seed)
        : range(range), skew(skew), seed(seed), gen(seed),
          one_minus_skew(1.0 - skew),
          inv_one_minus_skew(1.0 / (1.0 - skew)),
          inv_max(1.0 / (std::mt19937_64::max() + 1.0)) 
    {
        _t = (std::pow(range, one_minus_skew) - skew) * inv_one_minus_skew;
    }

    long sample() {
        while (true) {
            double pt = std::fma(gen(), _t, 0.0);

            double invB_temp = std::pow(pt * one_minus_skew + skew, inv_one_minus_skew);
            double invB = (pt <= 1.0) ? pt : invB_temp;

            const long sampleX = static_cast<long>(invB) + 1;
            
            // Early exit for common case (sampleX=1)
            if (sampleX == 1) return 1;

            const double yRand = gen() * inv_max;

            double rat = (sampleX <= 1) ? 1.0 : std::exp(skew * std::log(invB / sampleX)); 
            
            if (yRand < rat) return sampleX;
        }
    }

private:
    const long range;
    const double skew;
    const long seed;
    const double one_minus_skew;    // 1.0 - skew
    const double inv_one_minus_skew; // 1.0/(1.0 - skew)
    const double inv_max;           // 1.0/(2^64)
    
    double _t;
    std::mt19937_64 gen;
};

#endif
