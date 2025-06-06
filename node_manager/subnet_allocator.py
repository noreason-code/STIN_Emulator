import logging
import os
ip_range = [
    # [(10 << 24) + (0 << 16) + (0 << 8) + 0, (10 << 24) + (255 << 16) + (255 << 8) + 255],
    [(172 << 24) + (18 << 16) + (0 << 8) + 0, (172 << 24) + (31 << 16) + (255 << 8) + 255],
    [(192 << 24) + (168 << 16) + (0 << 8) + 0, (192 << 24) + (168 << 16) + (255 << 8) + 255],
    [(173 << 24) + (18 << 16) + (0 << 8) + 0, (173 << 24) + (31 << 16) + (255 << 8) + 255]
]

gsl_ip_range = [
    [(173 << 24) + (18 << 16) + (0 << 8) + 0, (173 << 24) + (18 << 16) + (0 << 8) + 255],
    [(173 << 24) + (18 << 16) + (1 << 8) + 0, (173 << 24) + (18 << 16) + (1 << 8) + 255],
    [(173 << 24) + (18 << 16) + (2 << 8) + 0, (173 << 24) + (18 << 16) + (2 << 8) + 255],
    [(173 << 24) + (18 << 16) + (3 << 8) + 0, (173 << 24) + (18 << 16) + (3 << 8) + 255],
    [(173 << 24) + (18 << 16) + (4 << 8) + 0, (173 << 24) + (18 << 16) + (4 << 8) + 255],
    [(173 << 24) + (18 << 16) + (5 << 8) + 0, (173 << 24) + (18 << 16) + (5 << 8) + 255],
    [(173 << 24) + (18 << 16) + (6 << 8) + 0, (173 << 24) + (18 << 16) + (6 << 8) + 255],
    [(173 << 24) + (18 << 16) + (7 << 8) + 0, (173 << 24) + (18 << 16) + (7 << 8) + 255],
    [(173 << 24) + (18 << 16) + (8 << 8) + 0, (173 << 24) + (18 << 16) + (8 << 8) + 255],
    [(173 << 24) + (18 << 16) + (9 << 8) + 0, (173 << 24) + (18 << 16) + (9 << 8) + 255]
]

user_ip_range = [
    [(173 << 24) + (18 << 16) + (10 << 8) + 0, (173 << 24) + (18 << 16) + (10 << 8) + 255],
    [(173 << 24) + (18 << 16) + (11 << 8) + 0, (173 << 24) + (18 << 16) + (11 << 8) + 255],
    [(173 << 24) + (18 << 16) + (12 << 8) + 0, (173 << 24) + (18 << 16) + (12 << 8) + 255],
    [(173 << 24) + (18 << 16) + (13 << 8) + 0, (173 << 24) + (18 << 16) + (13 << 8) + 255],
    [(173 << 24) + (18 << 16) + (14 << 8) + 0, (173 << 24) + (18 << 16) + (14 << 8) + 255],
    [(173 << 24) + (18 << 16) + (15 << 8) + 0, (173 << 24) + (18 << 16) + (15 << 8) + 255],
    [(173 << 24) + (18 << 16) + (16 << 8) + 0, (173 << 24) + (18 << 16) + (16 << 8) + 255],
    [(173 << 24) + (18 << 16) + (17 << 8) + 0, (173 << 24) + (18 << 16) + (17 << 8) + 255],
    [(173 << 24) + (18 << 16) + (18 << 8) + 0, (173 << 24) + (18 << 16) + (18 << 8) + 255],
    [(173 << 24) + (18 << 16) + (19 << 8) + 0, (173 << 24) + (18 << 16) + (19 << 8) + 255]
]


class SubnetAllocator:

    def __init__(self, prefix_len: int):
        self.range_index = 0
        self.subnet_ip = ip_range[0][0]
        self.prefix_len = prefix_len
        self.delta = 1 << (32 - prefix_len)
        self.conflict_ranges = []
        self.gene_conflict_range()
        self.conflict_ranges.sort()
        #hs add
        self.gsl_subnet_ip = gsl_ip_range
        self.user_subnet_ip = user_ip_range

    def gene_conflict_range(self):
        cmd = 'ifconfig -a | grep netmask'
        result = os.popen(cmd).read()[:-1]
        net_list = str(result).split('\n', -1)
        for net in net_list:
            item = net.split()
            netmask_str = item[3]
            ip_str = item[1]
            netmask_item = netmask_str.split('.', -1)
            ip_item = ip_str.split('.', -1)
            netmask = 0
            ip_addr = 0
            for p in range(4):
                netmask <<= 8
                netmask += int(netmask_item[p])
                ip_addr <<= 8
                ip_addr += int(ip_item[p])
            subnet_ip = ip_addr & netmask
            subnet_broad = ip_addr + ((~netmask) & 0xffffffff)
            self.conflict_ranges.append([subnet_ip, subnet_broad])

    # hs modified
    def alloc_local_subnet(self, is_gsl: bool, network_id: str) -> int:
        if is_gsl:
            ip_type = network_id.split('_')[0]
            ip_index = int(network_id.split('_')[1])
            # logging.info(network_id)
            print(ip_index)
            print(self.gsl_subnet_ip[ip_index])
            if ip_type == "user":
                init_ip = self.user_subnet_ip[ip_index][0]
            else:
                init_ip = self.gsl_subnet_ip[ip_index][0]
            print(init_ip)
            # hs add
            self.gene_conflict_range()
            self.conflict_ranges.sort()
            alloc_ip = self.check_conflict(init_ip)

            # self.gsl_subnet_ip = alloc_ip + (1 << (32 - self.prefix_len))
            # if self.gsl_subnet_ip > ip_range[self.range_index][1]:
            #     self.range_index += 1
            #     if self.range_index >= len(ip_range):
            #         raise "no more"
            #     self.subnet_ip = ip_range[self.range_index][0]
            return alloc_ip
        else:
            alloc_ip = self.check_conflict(self.subnet_ip)
            self.subnet_ip = alloc_ip + (1 << (32 - self.prefix_len))
            if self.subnet_ip > ip_range[self.range_index][1]:
                self.range_index += 1
                if self.range_index >= len(ip_range):
                    raise "no more"
                self.subnet_ip = ip_range[self.range_index][0]
            return alloc_ip

    def check_conflict(self, ip_addr) -> int:
        sub_net_end = ip_addr + (1 << (32 - self.prefix_len)) - 1
        for conflict_range in self.conflict_ranges:
            if conflict_range[0] <= ip_addr <= conflict_range[1]:
                ip_addr = conflict_range[1] + 1
                sub_net_end = ip_addr + (1 << (32 - self.prefix_len)) - 1
                continue
            if conflict_range[0] <= sub_net_end <= conflict_range[1]:
                ip_addr = conflict_range[1] + 1
                sub_net_end = ip_addr + (1 << (32 - self.prefix_len)) - 1
                continue

        return ip_addr


def ip2str(ip_addr: int) -> str:
    ip_0 = (ip_addr & 0xff000000) >> 24
    ip_1 = (ip_addr & 0x00ff0000) >> 16
    ip_2 = (ip_addr & 0x0000ff00) >> 8
    ip_3 = (ip_addr & 0x000000ff)
    return "%d.%d.%d.%d" % (ip_0, ip_1, ip_2, ip_3)


if __name__ == "__main__":
    allocator = SubnetAllocator(29)
    for i in range(10):
        ip = allocator.alloc_local_subnet()
        print(ip)
