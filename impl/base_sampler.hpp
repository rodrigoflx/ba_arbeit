#ifndef BASE_SAMPLER_HPP
#define BASE_SAMPLER_HPP

#include "sampler_i.hpp"

/** 
 *  Base class for samplers based on the following code: 
 *  https://github.com/scipy/scipy/blob/v1.15.1/scipy/stats/_discrete_distns.py#L1295
 *  
 */
class base_sampler : public sampler_i {
    public:
        base_sampler(long range, double skew, long seed) : sampler_i(range, skew, seed) {};
        long sample() override;
    private:
        long range;
        double skew;
        long seed;
};

sampler_i* create_concrete_sampler(long range, long seed, double skew) {
    return new base_sampler(range, skew, seed);
}

#endif