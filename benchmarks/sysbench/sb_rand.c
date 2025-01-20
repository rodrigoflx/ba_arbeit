#include "sb_rand.h"
#include <math.h>
#include <stdint.h>

sb_rng_state_t sb_rng_state;

double zipf_exp;
double zipf_s;
double zipf_hIntegralX1;

static double hIntegral(double x, double e);
static double hIntegralInverse(double x, double e);
static double h(double x, double e);
static double helper1(double x);
static double helper2(double x);

void sb_rand_init(void)
{
  zipf_s = 2 - hIntegralInverse(hIntegral(2.5, zipf_exp) - h(2, zipf_exp),
                                zipf_exp);
  zipf_hIntegralX1 = hIntegral(1.5, zipf_exp) - 1;

  // Seed PRNG 
  sb_rng_state[0] = (((uint64_t) random()) << 32) |
    (((uint64_t) random()) & UINT32_MAX);
  sb_rng_state[1] = (((uint64_t) random()) << 32) |
    (((uint64_t) random()) & UINT32_MAX);

}

uint32_t sb_rand_zipfian_int(uint32_t n, double e, double s,
                                    double hIntegralX1)
{
  /*
    The paper describes an algorithm for exponents larger than 1 (Algorithm
    ZRI).

    The original method uses

    H(x) = (v + x)^(1 - q) / (1 - q)

    as the integral of the hat function.  This function is undefined for q = 1,
    which is the reason for the limitation of the exponent.  If instead the
    integral function

    H(x) = ((v + x)^(1 - q) - 1) / (1 - q)

    is used, for which a meaningful limit exists for q = 1, the method works for
    all positive exponents.  The following implementation uses v = 0 and
    generates integral number in the range [1, numberOfElements].  This is
    different to the original method where v is defined to be positive and
    numbers are taken from [0, i_max].  This explains why the implementation
    looks slightly different.
  */
  const double hIntegralNumberOfElements = hIntegral(n + 0.5, e);

  for (;;)
  {
    double u = hIntegralNumberOfElements + sb_rand_uniform_double() *
      (hIntegralX1 - hIntegralNumberOfElements);
    /* u is uniformly distributed in (hIntegralX1, hIntegralNumberOfElements] */

    double x = hIntegralInverse(u, e);
    uint32_t k = (uint32_t) (x + 0.5);

    /*
      Limit k to the range [1, numberOfElements] if it would be outside due to
      numerical inaccuracies.
    */
    if (k < 1)
      k = 1;
    else if (k > n)
      k = n;

    /*
      Here, the distribution of k is given by:

      P(k = 1) = C * (hIntegral(1.5) - hIntegralX1) = C
      P(k = m) = C * (hIntegral(m + 1/2) - hIntegral(m - 1/2)) for m >= 2

      where C = 1 / (hIntegralNumberOfElements - hIntegralX1)
    */

    if (k - x <= s || u >= hIntegral(k + 0.5, e) - h(k, e))
    {
      /*
        Case k = 1:

        The right inequality is always true, because replacing k by 1 gives u >=
        hIntegral(1.5) - h(1) = hIntegralX1 and u is taken from (hIntegralX1,
        hIntegralNumberOfElements].

        Therefore, the acceptance rate for k = 1 is P(accepted | k = 1) = 1 and
        the probability that 1 is returned as random value is P(k = 1 and
        accepted) = P(accepted | k = 1) * P(k = 1) = C = C / 1^exponent

        Case k >= 2:

        The left inequality (k - x <= s) is just a short cut to avoid the more
        expensive evaluation of the right inequality (u >= hIntegral(k + 0.5) -
        h(k)) in many cases.

        If the left inequality is true, the right inequality is also true:
          Theorem 2 in the paper is valid for all positive exponents, because
          the requirements h'(x) = -exponent/x^(exponent + 1) < 0 and
          (-1/hInverse'(x))'' = (1+1/exponent) * x^(1/exponent-1) >= 0 are both
          fulfilled.  Therefore, f(x) = x - hIntegralInverse(hIntegral(x + 0.5)
          - h(x)) is a non-decreasing function. If k - x <= s holds, k - x <= s
          + f(k) - f(2) is obviously also true which is equivalent to -x <=
          -hIntegralInverse(hIntegral(k + 0.5) - h(k)), -hIntegralInverse(u) <=
          -hIntegralInverse(hIntegral(k + 0.5) - h(k)), and finally u >=
          hIntegral(k + 0.5) - h(k).

        Hence, the right inequality determines the acceptance rate: P(accepted |
        k = m) = h(m) / (hIntegrated(m+1/2) - hIntegrated(m-1/2)) The
        probability that m is returned is given by P(k = m and accepted) =
        P(accepted | k = m) * P(k = m) = C * h(m) = C / m^exponent.

      In both cases the probabilities are proportional to the probability mass
      function of the Zipf distribution.
      */

      return k;
    }
  }
}










/*
 * Helper functions for the Zipfian random number generator.
 */
 
static double h(double x, double e)
{
  return exp(-e * log(x));
}

static double hIntegral(double x, double e)
{
  const double logX = log(x);
  return helper2((1 - e) * logX) * logX;
}

static double hIntegralInverse(double x, double e)
{
  double t = x * (1 -e);
  if (t < -1)
  {
    /*
      Limit value to the range [-1, +inf).
      t could be smaller than -1 in some rare cases due to numerical errors.
    */
    t = -1;
  }

  return exp(helper1(t) * x);
}

static double helper1(double x)
{
  if (fabs(x) > 1e-8)
    return log1p(x) / x;
  else
    return 1 - x * (0.5 - x * (0.33333333333333333 - 0.25 * x));
}

/*
 Helper function that calculates (exp(x) - 1) / x.

 A Taylor series expansion is used, if x is close to 0.
*/

static double helper2(double x)
{
  if (fabs(x) > 1e-8)
    return expm1(x) / x;
  else
    return 1 + x * 0.5 * (1 + x * 0.33333333333333333 * (1 + 0.25 * x));
}