FROM ubuntu_python:latest

USER root

# 添加run.bash
ADD run.bash /etc

# 拷贝satellite-node
COPY ./satellite_node /satellite_node

# 将netlink_test_userspace 进行拷贝
COPY ./netlink_test_userspace /netlink_test_userspace

RUN cd /netlink_test_userspace && cmake -S . -B build

RUN cd /netlink_test_userspace/build && make

# zhf add code
COPY ./udp_client_and_server_python /udp_client_and_server_python

# zhf add code
COPY ./tcp_client_and_server /tcp_client_and_server

# zhf add code
COPY ./udp_live_stream /udp_live_stream

COPY video_trans /video_trans

# 进入satellite-node目录
RUN cd /satellite_node

# 给bootstrap.sh加上可执行的权限
RUN chmod +x satellite_node/bootstrap.sh
#RUN apt-get update
#RUN apt-get install -y \
#    autoconf \
#    autogen \
#    libtool \
#    libjson-c-dev \
#    libelf-dev \
#    git autoconf automake libtool make libreadline-dev texinfo \
#    pkg-config libpam0g-dev libjson-c-dev bison flex \
#    libc-ares-dev python3-dev python3-sphinx \
#    install-info build-essential libsnmp-dev perl \
#    protobuf-c-compiler libprotobuf-c-dev \
#    libcap-dev libelf-dev libunwind-dev libpcre2-dev \
#    libyang-dev \
#    libnl-3-dev
#
#RUN touch /root/.Xauthority \
#    && xauth add unix:0.0 MIT-MAGIC-COOKIE-1  ed38891ce0eb40149fbdc76e11c94e76
#
## install libyang
#RUN git clone https://github.com/CESNET/libyang.git \
#    && cd libyang \
#    && git checkout v2.1.128 \
#    && mkdir build; cd build \
#    && cmake -D CMAKE_INSTALL_PREFIX:PATH=/usr \
#        -D CMAKE_BUILD_TYPE:String="Release" .. \
#    && make \
#    && make install
ENV LDFLAGS="-Wl,--copy-dt-needed-entries"

# 运行satellite-node
CMD /bin/bash /etc/run.bash