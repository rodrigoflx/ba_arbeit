#include "sb_rand.h"
#include "sysbench_wrapper.h"
#include <time.h>

long n_sys;

void zipf_create(long numberOfElements, double exponent)
{
    zipf_exp = exponent;
    n_sys = numberOfElements;
    sb_rand_init();
}

long zipf_sample()
{
    return sb_rand_zipfian_int(n_sys, zipf_exp, zipf_s, zipf_hIntegralX1);
}

long zipf_benchmark(long samples)
{ 
    clock_t t1 = clock();
    long sample;
    for (long i = 0; i < samples; i++) {
        sample = sb_rand_zipfian_int(n_sys, zipf_exp, zipf_s, zipf_hIntegralX1);
    }
    clock_t t2 = clock();
    sample++;
    return (t2 - t1) * 1000 / CLOCKS_PER_SEC;
}
