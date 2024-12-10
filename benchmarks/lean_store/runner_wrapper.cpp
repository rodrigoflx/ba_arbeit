#ifndef RUNNER_WRAPPER_H
#define RUNNER_WRAPPER_H

#include "runner.hpp"
#include <cstring> // For memset

extern "C" {

    struct Buckets {
        long arr[100];
        long sum;
    };

    Buckets sample_into_buckets_wrapper(long n, long samples, double alpha) {
        std::cout << "sample_into_buckets_wrapper called with n=" << n
                  << ", samples=" << samples
                  << ", alpha=" << alpha << std::endl;

        Buckets result;
        try {
            buckets cpp_buckets = sample_into_buckets(n, samples, alpha);
            std::memcpy(result.arr, cpp_buckets.arr, sizeof(long) * 100);
            result.sum = cpp_buckets.sum;
        } catch (const std::exception& e) {
            std::cerr << "Exception in sample_into_buckets_wrapper: " << e.what() << std::endl;
        }
        return result;
    };

    void buckets_to_csv_wrapper(long n, Buckets buckets, const char* filepath) {
        struct buckets cpp_buckets;
        std::memcpy(cpp_buckets.arr, buckets.arr, sizeof(long) * 100);
        cpp_buckets.sum = buckets.sum;
        buckets_to_csv(n, cpp_buckets, std::string(filepath));
    };
}

#endif // RUNNER_WRAPPER_H
