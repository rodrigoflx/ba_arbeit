#include "sampler_i.hpp"

// Forward declare the factory function
sampler_i* create_concrete_sampler(long range, long seed, double skew);

extern "C" {

void* create_sampler(long range, long seed, double skew) {
    return create_concrete_sampler(range, seed, skew);
}

void destroy_sampler(void* sampler) {
    delete static_cast<sampler_i*>(sampler);
}

long sample(void* sampler) {
    sampler_i* s = static_cast<sampler_i*>(sampler);
    return s->sample();
}
}
