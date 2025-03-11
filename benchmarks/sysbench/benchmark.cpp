#include <benchmark/benchmark.h>
#include "sb_rand.h"
#include "sysbench_wrapper.h"

extern long n_sys;

static void BM_ZipfThroughput(benchmark::State& state) {
    static bool initialized = false;
    if (!initialized) {
        zipf_create(10000000, 1.0); 
        initialized = true;
    }
    
    for (auto _ : state) {
        long sample = sb_rand_zipfian_int(n_sys, zipf_exp, zipf_s, zipf_hIntegralX1);
        benchmark::DoNotOptimize(sample);
    }
    
    state.SetItemsProcessed(state.iterations());
}

BENCHMARK(BM_ZipfThroughput)
    ->MeasureProcessCPUTime(); 

BENCHMARK_MAIN();
