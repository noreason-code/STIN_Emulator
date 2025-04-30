from docker_client import DockerClient
from satellite_node import SatelliteNode
from subnet_allocator import ip2str
from const_var import LATITUDE_KEY,LONGITUDE_KEY,HEIGHT_KEY,R_EARTH
import json
import math
import time
from loguru import logger
from global_var import ground_stations
# hs add
from network_controller import ground_network_object_creation,get_vethes_of_bridge,ground_network_object_creation_app
from const_var import *
from global_var import ground_stations, networks_ground, networks
import redis
import time
import threading
from network_controller import get_network_key

class GroundStation:
    DockerCli : DockerClient = None
    GroundStationCounter : int = 0
    def __init__(self,node_id: str, long: float,lat: float, cont_id: str, net_id: str) -> None:
        self.latitude = lat / 180 * math.pi
        self.longitude = long / 180 * math.pi
        self.node_id = node_id
        self.container_id = cont_id
        self.network_id = net_id
        self.connected_satellite_id = None
        self.connected_node_id = None
        self.handover_times = 0
        self.network_id_next = None
        self.gateway = None

    
    def disconnect_satellite(self, sat_cont_id: str):
        if sat_cont_id is None or GroundStation.DockerCli is None :
            return
        GroundStation.DockerCli.disconnect_node(sat_cont_id, self.network_id)
        #hs add
        GroundStation.DockerCli.disconnect_node(self.container_id, self.network_id)
        #用新的network_id替换旧的network_id供下一次disconnect使用
        self.network_id = self.network_id_next
        #hs modify
        # self.connected_satellite_id = None

    def connect_satellite(self, sat_node_id:str, sat_cont_id: str):
        if GroundStation.DockerCli is None:
            return
        GroundStation.DockerCli.connect_node(sat_cont_id, self.network_id, "sat")
        #更新地面站连接的卫星容器id和卫星节点id
        self.connected_satellite_id = sat_cont_id
        self.connected_node_id = sat_node_id

    #hs add
    def add_default_route_to_old_sat(self, container_id_new: str, container_id_old: str):
        network_key = get_network_key(container_id_new, container_id_old)
        try:
            network_obj = networks[network_key]
        except KeyError:
            return
        eth_list = network_obj.eth_interface_list
        new_eth = ""
        old_eth = ""
        if container_id_new < container_id_old:
            new_eth = eth_list[0]
            old_eth = eth_list[1]
        elif container_id_new > container_id_old:
            new_eth = eth_list[1]
            old_eth = eth_list[0]
        # command_get_gateway = ["sh", "-c",
        #                     "ip a | grep %s | awk \'BEGIN{FS=\"inet \"}{print $2}\' | awk \'BEGIN{FS=\"/29\"}{print $1}\'" % new_eth]
        command_get_gateway = ["sh", "-c",
                               "ip a | grep %s | awk \'BEGIN{FS=\"inet \"}{print $2}\' | awk \'BEGIN{FS=\"/29\"}{print $1}\'" % new_eth]
        response_gateway = GroundStation.DockerCli.client.containers.get(container_id_new).exec_run(command_get_gateway)
        # response_new_eth_ip_address = GroundStation.DockerCli.client.containers.get(container_id_new).exec_run(
        #     command_get_gateway)
        new_eth_ip_address = response_gateway.output.decode('utf-8').split('\n')[-2]
        print(f'old_eth: {old_eth}')
        print(f'new_eth: {new_eth}')
        print(f'new_eth_ip_address: {new_eth_ip_address}')
        command_gateway = ["ip", "route", "replace", "default", "via", new_eth_ip_address, "dev", old_eth]
        response_gateway = GroundStation.DockerCli.exec_cmd(container_id=container_id_old, cmd=command_gateway)

    def connect_satellite_for_switch(self, sat_node_id: str, sat_cont_id: str) -> str:
        if GroundStation.DockerCli is None:
            return
        #新建网络
        net_id, net_ip = GroundStation.DockerCli.create_network(self.node_id+"_"+str(self.handover_times))
        self.network_id_next = net_id
        ans_1 = ip2str(net_ip)
        print(f'new_net_ip: {ans_1}')
        #把地面站和新卫星加入到新建网络
        # ------------------------------------------------------------------------
        GroundStation.DockerCli.connect_node(self.container_id, self.network_id_next, "conn")
        command_eth = ["sh", "-c",
                       "ip l | grep \" eth\" | awk \'BEGIN{FS=\": \"}{print $2}\' | awk \'BEGIN{FS=\"@\"}{print $1}\' | sort"]
        # 获取地面站新接口
        response_ground = GroundStation.DockerCli.client.containers.get(self.container_id).exec_run(command_eth)
        eth_ground = response_ground.output.decode('utf-8').split('\n')[-2]  # 因为获取到的列表中最后一个元素是" "，所以获取倒数第二个，下同
        time.sleep(1)
        eth_down_command = ["ifconfig", "%s" % eth_ground, "down"]
        GroundStation.DockerCli.exec_cmd(self.container_id, eth_down_command)
        time.sleep(1)
        GroundStation.DockerCli.connect_node(sat_cont_id, self.network_id_next, "sat")
        # time.sleep(0.8)

        #在旧卫星中加入默认路由，下一跳是路由到新卫星的下一跳
        # net_addr = ip2str(net_ip - 1)
        # print(f'net_addr: {net_addr}')
        # command_get_route = ["sh", "-c", "ip r | grep %s | awk \'BEGIN{FS=\"/29 \"}{print $2}\' | awk \'BEGIN{FS=\" proto\"}{print $1}\'" % net_addr]
        # response_part_route = GroundStation.DockerCli.client.containers.get(self.connected_satellite_id).exec_run(command_get_route)
        # part_route_li = response_part_route.output.decode('utf-8').split('\n')[0]
        # part_route = part_route_li.split(' ')
        # eth_ip = part_route[1]  #对端ethIP地址
        # eth_name = part_route[3]    #本端eth名字
        # print(f'part_route: {part_route}')
        # command_replace_default = ["ip", "route", "replace", "default", "via", eth_ip, "dev", eth_name]
        # response_default = GroundStation.DockerCli.client.containers.get(self.connected_satellite_id).exec_run(command_replace_default)
        #判断新旧卫星之间是否存在链路，如果存在链路则添加相应的ARP条目
        # flag = True
        # network_key = get_network_key(sat_cont_id, self.connected_satellite_id)
        # try:
        #     network_obj = networks[network_key]
        # except KeyError:
        #     flag = False
        # if flag:
        #     command_get_mac = ["sh", "-c", "ip a | grep -B 1 %s | grep link | awk \'BEGIN{FS=\"ether \"}{print $2}\' | awk \'BEGIN{FS=\" brd\"}{print $1}\'" % eth_ip]
        #     response_mac = GroundStation.DockerCli.client.containers.get(sat_cont_id).exec_run(command_get_mac)
        #     eth_mac = response_mac.output.decode('utf-8').split('\n')[0]
        #     print(f'eth_mac: {eth_mac}')
        #     command_add_arp = ["arp", "-s", eth_ip, eth_mac]
        #     response_add_arp = GroundStation.DockerCli.client.containers.get(self.connected_satellite_id).exec_run(command_add_arp)

        # time.sleep(0.2)
        eth_up_command = ["ifconfig", "%s" % eth_ground, "up"]
        GroundStation.DockerCli.exec_cmd(self.container_id, eth_up_command)
        # -------------------------------------------------------------------------
        #获取新卫星eth
        response_sat = GroundStation.DockerCli.client.containers.get(sat_cont_id).exec_run(command_eth)
        eth_sat = response_sat.output.decode('utf-8').split('\n')[-2]
        #获取地面站网关
        command_get_gateway = ["sh", "-c",
                       "ip a | grep %s | awk \'BEGIN{FS=\"inet \"}{print $2}\' | awk \'BEGIN{FS=\"/29\"}{print $1}\'" % eth_sat]
        response_gateway = GroundStation.DockerCli.client.containers.get(sat_cont_id).exec_run(command_get_gateway)
        new_gateway = response_gateway.output.decode('utf-8').split('\n')[-2]
        print(f'new_gateway:{new_gateway}')
        self.gateway = new_gateway
        #---------------------------------------------------
        #创建网络对象
        #---------------------------------------------------
        network_obj_mission = []
        network_obj_mission.append((net_id, self.container_id, sat_cont_id, self.node_id))
        ground_network_object_creation_app(network_obj_mission, GroundStation.DockerCli)
        #---------------------------------------------------
        self.connected_satellite_id = sat_cont_id
        self.connected_node_id = sat_node_id
        time.sleep(8)
        return eth_ground

    def switch_satellite(self, sat_node_id: str, sat_cont_id: str, distance: float, switch_cost: float):
        logger.info("%s switch from %s to %s"%(self.node_id,self.connected_node_id,sat_node_id))
        # hs add
        # ----------------------------------------------
        # redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
        new_delay = int(distance / LIGHT_SPEED)
        # new_delay = 43

        # hs add
        # new_delay = int(redis_conn.get('new_delay'))
        print('星地间距离：%f m' % distance)
        print('星地间延迟：%d ms' % new_delay)
        # print(f'node_id: {self.node_id}')
        network_obj = networks_ground[self.node_id]
        network_obj.update_delay_param(new_delay)
        # print(f'network_obj_veth_li:{network_obj.veth_interface_list}')
        # -----------------------------------------------
        if sat_cont_id == self.connected_satellite_id:
            # hs add
            network_obj.update_info()
            return
        old_sat_cont_id = self.connected_satellite_id
        #hs add
        ground_eth = "eth1"
        if self.connected_satellite_id is None:
            self.connect_satellite(sat_node_id, sat_cont_id)
            network_obj.veth_interface_list = get_vethes_of_bridge(network_obj.br_interface_name, GroundStation.DockerCli,{}, self.container_id, sat_cont_id, 0)[0]
            network_obj.update_info()
        else:
            ground_eth = self.connect_satellite_for_switch(sat_node_id, sat_cont_id)
        logger.info("connect success")
        # time.sleep(2)
        #切换网关
        new_gateway = self.gateway
        command_gateway = ["ip", "route", "replace", "default", "via", new_gateway, "dev", ground_eth]
        response_gateway = self.DockerCli.exec_cmd(container_id=self.container_id, cmd=command_gateway)
        logger.info("switch gateway success")
        time.sleep(2)
        self.disconnect_satellite(old_sat_cont_id)
        logger.info("disconnect success")
        self.handover_times += 1
        # hs add
        redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
        handover_time = time.time()
        redis_conn.rpush('handover_time',handover_time)

