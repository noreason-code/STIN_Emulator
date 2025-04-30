import time
from multiprocessing import Process
from multiprocessing.connection import Pipe
from loguru import logger
import os
from math import cos, sin, sqrt
from typing import Dict, List, Tuple
from const_var import *
from satellite_node import SatelliteNode
from global_var import networks,networks_ground,satellite_map,networks_user
from threading import Thread

# hs add
import redis
import multiprocessing
from docker_client import DockerClient
from pyroute2 import NetNS




def generate_submission_list_for_network_object_creation(missions, submission_size: int):
    submission_list = []
    for i in range(0, len(missions), submission_size):
        submission_list.append(missions[i:i + submission_size])
    return submission_list


def network_object_creation_submission(submission, send_pipe):
    for net_id, container_id1, container_id2 in submission:
        network_key = get_network_key(container_id1, container_id2)
        networks[network_key] = Network(net_id,
                                        container_id1,
                                        container_id2,
                                        NETWORK_DELAY,
                                        NETWORK_BANDWIDTH,
                                        NETWORK_LOSS)
    send_pipe.send("finished")

# hs add
def network_object_creation_submission_app(submission, send_pipe, docker_client):
    redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
    delay_satellite = int(redis_conn.get('delay_satellite'))
    bandwidth_satellite = str(int(redis_conn.get('bandwidth_satellite')))
    loss_satellite = str(int(redis_conn.get('loss_satellite')))
    for net_id, container_id1, container_id2 in submission:
        network_key = get_network_key(container_id1, container_id2)
        networks[network_key] = Network(net_id,
                                        container_id1,
                                        container_id2,
                                        delay_satellite,
                                        bandwidth_satellite,
                                        loss_satellite,
                                        docker_client,
                                        False)
    send_pipe.send("finished")

# hs add
def ground_network_object_creation(missions):
    ground_index = 0
    for net_id,container_id1,container_id2 in missions:
        networks_ground["ground_" + str(ground_index)] = Network(net_id,
                                                container_id1,
                                                container_id2,
                                                NETWORK_DELAY_GROUND,
                                                NETWORK_BANDWIDTH_GROUND,
                                                NETWORK_LOSS_GROUND)
        ground_index = ground_index + 1

    # print(networks_ground)

# hs add
def ground_network_object_creation_app(missions, docker_client):
    redis_conn = redis.Redis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD,db=REDIS_DB)
    delay_ground = int(redis_conn.get('delay_ground'))
    bandwidth_ground = str(int(redis_conn.get('bandwidth_ground')))
    loss_ground = str(float(redis_conn.get('loss_ground')))
    # ground_index = 0
    for net_id, container_id1, container_id2, ground_id in missions:
        networks_ground[ground_id] = Network(net_id,
                                                container_id1,
                                                container_id2,
                                                delay_ground,
                                                bandwidth_ground,
                                                loss_ground,
                                                docker_client,
                                             True)
        # ground_index = ground_index + 1

    # print(networks_ground)
def user_network_object_creation(missions, docker_client):
    for net_id, container_id1, container_id2, user_id in missions:
        networks_user[user_id] = Network(net_id,
                                                container_id1,
                                                container_id2,
                                                0,
                                                "50000",
                                                "0",
                                                docker_client,
                                                False)


def create_network_object_with_multiple_process(missions, submission_size, docker_client):
    # hs add
    redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)

    current_finished_submission_count = 0
    rcv_pipe, send_pipe = Pipe()
    submission_list = generate_submission_list_for_network_object_creation(missions, submission_size)
    logger.info(f"create_network_object_submission_size: {submission_size}")
    # hs modify
    if redis_conn.get('app_flag') == b'True':
        for single_submission in submission_list:
            singleThread = Thread(target=network_object_creation_submission_app, args=(single_submission, send_pipe, docker_client))
            singleThread.start()
    else:
        for single_submission in submission_list:
            singleThread = Thread(target=network_object_creation_submission, args=(single_submission, send_pipe))
            singleThread.start()
    while True:
        rcv_string = rcv_pipe.recv()
        if rcv_string == "finished":
            current_finished_submission_count += 1
            if current_finished_submission_count == len(submission_list):
                rcv_pipe.close()
                send_pipe.close()
                break


