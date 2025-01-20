#include "sb_rand.h"
#include "stdlib.h"
#include "sysbench_wrapper.h"

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