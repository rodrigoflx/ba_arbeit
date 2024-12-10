#ifndef RUNNER_HPP
#define RUNNER_HPP

#include "ZipfGenerator.hpp"
#include <string>

struct buckets {
    long arr[100];
    long sum;
};

buckets sample_into_buckets(long n, long samples, double alpha);
void buckets_to_csv(long n, buckets buckets_, const std::string& filepath);

#endif // RUNNER_HPP