def distance(position_data: dict, ground: GroundStation) -> float:
    z1 = (position_data[HEIGHT_KEY]+R_EARTH) * math.sin(position_data[LATITUDE_KEY])
    base1 = (position_data[HEIGHT_KEY]+R_EARTH) * math.cos(position_data[LATITUDE_KEY])
    x1 = base1 * math.cos(position_data[LONGITUDE_KEY])
    y1 = base1 * math.sin(position_data[LONGITUDE_KEY])
    z2 = R_EARTH * math.sin(ground.latitude)
    base2 = R_EARTH * math.cos(ground.latitude)
    x2 = base2 * math.cos(ground.longitude)
    y2 = base2 * math.sin(ground.longitude)
    # hs add
    # ------------------
    # print('卫星高度：%f' % position_data[HEIGHT_KEY])
    # --------------------
    return math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)




def ground_select(satellites: list,position_data: dict,grounds: list,switch_cost: float):
    # logger.info("Enter ground daemon.")
    connections = {}
    for ground in grounds:
        if ground.connected_satellite_id is None:
            shortest_id = None
            shortest_dis = math.inf
            shortest_cont = None
        else:
            shortest_id = ground.connected_node_id
            shortest_cont = ground.connected_satellite_id
            shortest_dis = distance(position_data[shortest_id],ground)
        for sat in satellites:
            new_distance = distance(position_data[sat.node_id],ground)
            # loggedr.info("%s new %f old: %f"%(sat.node_id,new_distance,shortest_dis))
            if new_distance < shortest_dis:
                shortest_id = sat.node_id
                shortest_cont = sat.container_id
                shortest_dis = new_distance
        ground.switch_satellite(shortest_id,shortest_cont,shortest_dis,switch_cost)
        connections[ground.node_id] = shortest_id
    return connections

