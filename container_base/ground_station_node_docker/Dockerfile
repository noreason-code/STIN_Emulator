FROM ubuntu_modified:latest

USER root

ADD run.bash /etc

COPY ./ground_station_node /ground_station_node

# 进入ground_station_node目录
RUN cd /ground_station_node

# 给bootstrap.sh加上可执行的权限
RUN chmod +x ground_station_node/bootstrap.sh

CMD /bin/bash /etc/run.bash
