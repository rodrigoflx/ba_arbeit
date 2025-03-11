#ifndef ALIAS_SAMPLER_HPP
#define ALIAS_SAMPLER_HPP

#include <random>
#include <vector>
#include <cmath>
#include <algorithm>

/**
 * Base implementation of the sampler using rejection sampling.
 */
class alias_sampler {
public:
    alias_sampler(long range, double skew, long seed)
        : range(range), skew(skew), rng(seed), dist(0.0, 1.0) {
        this->H_n = computeNormalization(skew, range);
        this->table = buildCondensedTable(skew, range, 1e-8, H_n);
    }

    long sample() {
        double u = dist(rng);

        auto it = std::lower_bound(table.begin(), table.end(), u,
            [](const TableEntry& entry, double value) {
                return entry.cdf < value;
            });

        int lo = std::distance(table.begin(), it);
        double cdfStart = (lo == 0) ? 0.0 : table[lo-1].cdf;
        int k_start = (lo == 0) ? 1 : table[lo-1].k + 1;
        int k_end = table[lo].k;

        double cumulative = cdfStart;
        for (int k = k_start; k <= k_end; k++) {
            cumulative += precomputed_probs[k-1];
            if (cumulative >= u) {
                return k;
            }
        }

        return table.back().k;
    }

private:
    struct TableEntry {
        int k;
        double cdf;
    };

    long range;
    double skew;
    std::mt19937_64 rng;
    std::uniform_real_distribution<double> dist;
    double H_n;
    std::vector<TableEntry> table;
    std::vector<double> precomputed_probs;

    double computeNormalization(double s, int N) {
        double H = 0.0;
        for (int k = 1; k <= N; k++) {
            H += 1.0 / std::pow(k, s);
        }
        return H;
    }

    std::vector<TableEntry> buildCondensedTable(double s, int N, double delta, double H) {
        std::vector<TableEntry> table;
        table.reserve(static_cast<int>(1.0 / delta) + 10);

        double cumulative = 0.0;
        double lastStored = 0.0;

        precomputed_probs.reserve(N);
        for (int k = 1; k <= N; k++) {
            double pk = (1.0 / std::pow(k, s)) / H;
            precomputed_probs.push_back(pk);
            cumulative += pk;

            if ((cumulative - lastStored >= delta) || (k == N)) {
                table.emplace_back(TableEntry{k, cumulative});
                lastStored = cumulative;
            }
        }

        return table;
    }

};
    
#endif
    
    