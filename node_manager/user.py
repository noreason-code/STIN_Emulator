from docker_client import DockerClient
from global_var import ground_stations, users
from subnet_allocator import ip2str
from network_controller import user_network_object_creation


class User:
    def __init__(self, node_id: str, container_id: str, net_id: str, net_ip: str):
        self.node_id = node_id
        self.container_id = container_id
        self.net_id = net_id
        self.net_ip = net_ip


def create_user_node(docker_client: DockerClient, user_list: list, user_ground_connection: list):
    for i in range(len(user_list)):
        user_index = user_list[i]
        user_id = "user_" + str(user_index)
        # 创建用户容器
        container_id = docker_client.create_user_container(user_id)
        # 创建网络
        net_id, net_ip = docker_client.create_network(user_id)
        print(f'user net ip:{ip2str(net_ip)}')
        # 将当前用户容器加入网络
        docker_client.connect_node(container_id, net_id, "user_conn")
        # 获取与当前用户容器连接的地面站id并与地面站建立连接
        ground_index = "ground_" + str(user_ground_connection[i][1])
        ground_container_id = ""
        for item in ground_stations:
            if item.node_id == ground_index:
                ground_container_id = item.container_id
                break
        docker_client.connect_node(ground_container_id, net_id, "ground_conn")
        # 切换网关
        command_set_default = ["ip", "route", "replace", "default", "via", ip2str(net_ip + 3), "dev", "eth1"]
        # docker_client.exec_cmd(container_id=container_id,
        #                        cmd=["ip", "route", "replace", "default", "via", ip2str(net_ip + 2), "dev", "eth1"])
        docker_client.client.containers.get(container_id).exec_run(command_set_default)
        new_user = User(user_id, container_id, net_id, net_ip)
        users.append(new_user)
        # 创建网络对象
        network_obj_mission = []
        network_obj_mission.append((net_id, container_id, ground_container_id, user_id))
        user_network_object_creation(network_obj_mission, docker_client)



