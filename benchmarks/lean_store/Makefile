CXX = g++
CXXFLAGS = -std=c++20 -fPIC -pthread -rdynamic -fno-omit-frame-pointer -g3 -static-libstdc++ -O3

all: librunner.so

librunner.so: runner_wrapper.o runner.o zipf_generator.o random_generator.o
	$(CXX) -shared -o librunner.so runner_wrapper.o runner.o zipf_generator.o random_generator.o

runner_wrapper.o: runner_wrapper.cpp runner.hpp
	$(CXX) $(CXXFLAGS) -c runner_wrapper.cpp -o runner_wrapper.o

runner.o: runner.cpp RandomGenerator.hpp ZipfGenerator.hpp Exceptions.hpp Units.hpp
	$(CXX) $(CXXFLAGS) -c runner.cpp -o runner.o

zipf_generator.o: ZipfGenerator.cpp ZipfGenerator.hpp
	$(CXX) $(CXXFLAGS) -c ZipfGenerator.cpp -o zipf_generator.o

random_generator.o: RandomGenerator.cpp RandomGenerator.hpp
	$(CXX) $(CXXFLAGS) -c RandomGenerator.cpp -o random_generator.o

clean:
	rm -f *.o librunner.so
