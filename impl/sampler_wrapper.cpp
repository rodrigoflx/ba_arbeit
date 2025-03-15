#include <chrono>

volatile long dummy;

#ifdef USE_REJ_SAMPLER
    #include "rejection_sampler.hpp"
#elif defined(USE_RJI_SAMPLER)
    #include "rji_sampler.hpp"
#elif defined(USE_MARSAGLIA_SAMPLER)
    #include "marsaglia_sampler.hpp"
#else
    #error "No sampler implementation selected. Define USE_BASE_SAMPLER or USE_IMPL2_SAMPLER."
#endif

template <typename SamplerImpl>
class sampler_wrapper {
public:
    sampler_wrapper(long range, long seed, double skew)
        : sampler(range, skew, seed) {}

    long sample() {
        return sampler.sample();
    }

    long benchmark(long samples) {
        auto t1 = std::chrono::high_resolution_clock::now();
        for (long i = 0; i < samples; i++) {
            dummy = sampler.sample();
        }
        auto t2 = std::chrono::high_resolution_clock::now();
        return std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
    }

private:
    SamplerImpl sampler;
};

// Extern C API
extern "C" {
    // Template instantiations
#ifdef USE_BASE_SAMPLER
    using SelectedSampler = sampler_wrapper<rejection_sampler>;
#elif defined(USE_RJI_SAMPLER)
    using SelectedSampler = sampler_wrapper<rji_sampler>;
#elif defined(USE_MARSAGLIA_SAMPLER)
    using SelectedSampler = sampler_wrapper<marsaglia_sampler>;
#else
    #error "No sampler implementation selected"
#endif

    SelectedSampler* create_sampler(long range, long seed, double skew) {
        return new SelectedSampler(range, seed, skew);
    }

    void destroy_sampler(SelectedSampler* sampler) {
        delete sampler;
    }

    long sample(SelectedSampler* sampler) {
        return sampler->sample();
    }

    long benchmark(SelectedSampler* sampler, long samples) {
        return sampler->benchmark(samples);
    }
}
