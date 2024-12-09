#include "runner.hpp"
#include <iostream>

#define N 1000
#define SAMPLES N* 5

int main() {
    // Example usage of `sample_into_buckets` and `buckets_to_csv`
    buckets b = sample_into_buckets(N, SAMPLES, 0.8);

    for (int i = 0; i < 100; i++) {
        std::cout << "Bucket " << i << ": " << b.arr[i] << std::endl;
    }

    buckets_to_csv(10000, b, "output.csv");
    std::cout << "Buckets data written to output.csv" << std::endl;

    return 0;
}