def get_laser_delay_ms(position1: dict, position2: dict) -> int:
    lat1, lon1, hei1 = position1[LATITUDE_KEY], position1[LONGITUDE_KEY], position1[HEIGHT_KEY] + R_EARTH
    lat2, lon2, hei2 = position2[LATITUDE_KEY], position2[LONGITUDE_KEY], position2[HEIGHT_KEY] + R_EARTH
    x1, y1, z1 = hei1 * cos(lat1) * cos(lon1), hei1 * cos(lat1) * sin(lon1), hei1 * sin(lat1)
    x2, y2, z2 = hei2 * cos(lat2) * cos(lon2), hei2 * cos(lat2) * sin(lon2), hei2 * sin(lat2)
    dist_square = (x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2  # UNIT: m^2
    # logger.info(f"distance: {int(sqrt(dist_square))} light speed: {LIGHT_SPEED}")
    return int(sqrt(dist_square) / LIGHT_SPEED)  # UNIT: ms
    # ZHF MODIFY
    # return 0


def get_network_key(container_id1: str, container_id2: str) -> str:
    if container_id1 > container_id2:
        container_id1, container_id2 = container_id2, container_id1
    return container_id1 + container_id2


class ContainerEntrypoint:
    def __init__(self, veth_name: str, container_id: str):
        self.veth_name = veth_name
        self.container_id = container_id


def get_bridge_interface_name(bridge_id: str) -> str:
    full_name = "br-" + bridge_id
    br_interfaces_str = os.popen(
        '''ip l | grep -e "br-" | awk 'BEGIN{FS=": "}{print $2}' ''').read()  # popen与system可以执行指令,popen可以接受返回对象
    interface_list = br_interfaces_str.split('\n')[:-1]
    for interface_name in interface_list:
        if full_name.startswith(interface_name, 0):
            return interface_name
    raise SystemError("Interface Not Found")


def get_vethes_of_bridge(interface_name: str, docker_client: DockerClient,pid_dict:dict, container_id1: str, container_id2: str, flag: int) -> list:
    command = "ip l | " \
              "grep -e \"veth\" | " \
              "grep \"%s\" | " \
              "awk \'BEGIN{FS=\": \"}{print $2}\' | " \
              "awk \'BEGIN{FS=\"@\"}{print $1\"\\n\"$2}\'" % interface_name
    veth_and_eth_list_str = os.popen(command).read()

    veth_and_eth_list = veth_and_eth_list_str.split("\n")[:-1]
    return_veth_and_eth_list = []
    veth_list = []
    ifindex_list = []
    eth_list = []
    inner_eth_dict = {}
    for i in range(len(veth_and_eth_list)):
        if i % 2 == 0:
            veth_list.append(veth_and_eth_list[i])
        else:
            ifindex_list.append(veth_and_eth_list[i])
    # logger.info(ifindex_list)
    if flag == 0 or len(ifindex_list) == 1:
        pass
    else:
        source_container_ifindex = int(float(ifindex_list[0][2:]))
        target_container_ifindex = int(float(ifindex_list[1][2:]))
        #new add
        container_id_list = [container_id1, container_id2]
        ifindex_list = [source_container_ifindex, target_container_ifindex]
        for container_id in container_id_list:
            for ifindex in ifindex_list:
                container_pid = pid_dict[container_id]
                netns_path = f'/proc/{container_pid}/ns/net'
                # get_eth_command = ["nsenter", "--net=%s" % netns_path, "ip l | grep \"%d: \" | awk \'BEGIN{FS=\": \"}{print $2}\' | awk \'BEGIN{FS=\"@\"}{print $1}\'" % ifindex]
                get_eth_command = "nsenter --net=%s \
                                   ip l | grep \"%d: \" | awk \'BEGIN{FS=\": \"}{print $2}\' | awk \'BEGIN{FS=\"@\"}{print $1}\'" % (netns_path, ifindex)
                # response = docker_client.client.containers.get(container_id).exec_run(get_eth_command)
                response = os.popen(get_eth_command).read()
                eth_name = response.split('\n')[0]


                if eth_name == '':
                    continue
                else:
                    inner_eth_dict[container_id] = eth_name
                    break

        # get_eth_command_source = ["sh", "-c", "ip l | grep \"%d: \" | awk \'BEGIN{FS=\": \"}{print $2}\' | awk \'BEGIN{FS=\"@\"}{print $1}\'" % source_container_ifindex]
        # response_source = docker_client.client.containers.get(container_id1).exec_run(get_eth_command_source)
        # source_eth_name = response_source.output.decode('utf-8').split('\n')[0]  # 获取source端对应的eth名字
        # eth_list.append(source_eth_name)
        # get_eth_command_target = ["sh", "-c", "ip l | grep \"%d: \" | awk \'BEGIN{FS=\": \"}{print $2}\' | awk \'BEGIN{FS=\"@\"}{print $1}\'" % target_container_ifindex]
        # response_target = docker_client.client.containers.get(container_id2).exec_run(get_eth_command_target)
        # target_eth_name = response_target.output.decode('utf-8').split('\n')[0]  # 获取target端对应的eth名字
        # eth_list.append(target_eth_name)

    return_veth_and_eth_list.append(veth_list)
    # return_veth_and_eth_list.append(eth_list)
    return_veth_and_eth_list.append([])
    return_veth_and_eth_list.append(inner_eth_dict)
    return return_veth_and_eth_list


class Network:

    def __init__(self, bridge_id: str,
                 container_id1: str,
                 container_id2: str,
                 time: int,
                 band_width: str,
                 loss_percent: str,
                 docker_client: DockerClient,
                 is_ground):
        # 为保证network key的唯一性，设置map中key的字符串拼接顺序为小id在前,大id在后
        self.br_id = bridge_id
        self.br_interface_name = get_bridge_interface_name(bridge_id)
        self.container_pid_dict = {}  # container_id -> container_pid
        command_get_container_pid_1 = "docker inspect --format=\'{{.State.Pid}}\' %s" % container_id1
        command_get_container_pid_2 = "docker inspect --format=\'{{.State.Pid}}\' %s" % container_id2
        container_pid_1 = os.popen(command_get_container_pid_1).read().strip()
        container_pid_2 = os.popen(command_get_container_pid_2).read().strip()
        self.container_pid_dict[container_id1] = container_pid_1
        self.container_pid_dict[container_id2] = container_pid_2
        temp_res = get_vethes_of_bridge(self.br_interface_name, docker_client,self.container_pid_dict, container_id1, container_id2, 1)
        self.veth_interface_list = temp_res[0]
        self.eth_interface_list = temp_res[1]   #已弃用
        self.delay = time
        self.bandwidth = band_width
        self.loss = loss_percent
        self.source_container = container_id1
        self.target_container = container_id2
        self.inner_eth_dict = temp_res[2]
        self.dirty = False
        self.is_ground = is_ground  #用于判断是否是GSL网络对象，如果是，则不更新OSPF cost
        # hs modify
        if len(self.veth_interface_list) != 2 and len(self.veth_interface_list) != 1:
            logger.warning(self.veth_interface_list)
            raise ValueError("wrong veth number of bridge")
        if len(self.veth_interface_list) == 2:
            self.veth_map = {
                container_id1: self.veth_interface_list[0],
                container_id2: self.veth_interface_list[1]
            }
        elif len(self.veth_interface_list) == 1:
            self.veth_map = {
                container_id1: self.veth_interface_list[0]
            }

        self.init_info()

    '''
    #!/bin/bash
    echo "add tbf and netem to eth0..."
    tc qdisc del dev eth0 root
    tc qdisc add dev eth0 root handle 1:0 tbf rate 80kbit burst 10k limit 10kbit
    tc qdisc add dev eth0 parent 2:0 handle 1:0 netem delay 100ms loss 10%
    tc qdisc show dev eth0
    '''

    def init_info(self):
        # hs modify
        if len(self.veth_interface_list) == 2:
            # bandwidth unit is kbytes/s integer
            command = "tc qdisc replace dev %s root handle 1:0 tbf rate %dkbit burst %dMbit limit %dkbit" % (
                self.veth_interface_list[0], int(self.bandwidth) * 8, 40, int(self.bandwidth) * 8)
            exec_res = os.popen(command).read()

            command = "tc qdisc add dev %s parent 1:0 handle 2:0 netem delay %dms loss %s" % (
                self.veth_interface_list[0], self.delay, self.loss)
            exec_res = os.popen(command).read()

            # bandwidth unit is kbytes/s integer
            command = "tc qdisc replace dev %s root handle 1:0 tbf rate %dkbit burst %dMbit limit %dkbit" % (
                self.veth_interface_list[1], int(self.bandwidth) * 8, 40, int(self.bandwidth) * 8)
            exec_res = os.popen(command).read()

            command = "tc qdisc add dev %s parent 1:0 handle 2:0 netem delay %dms loss %s" % (
                self.veth_interface_list[1], self.delay, self.loss)
            exec_res = os.popen(command).read()

    def update_info(self):
        if not self.dirty:
            return
        self.dirty = False
        command = "tc qdisc replace dev %s root handle 1:0 tbf rate %dkbit burst %dMbit limit %dkbit" % (
            self.veth_interface_list[0], int(self.bandwidth) * 8, 40, int(self.bandwidth) * 8)

        exec_res = os.popen(command).read()
        command = "tc qdisc replace dev %s parent 1:0 handle 2:0 netem delay %dms loss %s" % (
            self.veth_interface_list[0], self.delay, self.loss)

        exec_res = os.popen(command).read()
        # bandwidth unit is kbytes/s integer
        command = "tc qdisc replace dev %s root handle 1:0 tbf rate %dkbit burst %dMbit limit %dkbit" % (
            self.veth_interface_list[1], int(self.bandwidth) * 8, 40, int(self.bandwidth) * 8)

        exec_res = os.popen(command).read()
        command = "tc qdisc replace dev %s parent 1:0 handle 2:0 netem delay %dms loss %s" % (
            self.veth_interface_list[1], self.delay, self.loss)

        exec_res = os.popen(command).read()

    def update_delay_param(self, set_time: int):
        if set_time != self.delay:
            self.delay = set_time
            self.dirty = True

    # hs add
    # These functions are only used for experiments
    # def update_delay_param_exp(self, set_time: int):
    #     self.delay = set_time
    #     self.update_info_exp()
    #
    # def update_info_exp(self):
    #     command = "tc qdisc replace dev %s root handle 1:0 tbf rate %dkbit burst %dMbit limit %dkbit" % (
    #         self.veth_interface_list[0], int(self.bandwidth) * 8, 40, int(self.bandwidth) * 8)
    #     exec_res = os.popen(command).read()
    #     command = "tc qdisc replace dev %s parent 1:0 handle 2:0 netem delay %dms loss %s" % (
    #         self.veth_interface_list[0], self.delay, self.loss)
    #     exec_res = os.popen(command).read()
    #
    #     command = "tc qdisc replace dev %s root handle 1:0 tbf rate %dkbit burst %dMbit limit %dkbit" % (
    #         self.veth_interface_list[1], int(self.bandwidth) * 8, 40, int(self.bandwidth) * 8)
    #     exec_res = os.popen(command).read()
    #     command = "tc qdisc replace dev %s parent 1:0 handle 2:0 netem delay %dms loss %s" % (
    #         self.veth_interface_list[1], self.delay, self.loss)
    #     exec_res = os.popen(command).read()


    def update_bandwidth_param(self, band_width: str):
        if band_width != self.bandwidth:
            self.bandwidth = band_width
            self.dirty = True

    def update_loss_param(self, loss_percent: str):
        if loss_percent != self.loss:
            self.loss = loss_percent
            self.dirty = True

    def set_link_down(self, down_order_li: list):
        container_id_1 = self.source_container
        container_id_2 = self.target_container
        # 获取容器的pid
        container_pid_dict = {}     # container_id -> container_pid
        command_get_container_pid_1 = "docker inspect --format=\'{{.State.Pid}}\' %s" % container_id_1
        command_get_container_pid_2 = "docker inspect --format=\'{{.State.Pid}}\' %s" % container_id_2
        container_pid_1 = os.popen(command_get_container_pid_1).read().strip()
        container_pid_2 = os.popen(command_get_container_pid_2).read().strip()
        container_pid_dict[container_id_1] = container_pid_1
        container_pid_dict[container_id_2] = container_pid_2
        down_task_dict = {}     # container_id -> eth_name
        for i in range(len(down_order_li)):
            down_container_id = down_order_li[i]
            down_task_dict[down_container_id] = self.inner_eth_dict[down_container_id]
        # first_down_id = down_order_li[0]
        # second_down_id = down_order_li[1]
        # down_task_dict[first_down_id] = self.inner_eth_dict[first_down_id]
        # down_task_dict[second_down_id] = self.inner_eth_dict[second_down_id]

        for container_id, eth_name in down_task_dict.items():
            container_pid = container_pid_dict[container_id]
            netns_path = f'/proc/{container_pid}/ns/net'
            with NetNS(netns_path) as ns:
                idx = ns.link_lookup(ifname=eth_name)[0]
                ns.link('set', index=idx, state='down')
            # with open('./eth_down_record.txt', 'a') as f:
            #     f.write(container_id)
            #     f.write('\n')
            #     f.write(str(time.time()))
            #     f.write('\n')


    def set_link_up(self, up_order_li: list):
        container_id_1 = self.source_container
        container_id_2 = self.target_container
        # 获取容器的pid
        # container_pid_dict = {}  # container_id -> container_pid
        # command_get_container_pid_1 = "docker inspect --format=\'{{.State.Pid}}\' %s" % container_id_1
        # command_get_container_pid_2 = "docker inspect --format=\'{{.State.Pid}}\' %s" % container_id_2
        # container_pid_1 = os.popen(command_get_container_pid_1).read().strip()
        # container_pid_2 = os.popen(command_get_container_pid_2).read().strip()
        # container_pid_dict[container_id_1] = container_pid_1
        # container_pid_dict[container_id_2] = container_pid_2
        up_task_dict = {}  # container_id -> eth_name
        for i in range(len(up_order_li)):
            up_container_id = up_order_li[i]
            up_task_dict[up_container_id] = self.inner_eth_dict[up_container_id]
        # first_up_id = up_order_li[0]
        # second_up_id = up_order_li[1]
        # up_task_dict[first_up_id] = self.inner_eth_dict[first_up_id]
        # up_task_dict[second_up_id] = self.inner_eth_dict[second_up_id]

        for container_id, eth_name in up_task_dict.items():
            container_pid = self.container_pid_dict[container_id]
            netns_path = f'/proc/{container_pid}/ns/net'
            with NetNS(netns_path) as ns:
                idx = ns.link_lookup(ifname=eth_name)[0]
                ns.link('set', index=idx, state='up')
            with open('./eth_up_record.txt', 'a') as f:
                f.write(container_id)
                f.write('\n')
                f.write(str(time.time()))
                f.write('\n')


def network_update_worker(network : Network, docker_client):
    #hs add
    if not network.dirty:
        return
    network.update_info()
    if network.is_ground:
        pass
    else:
        container_id_source = network.source_container
        container_id_target = network.target_container
        new_delay = network.delay
        cost = new_delay * 10  # 根据latency自定义cost
        # source_eth_name = network.eth_interface_list[0]
        # target_eth_name = network.eth_interface_list[1]
        # config_cost_command_source = ["vtysh", "-c", "configure terminal", "-c", "interface %s" % source_eth_name, "-c", "ip ospf cost %d" % cost, "exit", "exit", "exit"]
        # docker_client.client.containers.get(container_id_source).exec_run(config_cost_command_source, detach=True)
        # config_cost_command_target = ["vtysh", "-c", "configure terminal", "-c", "interface %s" % target_eth_name, "-c", "ip ospf cost %d" % cost, "exit", "exit", "exit"]
        # docker_client.client.containers.get(container_id_target).exec_run(config_cost_command_target, detach=True)
        for container_id, eth_name in network.inner_eth_dict.items():
            set_cost_command = ["vtysh", "-c", "configure terminal", "-c", "interface %s" % eth_name, "-c",
                                "ip ospf cost %d" % cost, "exit", "exit", "exit"]
            docker_client.client.containers.get(container_id).exec_run(set_cost_command, detach=True)

def update_network_delay(position_data: dict, topo: dict, docker_client):
    for start_node_id in topo.keys():
        conn_array = topo[start_node_id]
        for target_node_id in conn_array:
            # print("Update %s and %s"%(start_node_id,target_node_id))
            delay = get_laser_delay_ms(position_data[start_node_id],position_data[target_node_id])
            container_id1 = satellite_map[start_node_id].container_id
            container_id2 = satellite_map[target_node_id].container_id
            network_obj = networks[get_network_key(container_id1,container_id2)]
            network_obj.update_delay_param(delay)
            # process = multiprocessing.Process(target=update_network_delay, args=(network_obj, docker_client))
            # process.start()
            thread = Thread(target=network_update_worker,args=(network_obj, docker_client))
            thread.start()

def generate_mission_for_update_network_delay(position_data: Dict[str, Dict[str, float]], topo: Dict[str, List[str]],
                                              satellite_map_tmp: Dict[str, SatelliteNode]):
    update_network_delay_missions = []
    for start_node_id in topo.keys():
        conn_array = topo[start_node_id]
        for target_node_id in conn_array:
            start_container_id = satellite_map_tmp[start_node_id].container_id
            target_container_id = satellite_map_tmp[target_node_id].container_id
            delay = get_laser_delay_ms(position_data[start_node_id], position_data[target_node_id])
            network_key = get_network_key(start_container_id, target_container_id)
            update_network_delay_missions.append(
                (network_key, delay)
            )
    return update_network_delay_missions


def generate_submission_list_for_update_network_delay(missions: List[Tuple[str, int]],
                                                      submission_size: int):
    submission_list = []
    for i in range(0, len(missions), submission_size):
        submission_list.append(missions[i:i + submission_size])
    return submission_list


def update_network_delay_with_single_process(submission: List[Tuple[str, int]], networks_tmp, send_pipe):
    for network_key, delay in submission:
        network = networks_tmp[network_key]
        network.update_delay_param(delay)
        network.update_info()
    send_pipe.send("finished")


def update_network_delay_with_multi_process(stop_process_state,
                                            networks_tmp,
                                            position_data: Dict[str, Dict[str, float]],
                                            topo: Dict[str, List[str]],
                                            satellite_map_tmp: Dict[str, SatelliteNode],
                                            submission_size: int,
                                            update_interval: int):
    # update count
    update_count = 0
    # generate missions
    missions = generate_mission_for_update_network_delay(position_data, topo, satellite_map_tmp)
    # generate submission list
    submission_list = generate_submission_list_for_update_network_delay(missions, submission_size)
    # submit
    while True:
        # store the start time
        start_time = time.time()
        if stop_process_state.value:
            break
        # current count
        current_count = 0
        # generate pipe
        rcv_pipe, send_pipe = Pipe()
        for submission in submission_list:
            # process = Process(target=update_network_delay_with_single_process,
            #                   args=(submission, networks_tmp, send_pipe))
            # process.start()
            singleThread = Thread(target=update_network_delay_with_single_process,
                                  args=(submission, networks_tmp, send_pipe))
            singleThread.start()
        # receive the result
        while True:
            rcv_string = rcv_pipe.recv()
            if rcv_string == "finished":
                current_count += 1
                # traverse all the process and kill them
                if current_count == len(submission_list):
                    send_pipe.close()
                    rcv_pipe.close()
                    break
        end_time = time.time()
        logger.info(f"update satellite network delay in {end_time - start_time}s")
        update_count += 1
        if update_count == 1:
            break
        time.sleep(update_interval)
    logger.success("update satellite network delay process finished")

# hs add
def update_network_delay_with_multi_process_app(networks_tmp,
                                            position_data: Dict[str, Dict[str, float]],
                                            topo: Dict[str, List[str]],
                                            satellite_map_tmp: Dict[str, SatelliteNode],
                                            submission_size: int,
                                            update_interval: int
                                            ):
    redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
    # update count
    update_count = 0
    # generate missions
    missions = generate_mission_for_update_network_delay(position_data, topo, satellite_map_tmp)
    # generate submission list
    submission_list = generate_submission_list_for_update_network_delay(missions, submission_size)
    # submit
    while True:
        # store the start time
        start_time = time.time()
        if redis_conn.get('stop_process_state') == b'True':
            break
        # current count
        current_count = 0
        # generate pipe
        rcv_pipe, send_pipe = Pipe()
        for submission in submission_list:
            # process = Process(target=update_network_delay_with_single_process,
            #                   args=(submission, networks_tmp, send_pipe))
            # process.start()
            singleThread = Thread(target=update_network_delay_with_single_process,
                                  args=(submission, networks_tmp, send_pipe))
            singleThread.start()
        # receive the result
        while True:
            rcv_string = rcv_pipe.recv()
            if rcv_string == "finished":
                current_count += 1
                # traverse all the process and kill them
                if current_count == len(submission_list):
                    send_pipe.close()
                    rcv_pipe.close()
                    break
        end_time = time.time()
        logger.info(f"update satellite network delay in {end_time - start_time}s")
        update_count += 1
        if update_count == 1:
            break
        time.sleep(update_interval)
    logger.success("update satellite network delay process finished")

if __name__ == '__main__':
    print(generate_submission_list_for_network_object_creation([1, 2, 3, 4, 5], 1))
