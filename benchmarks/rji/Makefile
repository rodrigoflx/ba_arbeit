CXXFLAGS = -std=c++17 -O3 -Wall -Wextra -Werror

rji_sampler.so: rejection_inversion_zipf_wrapper.cpp
	$(CXX) $(CXXFLAGS) -shared -fPIC -o $@ $^