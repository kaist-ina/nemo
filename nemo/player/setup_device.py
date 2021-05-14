import argparse
import sys

from nemo.tool.adb import *
#from nemo.tool.snpe import *
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
    parser.add_argument('--train_type', type=str, default='train_video')

    #anchor point selector
    parser.add_argument('--algorithm', type=str, required=True)

    #device
    parser.add_argument('--device_id', type=str, required=True)

    #codec
    parser.add_argument('--output_width', type=int, default=1920)
    parser.add_argument('--output_height', type=int, default=1080)

    args = parser.parse_args()

    #setup directory
    device_root_dir = os.path.join('/sdcard/NEMO', args.content)

    #setup videos
    device_video_dir = os.path.join(device_root_dir, 'video')
    adb_mkdir(device_video_dir, args.device_id)
    video_path = os.path.join(args.data_dir, args.content, 'video', args.video_name)
    #adb_push(device_video_dir, video_path, args.device_id)

    #convert a dnn
    video_profile = get_video_profile(video_path)
    input_shape = [1, video_profile['height'], video_profile['width'], 3]
    scale = args.output_height // video_profile['height']

    model = build_model(args.model_type, args.num_blocks, args.num_filters, scale, args.upsample_type, apply_clip=True)
    if args.train_type == 'train_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.video_name, model.name)
    elif args.train_type == 'finetune_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.video_name, '{}_finetune'.format(model.name))
    else:
        raise ValueError('Unsupported training types')
    #snpe_convert_model(model, input_shape, checkpoint_dir)

    #setup a dnn
    device_checkpoint_dir = os.path.join(device_root_dir, 'checkpoint', args.video_name)
    adb_mkdir(device_checkpoint_dir, args.device_id)
    dlc_path = os.path.join(checkpoint_dir, '{}.dlc'.format(model.name))
    adb_push(device_checkpoint_dir, dlc_path, args.device_id)

    #setup a cache profile
    device_cache_profile_dir = os.path.join(device_root_dir, 'profile', args.video_name, model.name)
    adb_mkdir(device_cache_profile_dir, args.device_id)
    cache_profile_path = os.path.join(args.data_dir, args.content, 'profile', args.video_name, model.name, '{}.profile'.format(args.algorithm))
    adb_push(device_cache_profile_dir, cache_profile_path, args.device_id)
