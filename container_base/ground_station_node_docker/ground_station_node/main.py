import os

FRR_CONFIG_FILE_PATH = "/etc/frr/frr.conf"
FRR_SERVICE_START_CMD = "service frr start"

def write_into_frr(host_name:str):
    with open('./frr_config.config', 'w') as f:
        full_str = \
            f"""frr version 7.2.1 
frr defaults traditional
hostname {host_name}
log syslog informational
no ipv6 forwarding
service integrated-vtysh-config
!
interface eth1
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth2
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
interface eth3
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth4
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth5
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth6
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth7
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth8
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth9
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
interface eth10
    ip ospf network point-to-point
    ip ospf area 0.0.0.0
    ip ospf hello-interval 1
    ip ospf dead-interval 3
    ip ospf cost 600
router ospf
    redistribute connected
!
line vty
!
"""
        f.write(full_str)
    with open('./frr_config.config', 'r') as reader:
        content = reader.read()
        with open(FRR_CONFIG_FILE_PATH, 'w') as writer:
            writer.write(content)


if __name__ == '__main__':
    host_name = os.getenv('NODE_ID', None)
    write_into_frr(host_name)
    os.system(FRR_SERVICE_START_CMD)