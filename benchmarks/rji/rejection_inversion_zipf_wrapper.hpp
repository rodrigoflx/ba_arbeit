#ifndef REJECTION_INVERSION_ZIPF_WRAPPER_HPP
#define REJECTION_INVERSION_ZIPF_WRAPPER_HPP

#include "RejectionInversionZipf.hpp"

extern "C" {

// Create a new instance of RejectionInversionZipfSampler
void* zipf_create(long numberOfElements, double exponent, unsigned long seed);

// Delete an instance of RejectionInversionZipfSampler
void zipf_destroy(void* sampler);

// Sample a number using the Zipf sampler
long zipf_sample(void* sampler);

}

#endif
