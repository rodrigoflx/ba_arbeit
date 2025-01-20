#ifndef SB_RAND_H
#define SB_RAND_H

#include "stdint.h"
#include "xoroshiro128plus.h"
#include "stdlib.h"

typedef uint64_t sb_rng_state_t [2];

extern sb_rng_state_t sb_rng_state;

extern double zipf_exp;
extern double zipf_s;
extern double zipf_hIntegralX1;

void sb_rand_init(void);
uint32_t sb_rand_zipfian_int(uint32_t n, double e, double s, double hIntegralX1);

inline uint64_t sb_rand_uniform_uint64(void)
{
  return xoroshiro_next(sb_rng_state);
}

inline double sb_rand_uniform_double(void)
{
  const uint64_t x = sb_rand_uniform_uint64();
  const union { uint64_t i; double d; } u = { .i = UINT64_C(0x3FF) << 52 | x >> 12 };

  return u.d - 1.0;
}

#endif