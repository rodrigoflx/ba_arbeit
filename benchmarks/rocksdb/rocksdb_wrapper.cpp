#include "rocksdb_wrapper.hpp"

struct RocksDBStateWrapper {
    Random64 prng;
    RocksDBStateWrapper(uint64_t seed) : prng(seed) {}
};

void* zipf_create(double alpha, uint64_t seed) {
    InitializeHotKeyGenerator(alpha);
    return new RocksDBStateWrapper(seed);
}

int64_t zipf_sample(void* wrapper, uint64_t max_key) {
    auto* rdb_wrapper = static_cast<RocksDBStateWrapper*>(wrapper);
    double float_rand =
        (static_cast<double>(rdb_wrapper->prng.Next() % max_key)) / max_key;
    return GetOneHotKeyID(float_rand , max_key);
}