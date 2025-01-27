#ifndef PG_WRAPPER_H
#define PG_WRAPPER_H

#include "stdint.h"
#include <stdlib.h>

#include "zipf.h"

void* zipf_create(uint64_t seed);
long zipf_sample(pg_prng_state* state, uint64_t n, double s);
void zipf_destroy(pg_prng_state* state);
long zipf_benchmark(pg_prng_state* state, uint64_t n, uint64_t samples, double s);

#endif 