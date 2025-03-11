#include "zipf_generator_wrapper.hpp"
#include "ZipfGenerator.hpp"
#include <chrono>

using std::chrono::high_resolution_clock;
using std::chrono::duration_cast;
using std::chrono::duration;
using std::chrono::milliseconds;

struct ZipfWrapper {
    leanstore::utils::ZipfGenerator generator;

    ZipfWrapper(long numberOfElements, double exponent)
        : generator(numberOfElements, exponent) {}
};

void* zipf_create(long numberOfElements, double exponent, unsigned long seed) {
    return new ZipfWrapper(numberOfElements, exponent);
};

void zipf_destroy(void* wrapper) {
    delete static_cast<ZipfWrapper*>(wrapper);
};

long zipf_sample(void* wrapper) {
    auto* zipf = static_cast<ZipfWrapper*>(wrapper);
    return zipf->generator.rand();
};

long zipf_benchmark(void* wrapper, long samples) {
    auto* zipf = static_cast<ZipfWrapper*>(wrapper);
    
    auto t1 = high_resolution_clock::now();
    long sample;
    for (long i = 0; i < samples; i++) {
        sample = zipf->generator.rand();
    }
    sample++;
    auto t2 = high_resolution_clock::now();
    return duration_cast<milliseconds>(t2 - t1).count();
};
