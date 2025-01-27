#include "pg_wrapper.h"
#include "time.h"

void* zipf_create(uint64_t seed)
{
    pg_prng_state* state =  malloc(sizeof(pg_prng_state));
    if (state == NULL)
    {
        return NULL;
    }
    pg_prng_seed(state, seed);
    return (void *) state;
}

long zipf_sample(pg_prng_state* state, uint64_t n, double s)
{
    return computeInterativeZipfian(state, n, s);
}

void zipf_destroy(pg_prng_state* state)
{
    if (state == NULL)
    {
        return;
    }
    free(state);
} 

long zipf_benchmark(pg_prng_state* state,uint64_t n, uint64_t samples, double s)
{
    clock_t t1 = clock();
    for (long i = 0; i < samples; i++) {
        computeInterativeZipfian(state, n, s);
    }
    clock_t t2 = clock();
    return (t2 - t1) * 1000 / CLOCKS_PER_SEC;
}