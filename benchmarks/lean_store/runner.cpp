#include "runner.hpp"
#include <iostream>
#include <fstream>
#include <cstring>
#include <algorithm>

buckets sample_into_buckets(long n, long samples, double alpha) {
    buckets bucket_;

    std::fill(std::begin(bucket_.arr), std::end(bucket_.arr), 0);
    bucket_.sum = samples;

    leanstore::utils::ZipfGenerator zipf_gen(n, 1.0 - (1.0/alpha));
    unsigned long bucket_size = n / 100;


    for (long i = 0; i < samples; i++) {
        uint64_t sample = zipf_gen.rand();
        uint64_t index = std::min(sample / bucket_size, 99UL);
        bucket_.arr[index]++;
    }

    return bucket_; 
}

void buckets_to_csv(long n, buckets buckets_, const std::string& filepath) {
    std::ofstream file(filepath);

    if (file.is_open()) {
        file << "bucket_num,cnt,rel_freq" << std::endl;

        for (int i = 0; i < 100; i++) {
            file << i << "," << buckets_.arr[i] << "," << buckets_.arr[i] /(double) n << std::endl;
        }

        file.close();
    } else {
        std::cerr << "Unable to open file with given name: " << filepath << std::endl;
    }
}
