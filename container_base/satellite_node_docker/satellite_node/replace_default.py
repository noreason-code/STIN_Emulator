import os
import time
import re


def parse_route_table(route_table):
    routes = {}
    for line in route_table.splitlines():
        parts = line.strip().split()
        if len(parts) >= 5 and parts[1] == "via":
            destination = parts[0]
            gateway = parts[2]
            eth_name = parts[4]
            routes[destination] = [gateway, eth_name]
    return routes


def get_route_table():
    command = "ip route show"
    result = os.popen(command).read()
    return parse_route_table(result)


def ip2int(ip_str: str):
    part_list = ip_str.split('.')
    ip_int = (int(part_list[0]) << 24) + (int(part_list[1]) << 16) + (int(part_list[2]) << 8) + int(part_list[3].split('/')[0])
    return ip_int


if __name__ == '__main__':
    pattern = r'^173.'
    previous_route_table = get_route_table()
    latest_gsl_ip_int = 0

    while True:
        current_route_table = get_route_table()
        added_routes = {k: v for k, v in current_route_table.items() if k not in previous_route_table}
        if added_routes:
            for destination, gateway_and_eth in added_routes.items():
                if re.match(pattern, destination):
                    destination_int = ip2int(destination)   #只有在增加最新的gsl_ip时才更新默认路由
                    if destination_int >= latest_gsl_ip_int:
                        command_set_default = "ip route replace default via %s dev %s" % (gateway_and_eth[0], gateway_and_eth[1])
                        os.system(command_set_default)
                        command_ping = "ping -c 1 %s" % gateway_and_eth[0]  #通过ping来规避缺失ARP缓存丢包
                        os.system(command_ping)
                        latest_gsl_ip_int = destination_int
                        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        log_str = f"time:{t} | replaced default route: destination:{destination} via: {gateway_and_eth[0]} dev: {gateway_and_eth[1]}"
                        # print(f'time:{t} | replaced default route : destination {destination} via {gateway_and_eth[0]} dev {gateway_and_eth[1]}')
                        with open('./replace_default.log', 'a') as f:
                            f.write(log_str + '\n')
        previous_route_table = current_route_table
        time.sleep(0.1)

