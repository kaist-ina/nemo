import os, time, sys, time
import subprocess
import argparse
import collections
import json
import importlib

import numpy as np

import nemo.dnn.model
from nemo.tool.snpe import snpe_convert_model, snpe_convert_dataset, snpe_benchmark, snpe_benchmark_random_config
from nemo.tool.video import profile_video

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #path
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--video_name', type=str, required=True)
    parser.add_argument('--ffmpeg_path', type=str, default='/usr/bin/ffmpeg')

    #training
    parser.add_argument('--train_type', type=str, required=True)

    #dnn
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int, required=True)
    parser.add_argument('--num_blocks', type=int, required=True)
    parser.add_argument('--scale', type=int, required=True)
    parser.add_argument('--upsample_type', type=str, default='deconv')

    #device
    parser.add_argument('--device_id', type=str, required=True)
    parser.add_argument('--runtime', type=str, default='GPU_FP16')

    args = parser.parse_args()

    video_path = os.path.join(args.data_dir, args.content, 'video', args.video_name)
    video_profile = profile_video(video_path)
    input_shape = [1, video_profile['height'], video_profile['width'], 3]

    model = nemo.dnn.model.build(args.model_type, args.num_blocks, args.num_filters, args.scale, args.upsample_type, apply_clip=True)
    if args.train_type == 'train_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.video_name, model.name)
        log_dir = os.path.join(args.data_dir, args.content, 'log', args.video_name, model.name, 'snpe_random_benchmark')
    elif args.train_type == 'finetune_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.video_name, '{}_finetune'.format(model.name))
        log_dir = os.path.join(args.data_dir, args.content, 'log', args.video_name, '{}_finetune'.format(model.name), 'snpe_random_benchmark')
    else:
        raise ValueError('Unsupported training types')

    dlc_path = os.path.join(checkpoint_dir, '{}.dlc'.format(model.name))
    snpe_convert_model(model, input_shape, checkpoint_dir)

    json_path = snpe_benchmark_random_config(args.device_id, args.runtime, model.name, dlc_path, log_dir)
    snpe_benchmark(json_path)
