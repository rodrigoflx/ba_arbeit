# Define compiler and flags
CXX = g++
CXXFLAGS = -fPIC -std=c++20 -Wall -Wextra -O3
LDFLAGS = -shared 

# Define sources
SOURCES = sampler_wrapper.cpp

# Define target library
TARGET = libsampler.so

# Default to implementation 1
IMPL ?= 4
ifeq ($(IMPL), 1)
    CXXFLAGS += -DUSE_BASE_SAMPLER
else ifeq ($(IMPL), 2)
    CXXFLAGS += -DUSE_RJI_SAMPLER
else ifeq ($(IMPL), 3)
    CXXFLAGS += -DUSE_ALIAS_SAMPLER
else ifeq ($(IMPL), 4) 
    CXXFLAGS += -DUSE_CONT_SAMPLER
else
    $(error Invalid value for IMPL. Must be 1 (Base Sampler), 2 (Rejection-Inversion), 3 (Alias), 4 (Continous Approximation Sampler) )

endif

all: $(TARGET)

# Build the shared library
$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^

clean:
	rm -f $(TARGET)
