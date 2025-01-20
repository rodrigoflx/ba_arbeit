#include <iostream>
#include "impl2_sampler.hpp"

impl2_sampler::impl2_sampler(long range, double skew, long seed) : sampler_i(range, skew, seed) {};

long impl2_sampler::sample() {
    std::cout << "Not implemented yet" << std::endl;
    return 1;
}