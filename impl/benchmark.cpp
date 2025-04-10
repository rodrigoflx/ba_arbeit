#include <benchmark/benchmark.h>
#include "marsaglia_sampler.hpp"

static void BM_ZipfThroughput(benchmark::State& state) {
    static bool initialized = false;
    unsigned long n = 10000000;
    double zipf_exp = 0.8;
    static marsaglia_sampler sampler = marsaglia_sampler(n, zipf_exp, 0);

    if (!initialized) {
        initialized = true;
    }
    
    for (auto _ : state) {
        long sample = sampler.sample();
        benchmark::DoNotOptimize(sample);
    }
    
    state.SetItemsProcessed(state.iterations());
}

BENCHMARK(BM_ZipfThroughput)
    ->MeasureProcessCPUTime(); 

BENCHMARK_MAIN();