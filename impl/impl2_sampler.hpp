#ifndef IMPL2_SAMPLER_HPP
#define IMPLE2_SAMPLER_HPP

#include "sampler_i.hpp"

class impl2_sampler : public sampler_i {
    public:
        impl2_sampler(long range, double skew, long seed);
        long sample() override;
};

sampler_i* create_concrete_sampler(long range, long seed, double skew) {
    return new impl2_sampler(range, skew, seed);
}

#endif