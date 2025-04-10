#ifndef MARSAGLIA_SAMPLER_HPP
#define MARSAGLIA_SAMPLER_HPP

#include <random>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>

#include "zipf_dist.hpp"

/**
 * Implementation based on Marsaglia's Condensed Table lookup. Modification includes a MacLaurin approximated Harmonic Number
 * Heavily inspired by Apache Common's implementation:  https://github.com/apache/commons-rng/blob/master/commons-rng-sampling/src/main/java/org/apache/commons/rng/sampling/distribution/MarsagliaTsangWangDiscreteSampler.java
 * and the original paper: https://www.jstatsoft.org/article/view/v011i03 
 */
class marsaglia_sampler {
public:
    marsaglia_sampler(long range, double skew, long seed)
        : range(range), skew(skew), rng(seed), dist(0.0, (1 << 30) - 1), pmf(range) {
        
        // Precompute PMF table
        H_n = zipf_dist::_generate_harmonic(skew, range);
        for (int i = 1; i <= range; ++i) {
            pmf[i - 1] = 1.0 / (std::pow(i, skew) * H_n);
        }

        // Build tables
        build_tables();
    }

    long sample() {
       int j = dist(rng);
        if (j < t1_) {
            return table1_[j >> 24];
        } else if (j < t2_) {
            return table2_[(j - t1_) >> 18];
        } else if (j < t3_) {
            return table3_[(j - t2_) >> 12];
        } else if (j < t4_) {
            return table4_[(j - t3_) >> 6];
        } else {
            return table5_[j - t4_];
        } 
    }

private:
    long range;
    double skew;
    double H_n;
    std::vector<int> table1_, table2_, table3_, table4_, table5_;
    std::vector<double> pmf;
    int t1_, t2_, t3_, t4_;

    std::mt19937_64 rng;
    std::uniform_int_distribution<int> dist;

    void build_tables() {
        constexpr int64_t TOTAL = 1LL << 30; 
        double sum = 0.0;
        for (double p : pmf) {
            sum += p;
        }

        std::vector<int> prob(range);
        int64_t accum = 0;
        int maxIndex = 0;
        int maxVal = 0;

        int lastpInt = 0;
        int equals = 0;
        for (int i = 0; i < range; i++) {
            int pInt = static_cast<int>(pmf[i] * TOTAL / sum + 0.5);
            if (pInt == lastpInt) {
                equals++;
            } 
            lastpInt = pInt;

            prob[i] = pInt;
            accum += pInt;
            if (pInt > maxVal) {
                maxVal = pInt;
                maxIndex = i;
            }
        }

        if (accum < TOTAL) {
            prob[maxIndex] += TOTAL - accum;
        } else if (accum > TOTAL) {
            prob[maxIndex] -= accum - TOTAL;
        }

        size_t size1 = 0, size2 = 0, size3 = 0, size4 = 0, size5 = 0;
        for (int m : prob) {
            size1 += getBase64Digit(m, 1);
            size2 += getBase64Digit(m, 2);
            size3 += getBase64Digit(m, 3);
            size4 += getBase64Digit(m, 4);
            size5 += getBase64Digit(m, 5);
        }
        table1_.resize(size1);
        table2_.resize(size2);
        table3_.resize(size3);
        table4_.resize(size4);
        table5_.resize(size5);

        size_t pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0, pos5 = 0;
        for (int i = 0; i < range; i++) {
            int value = i;
            int d1 = getBase64Digit(prob[i], 1);
            int d2 = getBase64Digit(prob[i], 2);
            int d3 = getBase64Digit(prob[i], 3);
            int d4 = getBase64Digit(prob[i], 4);
            int d5 = getBase64Digit(prob[i], 5);
            for (int j = 0; j < d1; j++) {
                table1_[pos1++] = value;
            }
            for (int j = 0; j < d2; j++) {
                table2_[pos2++] = value;
            }
            for (int j = 0; j < d3; j++) {
                table3_[pos3++] = value;
            }
            for (int j = 0; j < d4; j++) {
                table4_[pos4++] = value;
            }
            for (int j = 0; j < d5; j++) {
                table5_[pos5++] = value;
            }
        }

        t1_ = table1_.size() << 24;
        t2_ = t1_ + (table2_.size() << 18);
        t3_ = t2_ + (table3_.size() << 12);
        t4_ = t3_ + (table4_.size() << 6);
    }

    static int getBase64Digit(int m, int k) {
        return (m >> (30 - 6 * k)) & 63;
    }
}; 

#endif
    
    