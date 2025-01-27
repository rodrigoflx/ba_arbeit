#ifndef SYSBENCH_WRAPPER_H
#define SYSBENCH_WRAPPER_H

#include "stdint.h"

long n;

void zipf_create(long numberOfElements, double exponent);
long zipf_sample();
long zipf_benchmark(long samples); 

#endif // SYSBENCH_WRAPPER_H