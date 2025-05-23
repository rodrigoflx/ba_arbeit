#ifndef _LINUX_HASH_H
#define _LINUX_HASH_H

#include <inttypes.h>
#include "arch.h"
#include "compiler.h"

#define BITS_PER_LONG 64 

/* Fast hashing routine for a long.
   (C) 2002 William Lee Irwin III, IBM */

/*
 * Although a random odd number will do, it turns out that the golden
 * ratio phi = (sqrt(5)-1)/2, or its negative, has particularly nice
 * properties.
 *
 * These are the negative, (1 - phi) = (phi^2) = (3 - sqrt(5))/2.
 * (See Knuth vol 3, section 6.4, exercise 9.)
 */
#define GOLDEN_RATIO_32 0x61C88647
#define GOLDEN_RATIO_64 0x61C8864680B583EBull

static inline unsigned long __hash_long(uint64_t val)
{
	uint64_t hash = val;

#if BITS_PER_LONG == 64
	hash *= GOLDEN_RATIO_64;
#else
	/*  Sigh, gcc can't optimise this alone like it does for 32 bits. */
	uint64_t n = hash;
	n <<= 18;
	hash -= n;
	n <<= 33;
	hash -= n;
	n <<= 3;
	hash += n;
	n <<= 3;
	hash -= n;
	n <<= 4;
	hash += n;
	n <<= 2;
	hash += n;
#endif

	return hash;
}

static inline unsigned long hash_long(unsigned long val, unsigned int bits)
{
	/* High bits are more random, so use them. */
	return __hash_long(val) >> (BITS_PER_LONG - bits);
}

static inline uint64_t __hash_u64(uint64_t val)
{
	return val * GOLDEN_RATIO_64;
}
	
static inline unsigned long hash_ptr(void *ptr, unsigned int bits)
{
	return hash_long((uintptr_t)ptr, bits);
}

/*
 * Bob Jenkins jhash
 */

#define JHASH_INITVAL	GOLDEN_RATIO_32

static inline uint32_t rol32(uint32_t word, uint32_t shift)
{
	return (word << shift) | (word >> (32 - shift));
}

/* __jhash_mix -- mix 3 32-bit values reversibly. */
#define __jhash_mix(a, b, c)			\
{						\
	a -= c;  a ^= rol32(c, 4);  c += b;	\
	b -= a;  b ^= rol32(a, 6);  a += c;	\
	c -= b;  c ^= rol32(b, 8);  b += a;	\
	a -= c;  a ^= rol32(c, 16); c += b;	\
	b -= a;  b ^= rol32(a, 19); a += c;	\
	c -= b;  c ^= rol32(b, 4);  b += a;	\
}

/* __jhash_final - final mixing of 3 32-bit values (a,b,c) into c */
#define __jhash_final(a, b, c)			\
{						\
	c ^= b; c -= rol32(b, 14);		\
	a ^= c; a -= rol32(c, 11);		\
	b ^= a; b -= rol32(a, 25);		\
	c ^= b; c -= rol32(b, 16);		\
	a ^= c; a -= rol32(c, 4);		\
	b ^= a; b -= rol32(a, 14);		\
	c ^= b; c -= rol32(b, 24);		\
}

static inline uint32_t jhash(const void *key, uint32_t length, uint32_t initval)
{
	const uint8_t *k = key;
	uint32_t a, b, c;

	/* Set up the internal state */
	a = b = c = JHASH_INITVAL + length + initval;

	/* All but the last block: affect some 32 bits of (a,b,c) */
	while (length > 12) {
		a += *k;
		b += *(k + 4);
		c += *(k + 8);
		__jhash_mix(a, b, c);
		length -= 12;
		k += 12;
	}

	/* Last block: affect all 32 bits of (c) */
	/* All the case statements fall through */
	switch (length) {
	case 12: c += (uint32_t) k[11] << 24;	fio_fallthrough;
	case 11: c += (uint32_t) k[10] << 16;	fio_fallthrough;
	case 10: c += (uint32_t) k[9] << 8;	fio_fallthrough;
	case 9:  c += k[8];			fio_fallthrough;
	case 8:  b += (uint32_t) k[7] << 24;	fio_fallthrough;
	case 7:  b += (uint32_t) k[6] << 16;	fio_fallthrough;
	case 6:  b += (uint32_t) k[5] << 8;	fio_fallthrough;
	case 5:  b += k[4];			fio_fallthrough;
	case 4:  a += (uint32_t) k[3] << 24;	fio_fallthrough;
	case 3:  a += (uint32_t) k[2] << 16;	fio_fallthrough;
	case 2:  a += (uint32_t) k[1] << 8;	fio_fallthrough;
	case 1:  a += k[0];
		 __jhash_final(a, b, c);
		 fio_fallthrough;
	case 0: /* Nothing left to add */
		break;
	}

	return c;
}

#endif /* _LINUX_HASH_H */
