trap "exit 0" TERM
cd /ground_station_node/ && ./bootstrap.sh
tail -f /dev/null