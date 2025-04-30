in this folder,
load_awareness.c uses libnl to send/receive netlink messages to/from kernel.
and change the ospf cost configuration in FRRouting if needed.

compile load_awareness.c: gcc load_awareness.c -o sample `pkg-config --cflags --libs libnl-3.0 libnl-route-3.0 libpcap`