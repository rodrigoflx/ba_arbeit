CXX = g++
CXXFLAGS = -Wall -std=c++17 -fPIC

all: librunner.so runner_executable

# Build the shared library
librunner.so: runner_wrapper.o runner.o
	$(CXX) -shared -o librunner.so runner_wrapper.o runner.o

runner_wrapper.o: runner_wrapper.cpp runner.hpp
	$(CXX) $(CXXFLAGS) -c runner_wrapper.cpp -o runner_wrapper.o

runner.o: runner.cpp runner.hpp RejectionInversionZipf.hpp
	$(CXX) $(CXXFLAGS) -c runner.cpp -o runner.o

# Build the executable
runner_executable: runner_wrapper.o main.o runner.o
	$(CXX) -o runner_executable runner_wrapper.o main.o runner.o

main.o: main.cpp runner.hpp RejectionInversionZipf.hpp
	$(CXX) $(CXXFLAGS) -c main.cpp -o main.o

# Clean target
clean:
	rm -f librunner.so runner_executable runner_wrapper.o runner.o main.o


