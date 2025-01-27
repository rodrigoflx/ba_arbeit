all: pg_wrapper.so

pg_wrapper.so: pg_wrapper.c
	gcc -shared -fPIC -o pg_wrapper.so pg_wrapper.c -ldl -O3

clean:
	rm -f pg_wrapper.so