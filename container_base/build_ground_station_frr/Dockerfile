FROM ground-station-node:latest
LABEL authors="hs"

ENV container docker

USER root

RUN apt-get update
RUN apt-get install -y \
    autoconf \
    autogen \
    libtool \
    libjson-c-dev \
    libelf-dev \
    git autoconf automake libtool make libreadline-dev texinfo \
    pkg-config libpam0g-dev libjson-c-dev bison flex \
    libc-ares-dev python3-dev python3-sphinx \
    install-info build-essential libsnmp-dev perl \
    protobuf-c-compiler libprotobuf-c-dev \
    libcap-dev libelf-dev libunwind-dev libpcre2-dev \
    libyang-dev \
    libnl-3-dev

RUN touch /root/.Xauthority \
    && xauth add unix:0.0 MIT-MAGIC-COOKIE-1  ed38891ce0eb40149fbdc76e11c94e76
# install libyang
RUN git clone https://github.com/CESNET/libyang.git \
    && cd libyang \
    && git checkout v2.1.128 \
    && mkdir build; cd build \
    && cmake -D CMAKE_INSTALL_PREFIX:PATH=/usr \
        -D CMAKE_BUILD_TYPE:String="Release" .. \
    && make \
    && make install

ENV LDFLAGS="-Wl,--copy-dt-needed-entries"

# install frr-lofi
COPY frr-lofi-src /frr
RUN chmod -R 777 /frr \
    && cd /frr \
    && ./bootstrap.sh \
    && ./configure \
        --prefix=/usr \
        --includedir=\${prefix}/include \
        --bindir=\${prefix}/bin \
        --sbindir=\${prefix}/lib/frr \
        --libdir=\${prefix}/lib/frr \
        --libexecdir=\${prefix}/lib/frr \
        --localstatedir=/var/run/frr \
        --sysconfdir=/etc/frr \
        --with-moduledir=\${prefix}/lib/frr/modules \
        --enable-user=frr \
        --enable-group=frr \
        --enable-vty-group=frrvty \
        --enable-vtysh \
        --disable-staticd \
    && make -j$(nproc) \
    && make install -j$(nproc)

RUN cd /frr \
    && install -m 775 -o frr -g frr -d /var/log/frr \
    && install -m 775 -o frr -g frrvty -d /etc/frr \
    && install -m 640 -o frr -g frrvty tools/etc/frr/vtysh.conf /etc/frr/vtysh.conf \
    && install -m 640 -o frr -g frr tools/etc/frr/frr.conf /etc/frr/frr.conf \
    && install -m 640 -o frr -g frr tools/etc/frr/daemons.conf /etc/frr/daemons.conf \
    && install -m 640 -o frr -g frr tools/etc/frr/daemons /etc/frr/daemons \
    && install -m 644 tools/frr.service /etc/systemd/system/frr.service

COPY resources/daemons /etc/frr/daemons
RUN echo "log file /var/log/frr/hs_ospfd.log" >> /etc/frr/frr.conf \
    && echo "log record-priority" >> /etc/frr/frr.conf \
    && echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf && sysctl -p

COPY ./load_awareness/ /load_awareness
RUN chmod -R 777 /load_awareness \
    && /load_awareness/compile.sh
