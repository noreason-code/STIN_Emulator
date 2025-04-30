from flask import Flask, jsonify
from flask_cors import CORS
from global_var import reinit_global_var
import redis
import os.path
from satellite_config import Config
from data_updater import DataUpdater
from docker_client import DockerClient
from config_monitor import init_monitor, connect_monitor, set_monitor_app
from flask import request
from tle_generator import generate_tle
from constellation_creator import constellation_creator
from ground_station import create_station_from_json_app
from multiprocessing import Process
from const_var import *
from network_controller import update_network_delay_with_multi_process_app
from global_var import networks, connect_order_map, satellite_map, networks_ground
from position_broadcaster import position_broadcaster_app
from loguru import logger
import time
from draw_picture import draw
import numpy as np
import pickle
from user import create_user_node
from threading import Thread
from network_controller import get_network_key
import os


app = Flask(__name__)
#解决跨域
CORS(app,resources=r'/*')
#设置编码
app.config['JSON_AS_ASCII'] = False

# 用redis存储进程间共享数据
redis_conn = redis.Redis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD,db=REDIS_DB)

# read config.ini file
# ------------------------------------------------
file_path = os.path.abspath('.') + '/config.ini'
config = Config(file_path)
host_ip = config.DockerHostIP
image_name = config.DockerImageName
ground_image_name = config.GroundImageName
user_image_name = config.UserImageName
udp_port = config.UDPPort
monitor_image_name = config.MonitorImageName
# ------------------------------------------------

# create docker client
# ------------------------------------------------------------------
docker_client = DockerClient(image_name, host_ip, ground_image_name, user_image_name)
# ------------------------------------------------------------------


