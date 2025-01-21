#ifndef IMPL2_SAMPLER_HPP
#define IMPL2_SAMPLER_HPP

#include <iostream>

class impl2_sampler {
public:
    impl2_sampler(long range, double skew, long seed)
        : range(range), skew(skew), seed(seed) {}

    long sample() {
        std::cout << "Not implemented yet" << std::endl;
        return 1;
    }

private:
    long range;
    double skew;
    long seed;
};

#endif
