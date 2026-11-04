CC      ?= cc
CFLAGS  ?= -O2 -Wall -Wextra -std=c11
LDLIBS  := -lz

ifeq ($(shell uname -s),Darwin)
LDLIBS += -framework OpenGL
else
LDLIBS += -ldl
endif

BIN := retro-run

all: $(BIN) $(BIN)-x86_64

# Built aside and renamed into place: other processes may be running the old
# binary, and rewriting it in place invalidates its code signature under them.
$(BIN): retro-run.c
	$(CC) $(CFLAGS) -o .$@.new $< $(LDLIBS) && mv -f .$@.new $@

# For cores the buildbot only publishes for Intel: runs under Rosetta.
$(BIN)-x86_64: retro-run.c
	$(CC) -arch x86_64 $(CFLAGS) -o .$@.new $< $(LDLIBS) && mv -f .$@.new $@

clean:
	rm -f $(BIN) $(BIN)-x86_64

.PHONY: all clean
