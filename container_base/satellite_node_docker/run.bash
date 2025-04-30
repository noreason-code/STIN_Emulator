# cd /edit && nohup python3 start_compress.py > compress_log.log 2>&1 &
trap "exit 0" TERM
cd /satellite_node/ && nohup python event_generator.py 0.01 ${NODE_ID} false > event_generator.log &
#cd /satellite_node/ && nohup python default_improve.py > replace_default_route.log &
cd /satellite_node/ && ./bootstrap.sh

