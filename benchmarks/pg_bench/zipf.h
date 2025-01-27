#ifndef ZIPF_H
#define ZIPF_H

#include <stdint.h>
#include <math.h>
#include <stdbool.h>

#define UINT64CONST(x) UINT64_C(x)
#define unlikely(x) __builtin_expect((x) != 0, 0)


// PRNG state def and initializer
typedef struct pg_prng_state
{
	uint64_t		s0,
				    s1;
} pg_prng_state;


static uint64_t
splitmix64(uint64_t *state)
{
	/* state update */
	uint64_t		val = (*state += UINT64CONST(0x9E3779B97f4A7C15));

	/* value extraction */
	val = (val ^ (val >> 30)) * UINT64CONST(0xBF58476D1CE4E5B9);
	val = (val ^ (val >> 27)) * UINT64CONST(0x94D049BB133111EB);

	return val ^ (val >> 31);
}

bool
pg_prng_seed_check(pg_prng_state *state)
{
	/*
	 * If the seeding mechanism chanced to produce all-zeroes, insert
	 * something nonzero.  Anything would do; use Knuth's LCG parameters.
	 */
	if (unlikely(state->s0 == 0 && state->s1 == 0))
	{
		state->s0 = UINT64CONST(0x5851F42D4C957F2D);
		state->s1 = UINT64CONST(0x14057B7EF767814F);
	}

	/* As a convenience for the pg_prng_strong_seed macro, return true */
	return true;
}

void
pg_prng_seed(pg_prng_state* state, uint64_t seed)
{
	state->s0 = splitmix64(&seed);
	state->s1 = splitmix64(&seed);
	/* Let's just make sure we didn't get all-zeroes */
	(void) pg_prng_seed_check(state);
}


// PRNG functions 

static inline uint64_t
rotl(uint64_t x, int bits)
{
	return (x << bits) | (x >> (64 - bits));
}

static uint64_t
xoroshiro128ss(pg_prng_state *state)
{
	uint64_t		s0 = state->s0,
				sx = state->s1 ^ s0,
				val = rotl(s0 * 5, 7) * 9;

	/* update state */
	state->s0 = rotl(s0, 24) ^ sx ^ (sx << 16);
	state->s1 = rotl(sx, 37);

	return val;
}

double
pg_prng_double(pg_prng_state *state)
{
	uint64_t		v = xoroshiro128ss(state);

	/*
	 * As above, assume there's 52 mantissa bits in a double.  This result
	 * could round to 1.0 if double's precision is less than that; but we
	 * assume IEEE float arithmetic elsewhere in Postgres, so this seems OK.
	 */
	return ldexp((double) (v >> (64 - 52)), -52);
}

// Zipfian sampler
static int64_t computeInterativeZipfian(pg_prng_state *state, int64_t n, double s) {
    double		b = pow(2.0, s - 1.0);
	double		x,
				t,
				u,
				v;

	/* Ensure n is sane */
	if (n <= 1)
		return 1;

	while (1)
	{
		/* random variates */
		u = pg_prng_double(state);
		v = pg_prng_double(state);

		x = floor(pow(u, -1.0 / (s - 1.0)));

		t = pow(1.0 + 1.0 / x, s - 1.0);
		/* reject if too large or out of bound */
		if (v * x * (t - 1.0) / (b - 1.0) <= t / b && x <= n)
			break;
	}
	return (int64_t) x;
}
#endif ZIPF_H