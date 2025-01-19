# Define compiler and flags
CXX = g++
CXXFLAGS = -fPIC -std=c++20 -Wall -Wextra
LDFLAGS = -shared

# Define sources
BASE = base_sampler.cpp
IMPL2 = impl2_sampler.cpp
WRAPPER = sampler_wrapper.cpp

# Define target libraries
TARGETS = libsampler.so

# Default to implementation 1
IMPL ?= 1
ifeq ($(IMPL), 1)
    IMPLEMENTATION = $(BASE)
else ifeq ($(IMPL), 2)
    IMPLEMENTATION = $(IMPL2)
else
    $(error Invalid value for IMPL. Must be 1 or 2.)
endif

all: $(TARGETS)

# Build the shared library
libsampler.so: $(IMPLEMENTATION) $(WRAPPER)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^

clean:
	rm -f $(TARGETS)
