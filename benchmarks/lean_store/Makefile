CXX = g++
CXXFLAGS = -std=c++20 -fPIC -pthread -rdynamic -fno-omit-frame-pointer -g3 -static-libstdc++ -O3

lean_sampler.so: zipf_generator_wrapper.o zipf_generator.o random_generator.o
	$(CXX) -shared -o $@ $^ $(CXXFLAGS)

zipf_generator_wrapper.o: zipf_generator_wrapper.cpp zipf_generator_wrapper.hpp
	$(CXX) $(CXXFLAGS) -c zipf_generator_wrapper.cpp -o zipf_generator_wrapper.o

zipf_generator.o: ZipfGenerator.cpp ZipfGenerator.hpp
	$(CXX) $(CXXFLAGS) -c ZipfGenerator.cpp -o zipf_generator.o

random_generator.o: RandomGenerator.cpp RandomGenerator.hpp
	$(CXX) $(CXXFLAGS) -c RandomGenerator.cpp -o random_generator.o

clean:
	rm -f *.o lean_sampler.so
