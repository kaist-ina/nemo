import argparse
import sys
import time

from nemo.tool.adb import *
from nemo.tool.snpe import *
from nemo.tool.video import get_video_profile
from nemo.dnn.utility import build_model
from nemo.tool.libvpx  import get_num_threads

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #path
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--video_name', type=str, required=True)

    #model
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int)
    parser.add_argument('--num_blocks', type=int)
    parser.add_argument('--upsample_type', type=str, default='deconv')

    #anchor point selector
    parser.add_argument('--algorithm_type', type=str, required=True)

    #device
    parser.add_argument('--device_id', type=str, required=True)

    #codec
    parser.add_argument('--output_width', type=int, default=1920)
    parser.add_argument('--output_height', type=int, default=1080)

    #experiment
    parser.add_argument('--sleep', type=float, default=10)

    args = parser.parse_args()

    #case 1: decode
    device_root_dir = os.path.join('/data/local/tmp', args.content)
    device_name = args.device_id
    device_script_path = os.path.join(device_root_dir, 'script', args.video_name, 'measure_decode_latency.sh')
    device_log_path = os.path.join(device_root_dir, 'log', args.video_name, 'latency.txt')
    host_log_dir = os.path.join(args.data_dir, args.content, 'log', args.video_name, device_name)
    host_log_path = os.path.join(host_log_dir, 'latency.txt')
    os.makedirs(host_log_dir, exist_ok=True)

    start_time = time.time()
    adb_shell(device_script_path, args.device_id)
    adb_pull(device_log_path, host_log_path, args.device_id)
    end_time = time.time()
    print("decode takes {}sec".format(end_time - start_time))

    time.sleep(args.sleep)
