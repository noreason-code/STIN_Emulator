import os
import re
import time


def ip2int(ip_str: str):
    part_list = ip_str.split('.')
    ip_int = (int(part_list[0]) << 24) + (int(part_list[1]) << 16) + (int(part_list[2]) << 8) + int(part_list[3].split('/')[0])
    return ip_int


def ip2binary_str(ip_str: str):
    ip_address = ip_str
    ip_parts = ip_address.split('.')
    binary_parts = [format(int(part), "08b") for part in ip_parts]
    ip_binary_str = "".join(binary_parts)
    return ip_binary_str


def check_interface():
    rtn_li = []
    pattern = r'^173.'

    command_get_eth_li = "ip l | grep \" eth\" | awk \'BEGIN{FS=\": \"}{print $2}\' | awk \'BEGIN{FS=\"@\"}{print $1}\' | sort"
    eth_li_tmp = os.popen(command_get_eth_li).read().split('\n')
    eth_li_tmp_new = eth_li_tmp[:len(eth_li_tmp)-1]
    print(eth_li_tmp_new)
    print(type(eth_li_tmp_new))

    # 当前卫星有与GSL连接的接口的条件：
    # 1、接口数>=5
    # 2、第5个接口的IP地址是GSL地址格式
    if len(eth_li_tmp_new) <= 4:
        print("No GSL interface")
    else:
        eth_li = eth_li_tmp_new[4:]
        for eth_name in eth_li:
            command_get_ip = "ip a | grep %s | awk \'BEGIN{FS=\"inet \"}{print $2}\' | awk \'BEGIN{FS=\"/29\"}{print $1}\'" % eth_name
            eth_ip_address = os.popen(command_get_ip).read().strip()
            if re.match(pattern, eth_ip_address):
                rtn_li.append(ip2binary_str(eth_ip_address)[:24])   # 只存储前缀，24位
        print(rtn_li)

    return rtn_li


def parse_route_table(route_table):
    routes = {}
    for line in route_table.splitlines():
        parts = line.strip().split()
        if len(parts) >= 5 and parts[1] == "via":
            destination = parts[0].split('/')[0]
            gateway = parts[2]
            eth_name = parts[4]
            routes[destination] = [gateway, eth_name]
    return routes


def get_route_table():
    command = "ip route show"
    result = os.popen(command).read()
    return parse_route_table(result)


def add_default_route(previous_route_table_tmp: dict, ip_li: list):
    pattern = r'^173.'
    # latest_gsl_ip_int = latest_gsl_ip
    previous_route_table = previous_route_table_tmp
    current_route_table = get_route_table()
    added_routes = {k: v for k, v in current_route_table.items() if k not in previous_route_table}
    if added_routes:
        print(added_routes)
        for destination, gateway_and_eth in added_routes.items():
            if re.match(pattern, destination):
                # 此处加判断
                print(destination)
                destination_binary_str = ip2binary_str(destination)
                for prefix in ip_li:
                    if re.match(prefix, destination_binary_str):
                        command_set_default = "ip route replace default via %s dev %s" % (
                        gateway_and_eth[0], gateway_and_eth[1])
                        os.system(command_set_default)
                        command_ping = "ping -c 1 %s" % gateway_and_eth[0]  # 通过ping来规避缺失ARP缓存丢包
                        os.system(command_ping)
                        # latest_gsl_ip_int = destination_int     # 返回
                        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        log_str = f"time:{t} | replaced default route: destination:{destination} via: {gateway_and_eth[0]} dev: {gateway_and_eth[1]}"
                        with open('./replace_default.log', 'a') as f:
                            f.write(log_str + '\n')
                        print(
                            f"time:{t} | replaced default route: destination:{destination} via: {gateway_and_eth[0]} dev: {gateway_and_eth[1]}")
                        break
                t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(
                    f"time:{t} | does not replaced default route: destination:{destination} via: {gateway_and_eth[0]} dev: {gateway_and_eth[1]}")


    previous_route_table = current_route_table      # 返回
    return previous_route_table



if __name__ == '__main__':
    previous_route_table_tmp = get_route_table()
    # latest_gsl_ip = 0
    while True:
        ip_li = check_interface()
        if len(ip_li) != 0:
            previous_route_table_rtn = add_default_route(previous_route_table_tmp, ip_li)
            previous_route_table_tmp = previous_route_table_rtn
        time.sleep(1)


