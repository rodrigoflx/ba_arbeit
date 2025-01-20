#ifndef SYSBENCH_WRAPPER_H
#define SYSBENCH_WRAPPER_H

#include "stdint.h"

long n;

void zipf_create(long numberOfElements, double exponent);
long zipf_sample(); 

#endif // SYSBENCH_WRAPPER_H