FROM satellite-node:latest

LABEL mantainer="hs" description="LoFi image"

ENV container docker

USER root
# add frr users and groups
#RUN groupadd -r -g 92 frr \
#    && groupadd -r -g 85 frrvty \
#    && adduser --system --ingroup frr --home /var/run/frr/ \
#        --gecos "FRR suite" --shell /sbin/nologin frr \
#    && usermod -a -G frrvty frr
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
    # && systemctl enable frr
COPY resources/daemons /etc/frr/daemons
RUN echo "log file /var/log/frr/hs_ospfd.log" >> /etc/frr/frr.conf \
    && echo "log record-priority" >> /etc/frr/frr.conf \
    && echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf && sysctl -p

COPY ./load_awareness/ /load_awareness
RUN chmod -R 777 /load_awareness \
    && /load_awareness/compile.sh 


# copied from https://github.com/robertdebock/docker-ubuntu-systemd/blob/focal/Dockerfile
# Enable systemd.
# RUN apt-get update ; \
#     apt-get install -y systemd systemd-sysv kmod; \
#     apt-get clean ; \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* ; \
#     cd /lib/systemd/system/sysinit.target.wants/ ; \
#     ls | grep -v systemd-tmpfiles-setup | xargs rm -f $1 ; \
#     rm -f /lib/systemd/system/multi-user.target.wants/* ; \
#     rm -f /etc/systemd/system/*.wants/* ; \
#     rm -f /lib/systemd/system/local-fs.target.wants/* ; \
#     rm -f /lib/systemd/system/sockets.target.wants/*udev* ; \
#     rm -f /lib/systemd/system/sockets.target.wants/*initctl* ; \
#     rm -f /lib/systemd/system/basic.target.wants/* ; \
#     rm -f /lib/systemd/system/anaconda.target.wants/* ; \
#     rm -f /lib/systemd/system/plymouth* ; \
#     rm -f /lib/systemd/system/systemd-update-utmp*

# block some service from running
# added by sqsq
# RUN systemctl mask \
#     dev-hugepages.mount \
#     sys-fs-fuse-connections.mount \
#     sys-kernel-config.mount \
#     display-manager.service \
#     getty@.service \
#     systemd-logind.service \
#     systemd-remount-fs.service \
#     getty.target \
#     graphical.target \ 
#     systemd-journald.service \ 
#     systemd-timesyncd.service

# VOLUME [ "/sys/fs/cgroup" ]

# CMD ["/lib/systemd/systemd"]
# CMD ["/bin/bash", "-c", "while true; do :; done"]
#CMD ["/bin/bash", "/monitor_network.sh"]

# maunally starting: 
# docker run \
#   --tty \
#   --privileged \
#   --volume /sys/fs/cgroup:/sys/fs/cgroup:ro \
#   robertdebock/ubuntu
