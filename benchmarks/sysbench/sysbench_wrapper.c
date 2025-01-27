#include "sb_rand.h"
#include "sysbench_wrapper.h"
#include <time.h>


void zipf_create(long numberOfElements, double exponent)
{
    zipf_exp = exponent;
    n = numberOfElements;
    sb_rand_init();
}

long zipf_sample()
{
    return sb_rand_zipfian_int(n, zipf_exp, zipf_s, zipf_hIntegralX1);
}

long zipf_benchmark(long samples)
{ 
    clock_t t1 = clock();
    for (long i = 0; i < samples; i++) {
        sb_rand_zipfian_int(n, zipf_exp, zipf_s, zipf_hIntegralX1);
    }
    clock_t t2 = clock();
    return (t2 - t1) * 1000 / CLOCKS_PER_SEC;
}
