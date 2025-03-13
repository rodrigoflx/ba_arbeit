CFLAGS = -std=gnu99 -Wwrite-strings -Wall -Wdeclaration-after-statement -ffast-math  -D_GNU_SOURCE -include config-host.h  -Wimplicit-fallthrough -I. -I. -O3 -march=native -D_GNU_SOURCE -include config-host.h  -Wimplicit-fallthrough
CPPFLAGS = -std=c++14 -g -fpermissive -Wwrite-strings -Wall -Wdeclaration-after-statement -ffast-math  -D_GNU_SOURCE -include config-host.h  -Wimplicit-fallthrough -I. -I. -O3 -march=native -D_GNU_SOURCE -include config-host.h  -Wimplicit-fallthrough
SRC = zipf.c pattern.c strntol.c strcasestr.c rand.c

all: fio_zipf benchmark

fio_zipf: $(SRC) genzipf.c
	$(CC) $(CFLAGS) -o $@ $^ -lpthread -lm 

benchmark: $(SRC) benchmark.cpp
	$(CXX) $(CPPFLAGS) -o $@ $^ $(LDFLAGS) -lm -lpthread -lbenchmark

clean: 
	rm -f fio_zipf benchmark