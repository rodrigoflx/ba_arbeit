all: rocksdb_wrapper.so

rocksdb_wrapper.so: rocksdb_wrapper.cpp
	$(CXX) -O3 -shared -fPIC -o rocksdb_wrapper.so rocksdb_wrapper.cpp

clean:
	rm -f rocksdb_wrapper.so