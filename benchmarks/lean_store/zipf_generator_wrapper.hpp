#ifndef ZIPF_GENERATOR_WRAPPER_H
#define ZIPF_GENERATOR_WRAPPER_H

#include <cstring> // For memset

extern "C" {
    void* zipf_create(long numberOfElements, double exponent, unsigned long seed);

    void zipf_destroy(void* sampler);

    long zipf_sample(void* sampler); 
}

#endif // ZIPF_GENERATOR_WRAPPER_H