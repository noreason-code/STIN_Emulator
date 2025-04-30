# BROADCAST PARAMETERS
import threading
import os

LATITUDE_KEY = 'lat'
LONGITUDE_KEY = 'lon'
# hs add
LATITUDE_KEY_APP = 'lat'
LONGITUDE_KEY_APP = 'long'
HEIGHT_KEY = 'hei'
R_EARTH = 6371000
HOST_PREFIX_LEN = 16

# BROAD_CAST_SEND_INTERVAL
BROADCAST_SEND_INTERVAL = 0.5
NETWORK_DELAY_UPDATE_INTERVAL = 30

# VOLUME1
base_dir = os.path.join(os.getcwd(),"../configuration")
VOLUME1 = "%s:/configuration" % base_dir
VOLUME2 = "/tmp/.X11-unix:/tmp/.X11-unix"
V_EDIT = "/home/satellite-2/Workspace/distributed_simulation/satellite-source-routing/satellite_node_docker/video_trans:/edit"

# hs add
VOLUME3 = '/home/huangshuo/Desktop/sat_net/distributed-emulator/node-manager/link:/tmp'
VOLUME_SK = '/home/huangshuo/Desktop/sat_net/distributed-emulator/node-manager/link/socket:/tmp/socket'

# hs add
VOLUME_IPERF = "/home/huangshuo/Desktop/sat_net/distributed-emulator/socket:/tmp"
        
# LIGHT_SPEED
LIGHT_SPEED = 300000

# DELAY BANDWIDTH LOSS
NETWORK_DELAY = 0 # unit ms, 150 means 150ms
NETWORK_BANDWIDTH = 1000 # unis kbytes/s must integer, 100 means 100kB/s
NETWORK_LOSS = 0 # percent 0 means 0%

# hs add
NETWORK_DELAY_GROUND = 100 # unit ms, 150 means 150ms
NETWORK_BANDWIDTH_GROUND = 10 # unis kbytes/s must integer, 100 means 100kB/s
NETWORK_LOSS_GROUND = 0 # percent 0 means 0%

# CONSTELLATION PARAMETERS
ORBIT_NUM = 6
SAT_PER_ORBIT = 11

# SUBMISSION SIZE
SUBMISSION_SIZE_FOR_NETWORK_OBJECT_CREATION = 1
SUBMISSION_SIZE_FOR_NETWORK_CREATION = 4
SUBMISSION_SIZE_FOR_CONTAINER_CREATION = 3
SUBMISSION_SIZE_FOR_DELETE_CONTAINER = 3
SUBMISSION_SIZE_FOR_DELETE_NETWORK = 4
SUBMISSION_SIZE_FOR_UPDATE_NETWORK_DELAY = 1

# hs add
REDIS_HOST = '10.134.180.138'
REDIS_PASSWORD = 'admin'
REDIS_PORT = 6379
REDIS_DB = 0
