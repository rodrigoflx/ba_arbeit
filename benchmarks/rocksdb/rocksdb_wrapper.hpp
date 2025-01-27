#include "zipf.hpp"
#include <stdint.h>

extern "C" {
    void* zipf_create(double alpha, uint64_t seed);
    int64_t zipf_sample(void* wrapper, uint64_t max_key);
};