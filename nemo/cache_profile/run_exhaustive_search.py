import os
import sys
import argparse
import shlex
import math
import time
import multiprocessing as mp
import shutil
import random
import itertools

import numpy as np
import tensorflow as tf

from nemo.tool.video import profile_video
from nemo.tool.libvpx import *
from nemo.tool.mac import count_mac_for_dnn, count_mac_for_cache
import nemo.dnn.model

class ExhaustiveSearcher():
    def __init__(self, model, vpxdec_path, dataset_dir, lr_video_name, hr_video_name, gop, output_width, output_height, \
                 quality_margin, num_decoders):
        self.model = model
        self.vpxdec_path = vpxdec_path
        self.dataset_dir = dataset_dir
        self.lr_video_name = lr_video_name
        self.hr_video_name = hr_video_name
        self.gop = gop
        self.output_width = output_width
        self.output_height = output_height
        self.quality_margin = quality_margin
        self.num_decoders = num_decoders

    #profile all possible anchor point sets
    def _run(self, num_anchor_points, chunk_idx=None, num_iters=None):
        postfix = 'chunk{:04d}'.format(chunk_idx)
        cache_profile_dir = os.path.join(self.dataset_dir, 'profile', self.lr_video_name, self.model.name, postfix)
        log_dir = os.path.join(self.dataset_dir, 'log', self.lr_video_name, self.model.name, postfix)
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(cache_profile_dir, exist_ok=True)
        algorithm_type = 'exhaustive_{}_{}'.format(num_anchor_points, num_iters)

        ###########step 1: measure bilinear, dnn quality##########
        #calculate num_skipped_frames and num_decoded frames
        start_time = time.time()
        lr_video_path = os.path.join(self.dataset_dir, 'video', self.lr_video_name)
        lr_video_profile = profile_video(lr_video_path)
        num_total_frames = int(round(lr_video_profile['frame_rate'], 3) * round(lr_video_profile['duration']))
        num_left_frames = num_total_frames - chunk_idx * self.gop
        assert(num_total_frames == math.floor(num_total_frames))
        num_skipped_frames = chunk_idx * self.gop
        num_decoded_frames = self.gop if num_left_frames >= self.gop else num_left_frames

        #save low-resolution, super-resoluted, high-resolution frames to local storage
        libvpx_save_rgb_frame(self.vpxdec_path, self.dataset_dir, self.lr_video_name, skip=num_skipped_frames, limit=num_decoded_frames, postfix=postfix)
        libvpx_save_yuv_frame(self.vpxdec_path, self.dataset_dir, self.hr_video_name, self.output_width, self.output_height, num_skipped_frames, num_decoded_frames, postfix)
        libvpx_setup_sr_frame(self.vpxdec_path, self.dataset_dir, self.lr_video_name, self.model, postfix)

        #measure bilinear, per-frame super-resolution quality
        quality_bilinear = libvpx_bilinear_quality(self.vpxdec_path, self.dataset_dir, self.lr_video_name, self.hr_video_name, self.output_width, self.output_height,
                                                    num_skipped_frames, num_decoded_frames, postfix)
        quality_dnn = libvpx_offline_dnn_quality(self.vpxdec_path, self.dataset_dir, self.lr_video_name, self.hr_video_name, self.model.name, \
                                                 self.output_width, self.output_height, num_skipped_frames, num_decoded_frames, postfix)

        end_time = time.time()
        print('{} video chunk: (Step1-profile bilinear, dnn quality) {}sec'.format(chunk_idx, end_time - start_time))

        ###########step 2: select anchor points##########
        total_start_time = time.time()
        frames = libvpx_load_frame_index(self.dataset_dir, self.lr_video_name, postfix)
        anchor_point_sets = list(itertools.combinations(frames, num_anchor_points))
        random.shuffle(anchor_point_sets)

        if num_iters is None:
            total_iteration = len(anchor_point_sets)
        else:
            total_iteration = num_iters

        #create multiple processes for quality measurements
        q0 = mp.Queue()
        q1 = mp.Queue()
        decoders = [mp.Process(target=libvpx_offline_cache_quality_mt_v1, args=(q0, q1, self.vpxdec_path, self.dataset_dir, \
                                    self.lr_video_name, self.hr_video_name, self.model.name, self.output_width, self.output_height)) for i in range(self.num_decoders)]
        for decoder in decoders:
            decoder.start()

        #run the SR-integrated codec and measure the quality
        for i in range(total_iteration):
            anchor_point_set = AnchorPointSet.create(frames, cache_profile_dir, '{}_{}'.format(algorithm_type, i))
            for frame in anchor_point_sets[i]:
                anchor_point_set.add_anchor_point(frame)
            q0.put((anchor_point_set, num_skipped_frames, num_decoded_frames, postfix))

        #summarize the results
        count = 0
        min_quality_diff = None
        log_path_0 = os.path.join(log_dir, 'quality_{}.txt'.format(algorithm_type))
        log_path_1 = os.path.join(log_dir, 'result_{}.txt'.format(algorithm_type))
        with open(log_path_0, 'w') as f0, open(log_path_1, 'w') as f1:
            for i in range(total_iteration):
                start_time = time.time()
                item = q1.get()
                quality_cache = item

                quality_log = '{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\n'.format(np.average(quality_cache), np.average(quality_dnn), np.average(quality_bilinear), np.average(quality_dnn) - np.average(quality_cache))
                f0.write(quality_log)

                quality_diff = np.average(np.asarray(quality_dnn) - np.asarray(quality_cache))
                if quality_diff < self.quality_margin:
                    count += 1
                if min_quality_diff is None or quality_diff < min_quality_diff:
                    min_quality_diff = quality_diff

                end_time = time.time()
                print('Iteration {} ({}sec): Percentage {}%, Quality difference {:.4f}dB'.format(i, end_time - start_time, count/(i+1) * 100, quality_diff))

            f1.write('Percentage of anchor point sets whose quality margin is smaller than {}dB: {}%\n'.format(self.quality_margin, count/total_iteration * 100))
            f1.write('Percentage of anchor point sets whose quality margin is bigger than {}dB: {}%\n'.format(self.quality_margin, (total_iteration - count)/total_iteration * 100))
            f1.write('Minimum quality margin: {}dB\n'.format(min_quality_diff))

        #remove the multiple processes
        for decoder in decoders:
            q0.put('end')
        for decoder in decoders:
            decoder.join()

        total_end_time = time.time()
        print('{} number of iterations is finished in {}sec: {}iteration/sec'.format(total_iteration, total_end_time - total_start_time, total_iteration / (total_end_time - total_start_time)))

    def run(self, exhaustive_num_anchor_points, chunk_idx=None, exhaustive_num_iters=None):
        if chunk_idx is not None:
            self._run(exhaustive_num_anchor_points, chunk_idx, exhaustive_num_iters)
        else:
            lr_video_path = os.path.join(self.dataset_dir, 'video', args.lr_video_name)
            lr_video_profile = profile_video(lr_video_path)
            num_chunks = int(math.ceil(lr_video_profile['duration'] / (args.gop / lr_video_profile['frame_rate'])))
            for i in range(num_chunks):
                self._run(exhaustive_num_anchor_points, i, exhaustive_num_iters)

