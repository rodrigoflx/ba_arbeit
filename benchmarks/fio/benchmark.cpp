#include <benchmark/benchmark.h>
#include <random>
#include "zipf.h"

static void BM_ZipfThroughput(benchmark::State& state) {

    struct zipf_state zs;
    double theta = 0.5;
    int n = 1000000;


    // Do a one-time initialization.
    static bool initialized = false;
    if (!initialized) {
        zipf_init(&zs, n, theta, -1, std::random_device()());
        initialized = true;
    }
    
    for (auto _ : state) {
        uint64_t sample = zipf_next(&zs);
        benchmark::DoNotOptimize(sample);
    }
    
    state.SetItemsProcessed(state.iterations());
}

BENCHMARK(BM_ZipfThroughput)
    ->MeasureProcessCPUTime(); // Optional: choose real time if needed with ->UseRealTime()

BENCHMARK_MAIN();
