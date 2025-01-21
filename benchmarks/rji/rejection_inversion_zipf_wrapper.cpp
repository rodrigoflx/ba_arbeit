#include "rejection_inversion_zipf_wrapper.hpp"
#include <random>
#include <chrono>


// Wrapper struct to hold sampler and RNG
struct ZipfWrapper {
    RejectionInversionZipfSampler sampler;
    std::mt19937_64 rng;

    ZipfWrapper(long numberOfElements, double exponent, unsigned long seed)
        : sampler(numberOfElements, exponent), rng(seed) {}
};

// Create a new instance of RejectionInversionZipfSampler
void* zipf_create(long numberOfElements, double exponent, unsigned long seed) {
    return new ZipfWrapper(numberOfElements, exponent, seed);
}

// Delete an instance of RejectionInversionZipfSampler
void zipf_destroy(void* wrapper) {
    delete static_cast<ZipfWrapper*>(wrapper);
}

// Sample a number using the Zipf sampler
long zipf_sample(void* wrapper) {
    auto* zipf = static_cast<ZipfWrapper*>(wrapper);
    return zipf->sampler.sample(zipf->rng);
}

long zipf_benchmark(void* wrapper, long samples) {
    auto* zipf = static_cast<ZipfWrapper*>(wrapper);
    
    auto t1 = std::chrono::high_resolution_clock::now();
    for (long i = 0; i < samples; i++) {
        zipf->sampler.sample(zipf->rng);
    }
    auto t2 = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
}