# Define compiler and flags
CXX = g++
CXXFLAGS = -fPIC -std=c++20 -Wall -Wextra
LDFLAGS = -shared

# Define sources
SOURCES = sampler_wrapper.cpp

# Define target library
TARGET = libsampler.so

# Default to implementation 1
IMPL ?= 1
ifeq ($(IMPL), 1)
    CXXFLAGS += -DUSE_BASE_SAMPLER
else ifeq ($(IMPL), 2)
    CXXFLAGS += -DUSE_IMPL2_SAMPLER
else
    $(error Invalid value for IMPL. Must be 1 or 2.)
endif

all: $(TARGET)

# Build the shared library
$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^

clean:
	rm -f $(TARGET)
