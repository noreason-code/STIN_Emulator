currentpath=$(dirname "$(readlink -f "$0")")
cd $currentpath
gcc load_awareness.c -o load_awareness -lm $(pkg-config --cflags --libs libnl-3.0)