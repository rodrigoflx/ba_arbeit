#ifndef BASE_SAMPLER_HPP
#define BASE_SAMPLER_HPP

#include <random>
#include <cmath> 

/**
 * Continuous approximation sampler based on the ideas exposed on:
 */
class cont_sampler {
public:
    cont_sampler(long range, double skew , unsigned int seed = std::random_device{}())
        : s(skew), range(range), rng(seed), uniform(0.0, 1.0) {}
    
    long sample() {
        double U = uniform(rng);
        double y = (std::pow(1.0 - U, -1.0 / (s - 1.0)) - 1.0);

        long k = static_cast<long>(std::floor(y)) + 1;
        return std::max(0L, std::min(k,range));
    }

private:
    double s;   
    long range;
    std::mt19937 rng;
    std::uniform_real_distribution<double> uniform;
};

#endif

