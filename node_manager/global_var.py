# all satellites
import threading
from collections import OrderedDict


satellites = []
networks = {}
satellite_map = {}
connect_order_map = OrderedDict()
interface_map = {}
ground_stations = []
# hs add
networks_ground = {}
networks_user = {}
users = []
def reinit_global_var():
    global satellites, networks, satellite_map, connect_order_map, interface_map, ground_stations,networks_ground,networks_user,users
    satellites.clear()
    networks.clear()
    satellite_map.clear()
    connect_order_map.clear()
    interface_map.clear()
    ground_stations.clear()
    networks_ground.clear()
    networks_user.clear()
    users.clear()

# lock
interface_map_lock = threading.Lock()