def create_station_from_json(docker_client : DockerClient, path: str):
    grounds = {}
    # hs add
    # -------------------------
    network_object_mission = []
    # -------------------------
    json_config = open(path,"r")
    config_bytes = json_config.read()
    ground_list = json.loads(config_bytes)
    for ground in ground_list:
        # hs modify
        new_ground,network_obj_mission = create_ground_station(docker_client,ground[LONGITUDE_KEY],ground[LATITUDE_KEY])
        network_object_mission.append((network_obj_mission[0],network_obj_mission[1],"1"))
        grounds[new_ground.node_id] = {
            "lat": new_ground.latitude,
            "long": new_ground.longitude
        }
    # print(network_object_mission)
    ground_network_object_creation(network_object_mission)
    return grounds

def create_ground_station(docker_client : DockerClient, long: float, lat: float):
    if GroundStation.DockerCli is None :
        GroundStation.DockerCli = docker_client
    # hs add
    if len(ground_stations) == 0:
        GroundStation.GroundStationCounter = 0

    ground_id = "ground_" + str(GroundStation.GroundStationCounter)
    GroundStation.GroundStationCounter += 1
    container_id = docker_client.create_ground_container(ground_id)
    net_id, net_ip = docker_client.create_network(ground_id)
    # hs add
    # --------------------------------------
    network_obj_mission=[]
    network_obj_mission.append(net_id)
    network_obj_mission.append(container_id)
    # --------------------------------------
    docker_client.connect_node(container_id,net_id,"conn")
    new_station = GroundStation(ground_id, long, lat, container_id, net_id)
    ground_stations.append(new_station)
    # docker_client.exec_cmd(container_id=container_id, cmd=[
    #     "ip" "route" "del" "default" "via" "172.17.0.1" "dev" "eth0 && ip route add default via 172.17.0.1 dev eth0 metric 500"])
    command_set_default = ["ip", "route", "replace", "default", "via", ip2str(net_ip+3), "dev", "eth1"]
    # docker_client.exec_cmd(container_id=container_id,cmd=["ip","route","add","default","via",ip2str(net_ip+3)])
    docker_client.client.containers.get(container_id).exec_run(command_set_default)
    # hs modify
    return new_station,network_obj_mission


