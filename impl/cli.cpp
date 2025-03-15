#include <unistd.h>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <chrono>

#include "marsaglia_sampler.hpp"

bool parseArguments(int argc, char* argv[],
                    double &s, int &N, int &numSamples) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " s N num_samples\n"
                  << "  s          : Zipf exponent (e.g., 1.5)\n"
                  << "  N          : Maximum integer (support: 1 to N)\n"
                  << "  num_samples: Number of samples to generate\n";
        return false;
    }
    std::istringstream iss1(argv[1]);
    std::istringstream iss2(argv[2]);
    std::istringstream iss3(argv[3]);
    if (!(iss1 >> s)) {
        std::cerr << "Error: Invalid value for s.\n";
        return false;
    }
    if (!(iss2 >> N)) {
        std::cerr << "Error: Invalid value for N.\n";
        return false;
    }
    if (!(iss3 >> numSamples)) {
        std::cerr << "Error: Invalid value for num_samples.\n";
        return false;
    }
    return true;
}

int main(int argc, char* argv[]) {
    double s;
    int N, numSamples;

    // Parse command-line arguments.
    if (!parseArguments(argc, argv, s, N, numSamples)) {
        return EXIT_FAILURE;
    }

    std::random_device rd;
    marsaglia_sampler sampler(N,s, rd());


    long sample;
    for (long i = 0; i < numSamples; i++) {
        std::cout << "Sample " << sampler.sample() << std::endl;
    }

    return EXIT_SUCCESS;
}