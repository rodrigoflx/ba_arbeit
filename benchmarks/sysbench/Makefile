CFLAGS = -O3 -funroll-loops
LDFLAGS = -lbenchmark 

all: sysbench_wrapper.so benchmark

benchmark: benchmark.cpp sysbench_wrapper.c sb_rand.c 
	$(CXX) $(CFLAGS) -o $@ $^ $(LDFLAGS)

sysbench_wrapper.so: sysbench_wrapper.c sb_rand.c 
	$(CC) $(CFLAGS) -shared -fPIC -o $@ $^ 

clean:
	rm -f sysbench_wrapper.so benchmark