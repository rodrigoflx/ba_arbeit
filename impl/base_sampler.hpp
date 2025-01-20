#ifndef BASE_SAMPLER_HPP
#define BASE_SAMPLER_HPP

#include "sampler_i.hpp"
#include <random>

/** 
 *  Base class for samplers based on the following code: 
 *  https://jasoncrease.medium.com/rejection-sampling-the-zipf-distribution-6b359792cffa
 */
class base_sampler : public sampler_i {
    public:
        base_sampler(long range, double skew, long seed);
        long sample() override;
    private:
        double _t;
        std::mt19937 gen;
};

sampler_i* create_concrete_sampler(long range, long seed, double skew) {
    return new base_sampler(range, skew, seed);
}

#endif