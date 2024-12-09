#include "runner.hpp"
#include <iostream>
#include <fstream>
#include <cstring>

buckets sample_into_buckets(long n, long samples, double alpha) {
    buckets bucket_;

    std::fill(std::begin(bucket_.arr), std::end(bucket_.arr), 0);
    bucket_.sum = samples;

    RejectionInversionZipfSampler rji_sampler(n, alpha);
    std::random_device rd;
    std::mt19937_64 rng(rd());
    long bucket_size = samples / 100;


    for (long i = 0; i < samples; i++) {
        long sample = rji_sampler.sample(rng);
        bucket_.arr[sample / bucket_size]++;
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