if __name__ == '__main__':
    tf.enable_eager_execution()

    parser = argparse.ArgumentParser()

    #directory, path
    parser.add_argument('--vpxdec_path', type=str, default=None)
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--lr_video_name', type=str, required=True)
    parser.add_argument('--hr_video_name', type=str, required=True)

    #codec
    parser.add_argument('--output_width', type=int, default=1920)
    parser.add_argument('--output_height', type=int, default=1080)

    #dnn
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int)
    parser.add_argument('--num_blocks', type=int)
    parser.add_argument('--upsample_type', type=str, default='deconv')
    parser.add_argument('--train_type', type=str, default='finetune_video')

    #anchor point selector
    parser.add_argument('--quality_margin', type=float, default=0.5)
    parser.add_argument('--gop', type=int, default=120)
    parser.add_argument('--chunk_idx', type=int, default=None)
    parser.add_argument('--num_decoders', default=8, type=int)
    parser.add_argument('--exhaustive_num_anchor_points', type=int, default=3)
    parser.add_argument('--exhaustive_num_iters', type=int, default=None)

    args = parser.parse_args()

    if args.vpxdec_path is None:
        args.vpxdec_path = os.path.join(os.environ['NEMO_ROOT'], 'third_party', 'libvpx', 'bin', 'vpxdec_nemo_ver2_x86')
        assert(os.path.exists(args.vpxdec_path))

    #profile videos
    dataset_dir = os.path.join(args.data_dir, args.content)
    lr_video_path = os.path.join(dataset_dir, 'video', args.lr_video_name)
    hr_video_path = os.path.join(dataset_dir, 'video', args.hr_video_name)
    print(lr_video_path)
    lr_video_profile = profile_video(lr_video_path)
    hr_video_profile = profile_video(hr_video_path)
    scale = args.output_height // lr_video_profile['height']
    nhwc = [1, lr_video_profile['height'], lr_video_profile['width'], 3]

    #load a dnn
    model = nemo.dnn.model.build(args.model_type, args.num_blocks, args.num_filters, scale, args.upsample_type)
    if args.train_type == 'train_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.lr_video_name, model.name)
    elif args.train_type == 'finetune_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.lr_video_name, '{}_finetune'.format(model.name))
    elif args.train_type == 'train_div2k':
        checkpoint_dir = os.path.join(args.data_dir, 'DIV2K', 'checkpoint', 'DIV2K_X{}'.format(scale), model.name)
    else:
        raise ValueError('Unsupported training types')
    ckpt = tf.train.Checkpoint(model=model)
    ckpt_path = tf.train.latest_checkpoint(checkpoint_dir)
    ckpt.restore(ckpt_path)

    #run es
    es = ExhaustiveSearcher(ckpt.model, args.vpxdec_path, dataset_dir, args.lr_video_name, args.hr_video_name, args.gop, \
                              args.output_width, args.output_height, args.quality_margin, args.num_decoders)
    es.run(args.exhaustive_num_anchor_points, args.chunk_idx, args.exhaustive_num_iters)
