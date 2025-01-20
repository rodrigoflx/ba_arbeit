CFLAGS = -O3 -funroll-loops

all: sysbench_wrapper.so

sysbench_wrapper.so: sysbench_wrapper.c sb_rand.c 
	$(CC) $(CFLAGS) -shared -fPIC -o $@ $^

clean:
	rm -f sysbench_wrapper.so