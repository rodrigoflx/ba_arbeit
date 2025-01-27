#include <stdint.h>
#include <math.h>
#include <vector>
#include <random>

std::vector<double> sum_probs(100001);
constexpr int64_t zipf_sum_size = 100000;

// A good 64-bit random number generator based on std::mt19937_64
class Random64 {
private:
std::mt19937_64 generator_;

public:
explicit Random64(uint64_t s) : generator_(s) {}

// Generates the next random number
uint64_t Next() { return generator_(); }

// Returns a uniformly distributed value in the range [0..n-1]
// REQUIRES: n > 0
uint64_t Uniform(uint64_t n) {
  return std::uniform_int_distribution<uint64_t>(0, n - 1)(generator_);
}

// Randomly returns true ~"1/n" of the time, and false otherwise.
// REQUIRES: n > 0
bool OneIn(uint64_t n) { return Uniform(n) == 0; }

// Skewed: pick "base" uniformly from range [0,max_log] and then
// return "base" random bits.  The effect is to pick a number in the
// range [0,2^max_log-1] with exponential bias towards smaller numbers.
uint64_t Skewed(int max_log) {
  return Uniform(uint64_t(1) << Uniform(max_log + 1));
}
};

void InitializeHotKeyGenerator(double alpha) {
double c = 0;
for (int64_t i = 1; i <= zipf_sum_size; i++) {
  c = c + (1.0 / std::pow(static_cast<double>(i), alpha));
}
c = 1.0 / c;

sum_probs[0] = 0;
for (int64_t i = 1; i <= zipf_sum_size; i++) {
  sum_probs[i] =
      sum_probs[i - 1] + c / std::pow(static_cast<double>(i), alpha);
}
}

int64_t GetOneHotKeyID(double rand_seed, int64_t max_key) {
int64_t low = 1, mid, high = zipf_sum_size, zipf = 0;
while (low <= high) {
  mid = (low + high) / 2;
  if (sum_probs[mid] >= rand_seed && sum_probs[mid - 1] < rand_seed) {
    zipf = mid;
    break;
  } else if (sum_probs[mid] >= rand_seed) {
    high = mid - 1;
  } else {
    low = mid + 1;
  }
}
int64_t tmp_zipf_seed = zipf * max_key / zipf_sum_size;
Random64 rand_local(tmp_zipf_seed);
return rand_local.Next() % max_key;
}

