import argparse
import os
import math
import glob
import sys
import time
import tensorflow as tf
tf.enable_eager_execution()
from nemo.tool.video import get_video_profile
import nemo.tool.libvpx as libvpx
from nemo.dnn.utility import build_model

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #directory, path
    parser.add_argument('--vpxdec_file', type=str, default=None)
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--lr_video_name', type=str, required=True)
    parser.add_argument('--hr_video_name', type=str, required=True)

    #codec
    parser.add_argument('--output_width', type=int, default=1920)
    parser.add_argument('--output_height', type=int, default=1080)
    parser.add_argument('--limit', type=int, default=None)

    #dnn
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int, required=True)
    parser.add_argument('--num_blocks', type=int, required=True)
    parser.add_argument('--upsample_type', type=str, default='deconv')

    #anchor point selector
    parser.add_argument('--algorithm', type=str, required=True)

    args = parser.parse_args()

    if args.vpxdec_file is None:
        args.vpxdec_file = os.path.join(os.environ['NEMO_CODE_ROOT'], 'third_party', 'libvpx', 'bin', 'vpxdec_nemo_ver2_x86')
        assert(os.path.exists(args.vpxdec_file))
    dataset_dir = os.path.join(args.data_dir, args.content)

    #profile videos
    dataset_dir = os.path.join(args.data_dir, args.content)
    lr_video_path = os.path.join(dataset_dir, 'video', args.lr_video_name)
    hr_video_path = os.path.join(dataset_dir, 'video', args.hr_video_name)
    lr_video_profile = get_video_profile(lr_video_path)
    hr_video_profile = get_video_profile(hr_video_path)
    scale = args.output_height // lr_video_profile['height']
    nhwc = [1, lr_video_profile['height'], lr_video_profile['width'], 3]

    #load a dnn
    model = build_model(args.model_type, args.num_blocks, args.num_filters, scale, args.upsample_type)
    checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.lr_video_name, model.name)
    ckpt = tf.train.Checkpoint(model=model)
    ckpt_path = tf.train.latest_checkpoint(checkpoint_dir)
    assert(ckpt_path is not None)
    ckpt.restore(ckpt_path)

    #setup lr, hr frames
    start_time = time.time()
    libvpx.save_rgb_frame(args.vpxdec_file, dataset_dir, args.lr_video_name, limit=args.limit)
    libvpx.save_yuv_frame(args.vpxdec_file, dataset_dir, args.hr_video_name, limit=args.limit, output_width=args.output_width, output_height=args.output_height)
    end_time = time.time()
    print('saving lr, hr image takes {}sec'.format(end_time - start_time))

    start_time = time.time()
    libvpx.setup_sr_frame(args.vpxdec_file, dataset_dir, args.lr_video_name, ckpt.model)
    end_time = time.time()
    print('saving sr image takes {}sec'.format(end_time - start_time))

    #meausure bilinear quality
    libvpx.bilinear_quality(args.vpxdec_file, dataset_dir, args.lr_video_name, args.hr_video_name, args.output_width, args.output_height, limit=args.limit)

    #measure per-frame sr quality
    libvpx.offline_dnn_quality(args.vpxdec_file, dataset_dir, args.lr_video_name, args.hr_video_name, ckpt.model.name, args.output_width, args.output_height, limit=args.limit)

    #measure nemo quality
    start_time = time.time()
    libvpx.offline_cache_quality(args.vpxdec_file, dataset_dir, args.lr_video_name, args.hr_video_name, ckpt.model.name, args.algorithm, args.output_width, args.output_height, limit=args.limit)
    end_time = time.time()
    print('measuring online cache quality takes {}sec'.format(end_time - start_time))

    #remove sr images
    start_time = time.time()
    sr_image_dir = os.path.join(dataset_dir, 'image', args.lr_video_name, ckpt.model.name)
    sr_image_files = glob.glob(os.path.join(sr_image_dir, '*.raw'))
    for sr_image_file in sr_image_files:
        os.remove(sr_image_file)
    end_time = time.time()
    print('removing hr image takes {}sec'.format(end_time-start_time))

    #remove lr, hr images
    start_time = time.time()
    lr_image_dir = os.path.join(dataset_dir, 'image', args.lr_video_name)
    lr_image_files = glob.glob(os.path.join(lr_image_dir, '*.raw'))
    for lr_image_file in lr_image_files:
        os.remove(lr_image_file)
    hr_image_dir = os.path.join(dataset_dir, 'image', args.hr_video_name)
    hr_image_files = []
    hr_image_files += glob.glob(os.path.join(hr_image_dir, '*.y'))
    hr_image_files += glob.glob(os.path.join(hr_image_dir, '*.u'))
    hr_image_files += glob.glob(os.path.join(hr_image_dir, '*.v'))
    for hr_image_file in hr_image_files:
        os.remove(hr_image_file)
    end_time = time.time()
    print('removing lr, hr image takes {}sec'.format(end_time-start_time))