@app.post('/api/intial/constellation')
def create_constellation():
    redis_conn.set('stop_process_state', 'False')

    # 从请求中获取数据
    # --------------------------------------------------------------------------
    orbit_num = request.get_json()['orbit_num']
    sat_num_per_orbit = request.get_json()['sat_num_per_orbit']
    create_ground_list = request.get_json()['create_ground_list']
    delay_satellite = request.get_json()['delay_satellite']
    bandwidth_satellite = request.get_json()['bandwidth_satellite']
    loss_satellite = request.get_json()['loss_satellite']
    delay_ground = request.get_json()['delay_ground']
    bandwidth_ground = request.get_json()['bandwidth_ground']
    loss_ground = request.get_json()['loss_ground']
    link_failure_rate = request.get_json()['link_failure_rate']
    switch_cost = float(request.get_json()['switch_cost'] / 1000)
    user_list = request.get_json()['user_list']
    user_ground_connection = request.get_json()['user_ground_connection']
    # --------------------------------------------------------------------------

    # 将参数配置信息存进redis
    # --------------------------------------------------------------
    redis_conn.set('delay_satellite',delay_satellite)
    redis_conn.set('bandwidth_satellite',(bandwidth_satellite * 125))
    redis_conn.set('loss_satellite',loss_satellite)
    redis_conn.set('delay_ground',delay_ground)
    redis_conn.set('bandwidth_ground',(bandwidth_ground * 125))
    redis_conn.set('loss_ground',loss_ground)
    # --------------------------------------------------------------

    # 将链路故障率写入卫星容器挂载的文件
    # ---------------------------------------------------------------
    with open('./link/link_failure_rate.txt','w') as f:
        f.write(str(link_failure_rate))
    # ---------------------------------------------------------------

    redis_conn.set('app_flag','True')

    # 初始化全局变量
    # -------------------
    reinit_global_var()
    # -------------------

    # create position updater
    # ---------------------------------------------------------------
    updater = DataUpdater("<broadcast>", host_ip, int(udp_port))
    # ---------------------------------------------------------------

    # create monitor
    # -------------------------------------------------------------------------
    successful_init = init_monitor(monitor_image_name, docker_client, udp_port)
    # -------------------------------------------------------------------------

    # start send monitor data
    # -----------------
    connect_monitor()
    # -----------------

    # generate satellite infos
    # ----------------------------------------------------------------
    satellite_infos, connections = generate_tle(orbit_num, sat_num_per_orbit, 0, 0, 360 // sat_num_per_orbit // 2, 0.06965)
    satellite_num = len(satellite_infos)
    # ----------------------------------------------------------------

    # generate constellation
    # ----------------------------------------------------------------------------------------------------
    position_datas, monitor_payloads = constellation_creator(docker_client, satellite_infos, connections, host_ip,
                                                             udp_port, successful_init)
    ground_stations = create_station_from_json_app(docker_client, config.GroundConfigPath_APP,create_ground_list)
    # ----------------------------------------------------------------------------------------------------
    # generate user_node
    create_user_node(docker_client, user_list, user_ground_connection)

    # set monitor
    # ----------------------------------------------------------
    process = Process(target=set_monitor_app, args=(monitor_payloads, ground_stations, 20))
    process.start()
    # ----------------------------------------------------------
    # ----------------------------------------------------------
    # start position broadcaster
    # ----------------------------------------------------------
    update_position_process = Process(target=position_broadcaster_app, args=(satellite_num,
                                                                         position_datas,
                                                                         updater,
                                                                         BROADCAST_SEND_INTERVAL,
                                                                         connect_order_map,
                                                                             switch_cost,
                                                                             docker_client))
    update_position_process.start()
    # ----------------------------------------------------------

    return jsonify({
        'code': 200,
        'message': 'create constellation success!'
    })

@app.post('/api/stop_and_kill_constellation')
def stop_and_kill_constellation():
    redis_conn.set('stop_process_state','True')
    logger.warning("start to stop and kill the process!")
    # time.sleep(20)
    logger.warning("start to stop and kill the constellation!")
    start_time = time.time()
    os.system("bash stop_and_kill_constellation.sh")
    end_time = time.time()
    logger.info(f"constellation destroy time cost: {end_time - start_time} s")

    return jsonify({
        'code':200,
        'message': 'stop and kill success!'
    })

@app.post('/api/socket_stop')
def socket_stop():

    redis_conn.set('stop_trans_flag', 'True')

    return jsonify({
        'code': 200,
        'message': 'success!'
    })

@app.post('/api/socket_stop_sat')
def socket_stop_sat():

    redis_conn.set('stop_trans_flag_sat', 'True')

    return jsonify({
        'code': 200,
        'message': 'success!'
    })


@app.post('/api/set_link_down')
def set_link_down():
    container_name_1 = request.get_json()['first_node']
    container_name_2 = request.get_json()['second_node']
    # 获取容器id
    command_get_container_id_1 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_1
    command_get_container_id_2 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_2
    container_id_1 = os.popen(command_get_container_id_1).read().strip()
    container_id_2 = os.popen(command_get_container_id_2).read().strip()
    # 获取network_key
    network_key = get_network_key(container_id_1, container_id_2)
    # 获取网络对象并调用其断开接口的函数
    network_obj = networks[network_key]
    network_obj.set_link_down([container_id_1])
    # 记录接口down的时间
    down_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    down_time = time.time()
    redis_conn.set('down_time', down_time)

    return jsonify({
        'code': 200,
        'message': down_time_str
    })


@app.post('/api/set_link_up')
def set_link_up():
    container_name_1 = request.get_json()['first_node']
    container_name_2 = request.get_json()['second_node']
    # 获取容器id
    command_get_container_id_1 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_1
    command_get_container_id_2 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_2
    container_id_1 = os.popen(command_get_container_id_1).read().strip()
    container_id_2 = os.popen(command_get_container_id_2).read().strip()
    # 获取network_key
    network_key = get_network_key(container_id_1, container_id_2)
    # 获取网络对象并调用其断开接口的函数
    network_obj = networks[network_key]
    network_obj.set_link_up([container_id_1])
    # 记录接口up的时间
    up_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    up_time = time.time()
    redis_conn.set('up_time', up_time)

    return jsonify({
        'code': 200,
        'message': up_time_str
    })


@app.post('/api/add_arp')
def add_arp():
    node_id1 = "node_64"
    node_id2 = "node_63"
    node_id3 = "node_62"

    cmd_64_1 = "arp -s 172.18.3.193 02:42:ac:12:03:c1"
    cmd_63_1 = "arp -s 172.18.3.195 02:42:ac:12:03:c3"
    cmd_63_2 = "arp -s 172.18.3.185 02:42:ac:12:03:b9"
    cmd_62_1 = "arp -s 172.18.3.187 02:42:ac:12:03:bb"

    docker_client.client.containers.get(node_id1).exec_run(cmd_64_1)
    docker_client.client.containers.get(node_id2).exec_run(cmd_63_1)
    docker_client.client.containers.get(node_id2).exec_run(cmd_63_2)
    docker_client.client.containers.get(node_id3).exec_run(cmd_62_1)

    return jsonify({
        'code': 200,
        'message': 'success'
    })


@app.post('/api/add_arp')
def add_arp_2():
    node_id1 = "node_64"
    node_id2 = "node_63"
    node_id3 = "node_62"

    cmd_64_1 = "arp -s 172.18.3.193 02:42:ac:12:03:c1"
    cmd_63_1 = "arp -s 172.18.3.195 02:42:ac:12:03:c3"
    cmd_63_2 = "arp -s 172.18.3.185 02:42:ac:12:03:b9"
    cmd_62_1 = "arp -s 172.18.3.187 02:42:ac:12:03:bb"

    docker_client.client.containers.get(node_id1).exec_run(cmd_64_1)
    docker_client.client.containers.get(node_id2).exec_run(cmd_63_1)
    docker_client.client.containers.get(node_id2).exec_run(cmd_63_2)
    docker_client.client.containers.get(node_id3).exec_run(cmd_62_1)

    return jsonify({
        'code': 200,
        'message': 'success'
    })

@app.post('/api/down_and_up')
def down_and_up():
    container_name_1 = request.get_json()['first_node']
    container_name_2 = request.get_json()['second_node']
    # 获取容器id
    command_get_container_id_1 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_1
    command_get_container_id_2 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_2
    container_id_1 = os.popen(command_get_container_id_1).read().strip()
    container_id_2 = os.popen(command_get_container_id_2).read().strip()
    # 获取network_key
    network_key = get_network_key(container_id_1, container_id_2)
    # 获取网络对象并调用其断开接口的函数
    network_obj = networks[network_key]

    li_name = "ftime"

    while True:
        if redis_conn.get('stop_trans_flag') == b'True':
            break
        else:
            network_obj.set_link_down([container_id_1])
            time.sleep(10)
            network_obj.set_link_up([container_id_1])
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            redis_conn.rpush(li_name, time_str)
            time.sleep(20)

    return jsonify({
        'code': 200,
        'message': "success"
    })

@app.post('/api/down_and_up_2')
def down_and_up_2():
    # first_link: 64-53
    # second_link: 64-63
    container_name_1 = request.get_json()['first_link_node_1']
    container_name_2 = request.get_json()['first_link_node_2']
    container_name_3 = request.get_json()['second_link_node_1']
    container_name_4 = request.get_json()['second_link_node_2']
    # 获取容器id
    command_get_container_id_1 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_1
    command_get_container_id_2 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_2
    command_get_container_id_3 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_3
    command_get_container_id_4 = "docker inspect --format=\'{{.Id}}\' %s" % container_name_4
    container_id_1 = os.popen(command_get_container_id_1).read().strip()
    container_id_2 = os.popen(command_get_container_id_2).read().strip()
    container_id_3 = os.popen(command_get_container_id_3).read().strip()
    container_id_4 = os.popen(command_get_container_id_4).read().strip()
    # 获取network_key
    network_key_first_link = get_network_key(container_id_1, container_id_2)
    network_key_second_link = get_network_key(container_id_3, container_id_4)
    # 获取网络对象并调用其断开接口的函数
    network_obj_first_link = networks[network_key_first_link]
    network_obj_second_link = networks[network_key_second_link]
    # 关闭次优路由接口，实现故障两条链路
    network_obj_second_link.set_link_down([container_id_3])

    li_name = "ftime"

    while True:
        if redis_conn.get('stop_trans_flag') == b'True':
            break
        else:
            network_obj_first_link.set_link_down([container_id_1, container_id_2])
            time.sleep(10)
            network_obj_first_link.set_link_up([container_id_2, container_id_1])
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            redis_conn.rpush(li_name, time_str)
            time.sleep(20)

    return jsonify({
        'code': 200,
        'message': "success"
    })

@app.post('/api/set_interface_up')
def set_interface_up():
    container_name = "node_64"
    cmd_eth2 = "ifconfig eth2 up"
    cmd_eth3 = "ifconfig eth3 up"
    docker_client.client.containers.get(container_name).exec_run(cmd_eth2)
    docker_client.client.containers.get(container_name).exec_run(cmd_eth3)

    return jsonify({
        "code": 200,
        "message": "success"
    })

@app.post('/api/start_tcpdump')
def start_tcpdump():
    container_name = "user_0"
    cmd_start_tcpdump = "tcpdump -i any -w /tmp/tcpdump_ret.cap"
    docker_client.client.containers.get(container_name).exec_run(cmd_start_tcpdump)

    return jsonify({
        "code": 200,
        "message": "success"
    })

@app.post('/api/update_network_delay')
def update_network_delay():
    delay_li = [30, 75]
    # 300 -> 75
    delay_index = 0

    # 循环更新network delay
    while True:
        if redis_conn.get('stop_trans_flag') == b'True':
            break
        else:
            delay = delay_li[delay_index % 2]
            redis_conn.set('new_delay', delay)
            time.sleep(20)
            delay_index = delay_index + 1

    return jsonify({
        'code': 200,
        'message': "experiment finished"
    })

@app.post('/api/load_modules')
def load_modules():
    command_load_multipath_module = "insmod /home/huangshuo/Desktop/multipath_module/multipath_module.ko"
    os.system(command_load_multipath_module)

    return jsonify({
        'code': 200,
        'message': 'success'
    })

@app.post('/api/unload_modules')
def unload_modules():
    command_unload_multipath_module = "rmmod multipath_module"
    os.system(command_unload_multipath_module)

    return jsonify({
        'code': 200,
        'message': 'success'
    })

@app.post('/api/config_ospf')
def config_ospf():
    node_name = request.get_json()['node_name']
    eth_name = request.get_json()['eth_name']
    cost = 100

    command_config = ['vtysh', '-c', 'configure terminal', '-c', 'interface %s' % eth_name, '-c', 'ip ospf network point-to-point', '-c', 'ip ospf area 0.0.0.0', '-c', 'ip ospf hello-interval 1', '-c', 'ip ospf dead-interval 3', '-c', 'ip ospf cost %d' % cost]
    docker_client.client.containers.get(node_name).exec_run(command_config)

    return jsonify({
        'code': 200,
        'message': 'success'
    })
@app.post('/api/start_trans_sat')
def start_trans_sat():
    sender_idx = "node_53"
    receiver_idx = "node_52"
    # 获取receiver的IP地址
    networks_rcv = docker_client.client.containers.get(receiver_idx).attrs['NetworkSettings']['Networks']
    first_network_key = next(iter(networks_rcv))
    rcv_ip_addr = networks_rcv[first_network_key]["IPAddress"]
    # 启动传输对命令
    cmd_rcv = ["sh", "-c", "cd tmp && cd socket && nohup python probe_performance_receiver_sat.py %s %d &" % (rcv_ip_addr, 9995)]
    cmd_snd = ["sh", "-c",
               "cd tmp && cd socket && nohup python probe_performance_sender_sat.py %s %d &" % (rcv_ip_addr, 9995)]
    # 将传输对发送方使用的CC更换成BBR
    # docker_client.client.containers.get(sender_idx).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )
    # 启动传输对
    docker_client.client.containers.get(receiver_idx).exec_run(cmd_rcv)
    print('receiver create success.')
    docker_client.client.containers.get(sender_idx).exec_run(cmd_snd)
    print('sender create success.')

    return jsonify({
        "code": 200,
        "message": "success"
    })
@app.post('/api/start_multitrans')
def start_multitrans():
    sender_index_0 = 'user_0'
    # sender_index_1 = 'user_1'
    # sender_index_2 = 'user_2'
    # sender_index_3 = 'user_3'
    # sender_index_4 = 'user_4'
    receiver_index_0 = 'user_5'
    # receiver_index_1 = 'user_6'
    # receiver_index_2 = 'user_7'
    # receiver_index_3 = 'user_8'
    # receiver_index_4 = 'user_9'
    #获取各receiver的IP地址
    ip_addr_recv_0 = \
        docker_client.client.containers.get(receiver_index_0).attrs['NetworkSettings']['Networks'][receiver_index_0][
            'IPAddress']
    # ip_addr_recv_1 = \
    #     docker_client.client.containers.get(receiver_index_1).attrs['NetworkSettings']['Networks'][receiver_index_1][
    #         'IPAddress']
    # ip_addr_recv_2 = \
    #     docker_client.client.containers.get(receiver_index_2).attrs['NetworkSettings']['Networks'][receiver_index_2][
    #         'IPAddress']
    # ip_addr_recv_3 = \
    #     docker_client.client.containers.get(receiver_index_3).attrs['NetworkSettings']['Networks'][receiver_index_3][
    #         'IPAddress']
    # ip_addr_recv_4 = \
    #     docker_client.client.containers.get(receiver_index_4).attrs['NetworkSettings']['Networks'][receiver_index_4][
    #         'IPAddress']
    # 启动传输对
    command_recv_0 = ["sh", "-c", "cd tmp && bash start_trans_recv.sh %s %d %d" % (ip_addr_recv_0, 9990, 0)]
    # command_recv_1 = ["sh", "-c", "cd tmp && bash start_trans_recv.sh %s %d %d" % (ip_addr_recv_1, 9991, 1)]
    # command_recv_2 = ["sh", "-c", "cd tmp && bash start_trans_recv.sh %s %d %d" % (ip_addr_recv_2, 9992, 2)]
    # command_recv_3 = ["sh", "-c", "cd tmp && bash start_trans_recv.sh %s %d %d" % (ip_addr_recv_3, 9993, 3)]
    # command_recv_4 = ["sh", "-c", "cd tmp && bash start_trans_recv.sh %s %d %d" % (ip_addr_recv_4, 9994, 4)]

    command_send_0 = ["sh", "-c", "cd tmp && bash start_trans_send.sh %s %d %d" % (ip_addr_recv_0, 9990, 0)]
    # command_send_1 = ["sh", "-c", "cd tmp && bash start_trans_send.sh %s %d %d" % (ip_addr_recv_1, 9991, 1)]
    # command_send_2 = ["sh", "-c", "cd tmp && bash start_trans_send.sh %s %d %d" % (ip_addr_recv_2, 9992, 2)]
    # command_send_3 = ["sh", "-c", "cd tmp && bash start_trans_send.sh %s %d %d" % (ip_addr_recv_3, 9993, 3)]
    # command_send_4 = ["sh", "-c", "cd tmp && bash start_trans_send.sh %s %d %dt" % (ip_addr_recv_4, 9994, 4)]

    #将传输对发送方使用的CC更换成BBR
    docker_client.client.containers.get(sender_index_0).exec_run(
        'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    )
    # docker_client.client.containers.get(sender_index_1).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )
    # docker_client.client.containers.get(sender_index_2).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )
    # docker_client.client.containers.get(sender_index_3).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )
    # docker_client.client.containers.get(sender_index_4).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )

    docker_client.client.containers.get(receiver_index_0).exec_run(command_recv_0)
    print('receiver 0 create success.')
    docker_client.client.containers.get(sender_index_0).exec_run(command_send_0)
    print('sender 0 create success.')
    # time.sleep(5)
    # docker_client.client.containers.get(receiver_index_1).exec_run(command_recv_1)
    # print('receiver 1 create success.')
    # docker_client.client.containers.get(sender_index_1).exec_run(command_send_1)
    # print('sender 1 create success.')
    # time.sleep(10)
    # docker_client.client.containers.get(receiver_index_2).exec_run(command_recv_2)
    # print('receiver 2 create success.')
    # docker_client.client.containers.get(sender_index_2).exec_run(command_send_2)
    # print('sender 2 create success.')
    # time.sleep(10)
    # docker_client.client.containers.get(receiver_index_3).exec_run(command_recv_3)
    # print('receiver 3 create success.')
    # docker_client.client.containers.get(sender_index_3).exec_run(command_send_3)
    # print('sender 3 create success.')
    # time.sleep(10)
    # docker_client.client.containers.get(receiver_index_4).exec_run(command_recv_4)
    # print('receiver 4 create success.')
    # docker_client.client.containers.get(sender_index_4).exec_run(command_send_4)
    # print('sender 4 create success.')

    return jsonify({
        'code': 200,
        'message': 'success'
    })


@app.post('/api/start_one_way_latency')
def start_one_way_latency():
    sender_index_0 = 'user_0'
    receiver_index_0 = 'user_5'
    #获取receiver的IP地址
    ip_addr_recv_0 = \
        docker_client.client.containers.get(receiver_index_0).attrs['NetworkSettings']['Networks'][receiver_index_0][
            'IPAddress']

    command_recv_0 = ["sh", "-c", "cd tmp && bash start_OWL_receiver.sh %s %d" % (ip_addr_recv_0, 9990)]
    command_send_0 = ["sh", "-c", "cd tmp && bash start_OWL_sender.sh %s %d" % (ip_addr_recv_0, 9990)]

    docker_client.client.containers.get(receiver_index_0).exec_run(command_recv_0)
    print('receiver 0 create success.')
    docker_client.client.containers.get(sender_index_0).exec_run(command_send_0)
    print('sender 0 create success.')

    return jsonify({
        'code': 200,
        'message': 'success'
    })

@app.post('/api/strat_multifct')
def start_multifct():
    sender_index_0 = 'user_0'
    sender_index_1 = 'user_1'
    sender_index_2 = 'user_2'
    sender_index_3 = 'user_3'
    sender_index_4 = 'user_4'
    receiver_index_0 = 'user_5'
    receiver_index_1 = 'user_6'
    receiver_index_2 = 'user_7'
    receiver_index_3 = 'user_8'
    receiver_index_4 = 'user_9'
    # 获取各receiver的IP地址
    ip_addr_recv_0 = \
        docker_client.client.containers.get(receiver_index_0).attrs['NetworkSettings']['Networks'][receiver_index_0][
            'IPAddress']
    # ip_addr_recv_1 = \
    #     docker_client.client.containers.get(receiver_index_1).attrs['NetworkSettings']['Networks'][receiver_index_1][
    #         'IPAddress']
    # ip_addr_recv_2 = \
    #     docker_client.client.containers.get(receiver_index_2).attrs['NetworkSettings']['Networks'][receiver_index_2][
    #         'IPAddress']
    # ip_addr_recv_3 = \
    #     docker_client.client.containers.get(receiver_index_3).attrs['NetworkSettings']['Networks'][receiver_index_3][
    #         'IPAddress']
    # ip_addr_recv_4 = \
    #     docker_client.client.containers.get(receiver_index_4).attrs['NetworkSettings']['Networks'][receiver_index_4][
    #         'IPAddress']
    # 启动传输对
    flow_type = "campus"
    command_recv_0 = ["sh", "-c", "cd tmp && bash start_fct_recv.sh %s %d %d %s" % (ip_addr_recv_0, 9990, 0, flow_type)]
    # command_recv_1 = ["sh", "-c", "cd tmp && bash start_fct_recv.sh %s %d %d %s" % (ip_addr_recv_1, 9991, 1, flow_type)]
    # command_recv_2 = ["sh", "-c", "cd tmp && bash start_fct_recv.sh %s %d %d %s" % (ip_addr_recv_2, 9992, 2, flow_type)]
    # command_recv_3 = ["sh", "-c", "cd tmp && bash start_fct_recv.sh %s %d %d %s" % (ip_addr_recv_3, 9993, 3, flow_type)]
    # command_recv_4 = ["sh", "-c", "cd tmp && bash start_fct_recv.sh %s %d %d %s" % (ip_addr_recv_4, 9994, 4, flow_type)]

    command_send_0 = ["sh", "-c", "cd tmp && bash start_fct_send.sh %s %d %d %s" % (ip_addr_recv_0, 9990, 0, flow_type)]
    # command_send_1 = ["sh", "-c", "cd tmp && bash start_fct_send.sh %s %d %d %s" % (ip_addr_recv_1, 9991, 1, flow_type)]
    # command_send_2 = ["sh", "-c", "cd tmp && bash start_fct_send.sh %s %d %d %s" % (ip_addr_recv_2, 9992, 2, flow_type)]
    # command_send_3 = ["sh", "-c", "cd tmp && bash start_fct_send.sh %s %d %d %s" % (ip_addr_recv_3, 9993, 3, flow_type)]
    # command_send_4 = ["sh", "-c", "cd tmp && bash start_fct_send.sh %s %d %d %s" % (ip_addr_recv_4, 9994, 4, flow_type)]

    # docker_client.client.containers.get(sender_index_0).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )
    # docker_client.client.containers.get(sender_index_1).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )
    # docker_client.client.containers.get(sender_index_2).exec_run(
    #     'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
    # )

    docker_client.client.containers.get(receiver_index_0).exec_run(command_recv_0)
    print('receiver 0 create success.')
    docker_client.client.containers.get(sender_index_0).exec_run(command_send_0)
    print('sender 0 create success.')
    # time.sleep(5)
    # docker_client.client.containers.get(receiver_index_1).exec_run(command_recv_1)
    # print('receiver 1 create success.')
    # docker_client.client.containers.get(sender_index_1).exec_run(command_send_1)
    # print('sender 1 create success.')
    # time.sleep(5)
    # docker_client.client.containers.get(receiver_index_2).exec_run(command_recv_2)
    # print('receiver 2 create success.')
    # docker_client.client.containers.get(sender_index_2).exec_run(command_send_2)
    # print('sender 2 create success.')
    # time.sleep(10)
    # docker_client.client.containers.get(receiver_index_3).exec_run(command_recv_3)
    # print('receiver 3 create success.')
    # docker_client.client.containers.get(sender_index_3).exec_run(command_send_3)
    # print('sender 3 create success.')
    # time.sleep(10)
    # docker_client.client.containers.get(receiver_index_4).exec_run(command_recv_4)
    # print('receiver 4 create success.')
    # docker_client.client.containers.get(sender_index_4).exec_run(command_send_4)
    # print('sender 4 create success.')

    return jsonify({
        'code': 200,
        'message': 'success'
    })


@app.post('/api/strat_throughput_and_rtt')
def start_throughput_and_rtt():
    # 获取json参数
    # -------------------------------------------------------------------------
    # receiver_ground_index = int(request.get_json()['receiver_ground_index'])
    # receiver_index = 'ground_' + str(receiver_ground_index)
    # sender_ground_index = int(request.get_json()['sender_ground_index'])
    # sender_index = 'ground_' + str(sender_ground_index)
    cc = request.get_json()['cc']
    transport_pair = np.array(request.get_json()['transport_pair'])
    # -------------------------------------------------------------------------

    # 初始化redis内容并启动传输对
    # -----------------------------------------------------------
    redis_conn.set('stop_trans_flag', 'False')
    redis_conn.ltrim('handover_time', 1, 0)
    for i in range(len(transport_pair)):
        #初始化存储列表
        # --------------------------------------------------------------
        throughput_li_sender_name = 'throughput_li_sender_' + str(i)
        throughput_li_receiver_name = 'throughput_li_receiver_' + str(i)
        rtt_li_name = 'rtt_li_' + str(i)
        cwnd_li_name = 'cwnd_li_' + str(i)
        redis_conn.ltrim(throughput_li_sender_name, 1, 0)
        redis_conn.ltrim(throughput_li_receiver_name, 1, 0)
        redis_conn.ltrim(rtt_li_name, 1, 0)
        redis_conn.ltrim(cwnd_li_name, 1, 0)
        #---------------------------------------------------------------
        pair = transport_pair[i]
        sender_index = 'ground_' + str(pair[0])
        receiver_index = 'ground_' + str(pair[1])
        # 获取receiver的ip地址
        ip_addr_recv = \
        docker_client.client.containers.get(receiver_index).attrs['NetworkSettings']['Networks'][receiver_index][
            'IPAddress']
        #获取sender的ip地址
        ip_addr_sender = \
        docker_client.client.containers.get(sender_index).attrs['NetworkSettings']['Networks'][sender_index][
            'IPAddress']
        # 启动receiver
        # ---------------------------------------------
        # docker_client.client.containers.get(receiver_index).exec_run(
        #     'sh -c \"cd tmp && nohup python Throughput_receiver.py %s %d %d &\"' % (ip_addr_recv, 9999, i))
        # print('Throughput_receiver create success.')
        docker_client.client.containers.get(receiver_index).exec_run(
            'sh -c \"cd tmp && nohup python probe_performance_receiver.py %s %d %d &\"' % (ip_addr_recv, 9999, i))
        print('receiver create success.')
        # docker_client.client.containers.get(receiver_index).exec_run(
        #     'sh -c \"cd tmp && nohup python part_rtt_receiver.py %s %d %s %d &\"' % (ip_addr_recv, 9998, 'r', i))
        # print('part_rtt_receiver_r create success.')
        # docker_client.client.containers.get(sender_index).exec_run(
        #     'sh -c \"cd tmp && nohup python part_rtt_receiver.py %s %d %s %d &\"' % (ip_addr_sender, 9997, 's', i))
        # print('part_rtt_receiver_s create success.')
        # docker_client.client.containers.get(receiver_index).exec_run(
        #     'sh -c \"cd tmp && nohup python RTT_receiver.py %s %d &\"' % (ip_addr_recv, 9998))
        # print('RTT_receiver create success.')

        # ---------------------------------------------

        # 启动sender
        # --------------------------------------------
        if cc == 'Reno':
            docker_client.client.containers.get(sender_index).exec_run(
                'sh -c \"echo \"reno\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
            )
        elif cc == 'BBR':
            docker_client.client.containers.get(sender_index).exec_run(
                'sh -c \"echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
            )
        elif cc == 'CUBIC':
            docker_client.client.containers.get(sender_index).exec_run(
                'sh -c \"echo \"cubic\" > /proc/sys/net/ipv4/tcp_congestion_control\"'
            )

        docker_client.client.containers.get(sender_index).exec_run(
            'sh -c \"cd tmp && nohup python probe_performance_sender.py %s %d %d &\"' % (ip_addr_recv, 9999, i)
        )
        print('sender create success.')
        # docker_client.client.containers.get(sender_index).exec_run(
        #     'sh -c \"cd tmp && nohup python part_rtt_sender.py %s %d &\"' % (ip_addr_recv, 9998))
        # print('part_rtt_sender_r create success.')
        # docker_client.client.containers.get(receiver_index).exec_run(
        #     'sh -c \"cd tmp && nohup python part_rtt_sender.py %s %d &\"' % (ip_addr_sender, 9997))
        # print('part_rtt_sender_s create success.')
        # docker_client.client.containers.get(sender_index).exec_run(
        #     'sh -c \"cd tmp && nohup python RTT_sender.py %s %d %d &\"' % (ip_addr_recv, 9998, i)
        # )
        # print('RTT_sender create success.')
    # -----------------------------------------------------------
    #初始化记录GSL切换时间列表，并设置测试开始时间
    #-------------------------------------------------------
    redis_conn.ltrim('handover_time', 1, 0)
    redis_conn.set('begin_time', time.time())
    #-------------------------------------------------------
    return jsonify({
        'code': 200,
        'message': 'success'
    })

@app.post('/api/start_FCT')
def start_FCT():
    # 获取json测试参数
    # -------------------------------------------------------------------------
    #改
    transport_pair = np.array(request.get_json()['transport_pair'])
    pair = transport_pair[0]
    sender_index = 'ground_' + str(pair[0])
    receiver_index = 'ground_' + str(pair[1])
    # receiver_ground_index = int(request.get_json()['receiver_ground_index'])
    # receiver_index = 'ground_' + str(receiver_ground_index)
    # sender_ground_index = int(request.get_json()['sender_ground_index'])
    # sender_index = 'ground_' + str(sender_ground_index)
    test_time = request.get_json()['time']
    flow_type = request.get_json()['flow_type']
    cc = request.get_json()['cc']
    link_utilization = request.get_json()['link_utilization']
    # -------------------------------------------------------------------------
    # 初始化redis内容
    # -----------------------------------------------------------
    redis_conn.set('stop_trans_flag', 'False')
    redis_conn.ltrim('FCT_li', 1, 0)
    # redis_conn.ltrim('RTT_li', 1, 0)
    # -----------------------------------------------------------
    # 获取receiver ip地址
    ip_addr = docker_client.client.containers.get(receiver_index).attrs['NetworkSettings']['Networks'][receiver_index][
        'IPAddress']
    # 启动receiver
    # ---------------------------------------------
    docker_client.client.containers.get(receiver_index).exec_run(
        'sh -c \"cd tmp && nohup python FCT_receiver.py %s %d %d %s &\"' % (ip_addr, 9999, test_time, flow_type))
    print('FCT_receiver create success.')
    # docker_client.client.containers.get(receiver_index).exec_run(
    #     'sh -c \"cd tmp && nohup python RTT_receiver.py %s %d &\"' % (ip_addr, 9998))
    # print('RTT_receiver create success.')
    # ---------------------------------------------
    # 启动sender
    # --------------------------------------------
    if cc == 'Reno':
        command = 'echo \"reno\" > /proc/sys/net/ipv4/tcp_congestion_control'
        os.system(command)
    elif cc == 'BBR':
        command = 'echo \"bbr\" > /proc/sys/net/ipv4/tcp_congestion_control'
        os.system(command)
    elif cc == 'CUBIC':
        command = 'echo \"cubic\" > /proc/sys/net/ipv4/tcp_congestion_control'
        os.system(command)
    docker_client.client.containers.get(sender_index).exec_run(
        'sh -c \"cd tmp && nohup python FCT_sender.py %s %d %d %s %f &\"' % (ip_addr, 9999, test_time, flow_type, link_utilization)
    )
    print('FCT_sender create success.')
    # docker_client.client.containers.get(sender_index).exec_run(
    #     'sh -c \"cd tmp && nohup python RTT_sender.py %s %d &\"' % (ip_addr, 9998)
    # )
    # print('RTT_sender create success.')

    return jsonify({
        'code':200,
        'message':'success'
    })

@app.get('/api/get_throughput')
def get_throughput():
    #改
    real_time_throughput = redis_conn.lpop('throughput_li_sender_0', 1) #先默认一个传输对
    bandwidth_ground = int(redis_conn.get('bandwidth_ground'))
    if real_time_throughput:
        unpickled_data = pickle.loads(real_time_throughput[0])
        throughput = unpickled_data['TP']
        if throughput > bandwidth_ground:
            throughput = bandwidth_ground
        time_stamp = unpickled_data['time']
        return jsonify({
            'code': 200,
            'message': 'success',
            'real_time_throughput': throughput,
            'time_stamp': time_stamp
        })
    # if real_time_throughput:
    #     return jsonify({
    #         'code': 200,
    #         'message': 'success',
    #         'real_time_throughput': float(real_time_throughput[0]),
    #     })
    else:
        return jsonify({
            'code': 0,
            'message': 'error',
        })

@app.get('/api/get_rtt')
def get_rtt():
    #改
    real_time_rtt = redis_conn.lpop('rtt_li_0', 1)  #先默认一个传输对
    if real_time_rtt:
        unpickled_data = pickle.loads(real_time_rtt[0])
        rtt = unpickled_data['RTT']
        time_stamp = unpickled_data['time']
        return jsonify({
            'code': 200,
            'message': 'success',
            'real_time_rtt': rtt,
            'time_stamp': time_stamp
        })
    # if real_time_rtt:
    #     return jsonify({
    #         'code':200,
    #         'message':'success',
    #         'real_time_rtt':float(real_time_rtt[0])
    #     })
    else:
        return jsonify({
            'code': 0,
            'message': 'error'
        })

# 'FCT':float(fct[0])
@app.get('/api/get_FCT')
def get_FCT():
    #改
    fct = redis_conn.lpop('FCT_li',1)
    if fct:
        unpickled_data = pickle.loads(fct[0])
        FCT = unpickled_data['fct']
        time_stamp = unpickled_data['time_stamp']
        return jsonify({
            'code': 200,
            'message': 'success',
            'FCT': FCT,
            'time_stamp': time_stamp
        })
    else:
        return jsonify({
            'code': 0,
            'message': 'error'
        })


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