# hs add
def create_ground_station_app(docker_client : DockerClient, long: float, lat: float , index: int):
    if GroundStation.DockerCli is None :
        GroundStation.DockerCli = docker_client
    # hs add
    # if len(ground_stations) == 0:
    #     GroundStation.GroundStationCounter = 0

    ground_id = "ground_" + str(index)
    # GroundStation.GroundStationCounter += 1
    container_id = docker_client.create_ground_container(ground_id)
    net_id, net_ip = docker_client.create_network(ground_id)
    # hs add
    # --------------------------------------
    network_obj_mission=[]
    network_obj_mission.append(net_id)
    network_obj_mission.append(container_id)
    network_obj_mission.append(ground_id)
    # --------------------------------------
    docker_client.connect_node(container_id,net_id,"conn")
    print(lat)
    print(long)
    new_station = GroundStation(ground_id, long, lat, container_id, net_id)
    ground_stations.append(new_station)
    # docker_client.exec_cmd(container_id=container_id, cmd=["ip","route","del","default","via","172.17.0.1","dev","eth0"])
    # docker_client.exec_cmd(container_id=container_id,cmd=["ip","route","replace","default","gw",ip2str(net_ip+2)])
    docker_client.exec_cmd(container_id=container_id, cmd=["ip", "route", "del", "default", "via", "172.17.0.1", "dev", "eth0"])
    docker_client.exec_cmd(container_id=container_id, cmd=["route", "add", "default", "gw", ip2str(net_ip + 2)])
    # hs modify
    return new_station,network_obj_mission

# hs add
def create_station_from_json_app(docker_client : DockerClient, path: str,create_list:list):
    grounds = {}
    # hs add
    # -------------------------
    network_object_mission = []
    # -------------------------
    json_config = open(path, "r")
    config_bytes = json_config.read()
    ground_list = json.loads(config_bytes)
    # print(ground_list)
    create_ground_station_list = []

    for index in create_list:
        ground_obj = {
            "index":index,
            "obj":ground_list[index]
        }
        create_ground_station_list.append(ground_obj)

    for ground in create_ground_station_list:
        index = ground['index']
        obj = ground['obj']
        # hs modify
        new_ground, network_obj_mission = create_ground_station_app(docker_client, obj[LONGITUDE_KEY_APP],
                                                                obj[LATITUDE_KEY_APP], index)
        network_object_mission.append((network_obj_mission[0], network_obj_mission[1], "1",network_obj_mission[2]))
        grounds[new_ground.node_id] = {
            "lat": new_ground.latitude,
            "long": new_ground.longitude
        }
    # print(network_object_mission)
    ground_network_object_creation_app(network_object_mission, docker_client)

    return grounds