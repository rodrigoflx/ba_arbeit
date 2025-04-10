# Define compiler and flags
CXX = g++
CXXFLAGS = -fPIC -std=c++20 -Wall -Wextra -O3 -funroll-loops -march=native -mtune=native

# Define sources
SOURCES = sampler_wrapper.cpp zipf_dist.cpp

# Define target library
TARGET = libsampler.so

# Default to implementation 1
IMPL ?= 1
ifeq ($(IMPL), 1)
    CXXFLAGS += -DUSE_REJ_SAMPLER
else ifeq ($(IMPL), 2)
    CXXFLAGS += -DUSE_RJI_SAMPLER
else ifeq ($(IMPL), 3) 
    CXXFLAGS += -DUSE_MARSAGLIA_SAMPLER
else
    $(error Invalid value for IMPL. Must be 1 (Base Sampler), 2 (Rejection-Inversion), 3 (Alias), 4 (Continous Approximation Sampler) )
endif

all: $(TARGET)

# Build the shared library
$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -shared -o $@ $^

benchmark: sampler_wrapper.cpp zipf_dist.cpp benchmark.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^ -lbenchmark

clean:
	rm -f *.so  cli benchmark
