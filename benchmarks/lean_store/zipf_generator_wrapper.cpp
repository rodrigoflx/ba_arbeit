#include "zipf_generator_wrapper.hpp"
#include "ZipfGenerator.hpp"

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
