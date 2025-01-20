#include <iostream>
#include <cmath>
#include <random>

#include "base_sampler.hpp"
#include "utils.hpp"

double bInvCdf(double p, double _skew, double _t) {
        if (p * _t <= 1)
            return p * _t;
        else
            return std::pow((p * _t) * (1 - _skew) + _skew, 1 / (1 - _skew) );
    }

base_sampler::base_sampler(long range, double skew, long seed) : sampler_i(range, skew, seed) {
    this->gen = std::mt19937(seed);
    this->_t = (std::pow(range, 1 - skew) - skew) / (1 - skew);
}

// Rejection-sampling algorithm
long base_sampler::sample() {
    // double H_n = _generate_harmonic(this->skew, this->range);

    // Set up uniform random number generators
    std::uniform_real_distribution<> uniform_dist(0.0, 1.0);

    while (true) {
        double invB = bInvCdf(uniform_dist(gen), this->skew, this->_t);
        long sampleX = (long)(invB + 1);
        double yRand = uniform_dist(gen);

        double ratioTop = std::pow(sampleX, - this->skew);
        double ratioBottom = sampleX <= 1 ? 1  / _t : std::pow(invB, -this->skew)  / _t;
        double rat = (ratioTop) / (ratioBottom * _t);

        if (yRand < rat) {
            return sampleX;
        }
    }
}