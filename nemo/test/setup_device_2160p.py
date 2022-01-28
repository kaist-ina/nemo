import argparse
import sys

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
    parser.add_argument('--lib_dir', type=str, required=True)

    #model
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int)
    parser.add_argument('--num_blocks', type=int)
    parser.add_argument('--upsample_type', type=str, default='deconv')
    parser.add_argument('--train_type', type=str, default='train_video')

    #anchor point selector
    parser.add_argument('--algorithm', type=str, required=True)

    #device
    parser.add_argument('--device_id', type=str, required=True)

    #codec
    parser.add_argument('--output_width', type=int, default=1920)
    parser.add_argument('--output_height', type=int, default=1080)
    parser.add_argument('--limit', type=int, default=1200)

    args = parser.parse_args()

    #setup directory
    device_root_dir = os.path.join('/data/local/tmp', args.content)
    device_video_dir = os.path.join(device_root_dir, 'video')
    device_lib_dir = os.path.join('/data/local/tmp', 'libs')
    device_bin_dir = os.path.join('/data/local/tmp', 'bin')
    adb_mkdir(device_video_dir, args.device_id)
    adb_mkdir(device_bin_dir, args.device_id)
    adb_mkdir(device_lib_dir, args.device_id)

    #setup vpxdec
    vpxdec_path = os.path.join(args.lib_dir, 'vpxdec_nemo_ver2')
    adb_push(device_bin_dir, vpxdec_path, args.device_id)

    #setup library
    c_path = os.path.join(args.lib_dir, 'libc++_shared.so')
    snpe_path = os.path.join(args.lib_dir, 'libSNPE.so')
    libvpx_path = os.path.join(args.lib_dir, 'libvpx.so')
    adb_push(device_lib_dir, c_path, args.device_id)
    adb_push(device_lib_dir, snpe_path, args.device_id)
    adb_push(device_lib_dir, libvpx_path, args.device_id)

    #setup videos
    video_path = os.path.join(args.data_dir, args.content, 'video', args.video_name)
    adb_push(device_video_dir, video_path, args.device_id) #TODO: remove this
    video_profile = get_video_profile(video_path)
    input_height = video_profile['height']

    #setup scripts (setup.sh, offline_dnn.sh, online_dnn.sh)
    script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.script')
    os.makedirs(script_dir, exist_ok=True)

    args.limit = 1200
    #case 1: No SR
    limit = '--limit={}'.format(args.limit) if args.limit is not None else ''
    device_script_dir = os.path.join(device_root_dir, 'script', args.video_name)
    adb_mkdir(device_script_dir, args.device_id)
    cmds = ['#!/system/bin/sh',
            'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{}'.format(device_lib_dir),
            'cd {}'.format(device_root_dir),
            '{} --codec=vp9  --noblit --threads={} --frame-buffers=50 {} --dataset-dir={} --input-video-name={} --save-latency --save-metadata'.format(os.path.join(device_bin_dir, 'vpxdec_nemo_ver2'), get_num_threads(input_height), limit, device_root_dir, args.video_name),
            'exit']
    # cmds = ['#!/system/bin/sh',
    #         'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{}'.format(device_lib_dir),
    #         'cd {}'.format(device_root_dir),
    #         '{} --codec=vp9  --noblit --threads={} --frame-buffers=50 {} --dataset-dir={} --input-video-name={} --save-latency --save-metadata'.format(os.path.join(device_bin_dir, 'vpxdec_nemo_ver2'), 4, limit, device_root_dir, args.video_name),
    #         'exit']
    cmd_script_path = os.path.join(script_dir, 'measure_decode_latency.sh')
    with open(cmd_script_path, 'w') as cmd_script:
        for ln in cmds:
            cmd_script.write(ln + '\n')
    adb_push(device_script_dir, cmd_script_path, args.device_id)
    os.system('adb -s {} shell "chmod +x {}"'.format(args.device_id, os.path.join(device_script_dir, '*.sh')))

