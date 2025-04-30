#include <netlink/socket.h>
#include <netlink/netlink.h>
#include <netlink/msg.h>
#include <netlink/route/link.h>
#include <netlink/route/tc.h>
#include <netlink/route/qdisc.h>
#include <netlink/utils.h>
#include <netlink/cache.h>
#include <unistd.h>
#include <stdio.h>
#include <math.h>

#define NETLINK_RECV_PACKET	30
#define ARRAY_SIZE          4
#define MAX_COST            65535

const char interface_name[4][5] = {"eth1", "eth2", "eth3", "eth4"};
int transmission_cost[5] = {0};         // transmission_cost[0] is the init cost of eth1
int forwarding_queue_capacity = 0;      // unit: packet
int bandwidth = 0;                      // unit: bps
int packet_size = 0;                    // unit: bits
double delta;
char command[120];
u_int32_t qlen_amplitude_threshold;     // send delta * forwarding_queue_capacity (i.e., packet number thr) to kernel through netlink messages

/**
 * calculate queuing delay based on bandwidth, avg packet size and qlen
 * bandwidth: bps
 * packet_size: bits
 * return: caculated queuing delay, unit: ms
 */
double estimate_queuing_delay(int bandwidth, int packet_size, int qlen)
{
    return (double)packet_size * (double)qlen / (double)bandwidth * 1000.0;
}

/**
 * change the delay to ospf cost
 * delay: ms
 */
int delay_to_cost(double delay)
{
    return round(delay * 10.0);
}

static int nl_recv_message(struct nl_msg *msg, void *arg) {
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    int *array_data;
    int ret;

    if (nlh->nlmsg_len < NLMSG_HDRLEN + ARRAY_SIZE * sizeof(int)) {
        printf("Invalid message length\n");
        return -1;
    }

    array_data = (int *)NLMSG_DATA(nlh);

    // printf("Received an int array from netlink message:\n");
    for (int i = 0; i < ARRAY_SIZE; ++i) {
        // printf("cnt:%d Array[%d]: %d\n", recv_cnt, i, array_data[i]);
        // printf("last_time_qlen[%d]:%d  array_data[%d]:%d\n", i, last_time_qlen[i], i, array_data[i]);    

        if (array_data[i] != -1) {  // array_data == -1 means this interface is down
            // should change spf cost and flood
            double queuing_delay = estimate_queuing_delay(bandwidth, packet_size, array_data[i]);
            int new_cost = transmission_cost[i] + delay_to_cost(queuing_delay);
            if (new_cost > MAX_COST) {
                new_cost = MAX_COST;
            }
            if (new_cost <= 0) {
                new_cost = 150;
            }
            
            snprintf(command, sizeof(command), "/change_ospf_cost.sh %s %d\n", interface_name[i], new_cost);
            // printf(command);
            
            ret = system(command);
            if (ret != 0) {
                perror("command failed\n");
                return -1;
            }      
        }
    }

    return 0;
}

/**
 * argv[1]: double  parameter delta in LoFi
 * argv[2]: int     forwarding queue capacity in pkts
 * argv[3]: int     bandwidth in bps
 * argv[4]: int     packet size in bit
 * argv[5]: int     cost of transmission delay of eth1 (e.g., 134)
 * argv[6]: int     cost of transmission delay of eth2 (e.g., 134)
 * argv[7]: int     cost of transmission delay of eth3 (e.g., 134)
 * argv[8]: int     cost of transmission delay of eth4 (e.g., 134)
 */
int main(int argc, char const *argv[])
{
    struct nl_sock *sk;
    int ret, i;
    struct nl_msg *delta_msg = nlmsg_alloc();
    struct nlmsghdr *hdr;

    if (argc != 9) {
        perror("parameter invalid\n");
        return -1;
    }

    delta = atof(argv[1]);
    forwarding_queue_capacity = atoi(argv[2]);
    bandwidth = atoi(argv[3]);
    packet_size = atoi(argv[4]);

    for (i = 0; i < ARRAY_SIZE; ++i) {
        transmission_cost[i] = atoi(argv[i + 5]);
    }
    qlen_amplitude_threshold = (u_int32_t)round(delta * forwarding_queue_capacity);

    sk = nl_socket_alloc();

    nl_socket_disable_seq_check(sk);

    nl_socket_set_local_port(sk, 0);	// let kernel select pid automatically

    nl_connect(sk, NETLINK_RECV_PACKET);

   // set callback function for received netlink messages
    nl_socket_modify_cb(sk, NL_CB_MSG_IN, NL_CB_CUSTOM, nl_recv_message, NULL);

    // send qlen_amplitude_threshold to kernel
    hdr = nlmsg_put(delta_msg, 0, NL_AUTO_SEQ, NETLINK_RECV_PACKET, sizeof(qlen_amplitude_threshold), NLM_F_CREATE);
    if (hdr == NULL) {
        perror("nlmsg_put failed\n");
    }
    memcpy(nlmsg_data(hdr), &qlen_amplitude_threshold, sizeof(qlen_amplitude_threshold));
    ret = nl_send_auto(sk, delta_msg);
    if (ret < 0) {
        perror("nl_sned_auto failed\n");
    }
    // printf("netlink data len:%d\n", nlmsg_datalen(hdr));
    printf("sent qlen_amplitude_threshold:%u\n", qlen_amplitude_threshold);

    printf("Listening for netlink messages...\n");

    while (1)
    {
        nl_recvmsgs_default(sk);
    }

    return 0;
}
