import os
import sys
import math
import time
import multiprocessing as mp
import shutil
import numpy as np
import tensorflow as tf
from nemo.tool.video import get_video_profile
import nemo.tool.libvpx as libvpx

class APS_NEMO():
    NAME0 = "APS"
    NAME1 = "NEMO"

    def __init__(self, model, args):
        self.model = args.model
        self.vpxdec_file = args.vpxdec_file
        self.dataset_dir = args.dataset_dir
        self.lr_video_name = args.lr_video_name
        self.hr_video_name = args.hr_video_name
        self.gop = args.gop
        self.threshold = args.threshold
        self.num_decoders = args.num_decoders

    # select a cache profile that results in the highest estimated quality
    def _select_anchor_point(self, cache_profile, ap_cache_profiles):
        max_estimated_quality = None
        max_avg_estimated_quality = None
        idx = None

        for i, ap_cache_profile in enumerate(ap_cache_profiles):
            estimated_quality = self._estimate_quality(cache_profile, ap_cache_profile)
            avg_estimated_quality = np.average(estimated_quality)
            if idx is None or avg_estimated_quality > max_avg_estimated_quality:
                max_avg_estimated_quality = avg_estimated_quality
                max_estimated_quality = estimated_quality
                idx = i

        return idx, max_estimated_quality

    # estimate the quality of cache profile
    def _estimate_quality(self, curr_cache_profile, new_cache_profile):
        if curr_cache_profile is not None:
            return np.maximum(curr_cache_profile.estimated_quality, new_cache_profile.measured_quality)
        else:
            return new_cache_profile.measured_quality

    # generate a cache profile per chunk & log video quality per chunk
    def run(self, chunk_idx):
        # step 1 : analyze anchor frames
        # setup directory
        postfix = 'chunk{:04d}'.format(chunk_idx)
        profile_dir = os.path.join(self.dataset_dir, 'profile', self.lr_video_name, self.model.name, postfix)
        os.makedirs(profile_dir, exist_ok=True)

        # setup frame indexes
        start_time = time.time()
        lr_video_file = os.path.join(self.dataset_dir, 'video', self.lr_video_name)
        lr_video_profile = get_video_profile(lr_video_file)
        total_frames = int(round(lr_video_profile['frame_rate'], 3) * round(lr_video_profile['duration']))
        left_frames = int(total_frames - chunk_idx * self.gop)
        assert(total_frames == math.floor(total_frames))
        start_idx = chunk_idx * self.gop
        end_idx = self.gop if left_frames >= self.gop else left_frames

        # setup lr, sr, hr frames
        libvpx.save_frame(self.vpxdec_file, self.dataset_dir, self.lr_video_name, start_idx, end_idx, postfix)
        libvpx.save_frame(self.vpxdec_file, self.dataset_dir, self.hr_video_name, start_idx, end_idx, postfix)
        libvpx.setup_sr_frame(self.vpxdec_file, self.dataset_dir, self.lr_video_name, self.model, postfix)

        # measure bilinear, per-frame SR video quality
        quality_bilinear = libvpx.bilinear_quality(self.vpxdec_file, self.dataset_dir, self.lr_video_name, self.hr_video_name, \
                                                    start_idx, end_idx, postfix)
        quality_dnn = libvpx.offline_dnn_quality(self.vpxdec_file, self.dataset_dir, self.lr_video_name, self.hr_video_name, \
                                                    self.model.name, lr_video_profile['height'], start_idx, end_idx, postfix)
        end_time = time.time()
        print('{} video chunk: (Step1-profile bilinear, dnn quality) {}sec'.format(chunk_idx, end_time - start_time))

        # measure video qualities of cache profiles with a single anchor frame
        start_time = time.time()
        frames = libvpx.load_frame_index(self.dataset_dir, self.lr_video_name, postfix)
        q0 = mp.Queue()
        q1 = mp.Queue()
        decoders = [mp.Process(target=libvpx.offline_cache_quality_mt, args=(q0, q1, self.vpxdec_file, self.dataset_dir, \
                                    self.lr_video_name, self.hr_video_name, self.model.name, lr_video_profile['height'])) for i in range(self.num_decoders)]
        for decoder in decoders:
            decoder.start()
        ap_cache_profiles = []
        for idx, frame in enumerate(frames):
            cache_profile = CacheProfile.fromframes(frames, profile_dir, '{}_{}.tmp'.format(self.NAME0, frame.name))
            cache_profile.add_anchor_point(frame)
            cache_profile.save()
            q0.put((cache_profile.path, start_idx, end_idx, postfix, idx))
            ap_cache_profiles.append(cache_profile)
        for frame in frames:
            item = q1.get()
            idx = item[0]
            quality = item[1]
            ap_cache_profiles[idx].set_measured_quality(quality)
            ap_cache_profiles[idx].remove()
        for decoder in decoders:
            q0.put('end')
        for decoder in decoders:
            decoder.join()
        end_time = time.time()
        print('{} video chunk: (Step1-profile anchor point quality) {}sec'.format(chunk_idx, end_time - start_time))

        # step 2 : order anchor frames
        start_time = time.time()
        ordered_cache_profiles = []
        cache_profile = None
        while len(ap_cache_profiles) > 0:
            idx, estimated_quality = self._select_anchor_point(cache_profile, ap_cache_profiles)
            ap_cache_profile = ap_cache_profiles.pop(idx)
            #print('_select_cache_profile: {} anchor points, {} chunk'.format(ap_cache_profile.anchor_points[0].name, chunk_idx))
            if len(ordered_cache_profiles) == 0:
                cache_profile = CacheProfile.fromcacheprofile(ap_cache_profile, profile_dir, '{}_{}.tmp'.format(self.NAME1, len(ap_cache_profile.anchor_points)))
                cache_profile.set_estimated_quality(ap_cache_profile.measured_quality)
            else:
                cache_profile = CacheProfile.fromcacheprofile(ordered_cache_profiles[-1], profile_dir, '{}_{}.tmp'.format(self.NAME1, len(ordered_cache_profiles[-1].anchor_points) + 1))
                cache_profile.add_anchor_point(ap_cache_profile.anchor_points[0])
                cache_profile.set_estimated_quality(estimated_quality)
            ordered_cache_profiles.append(cache_profile)
        end_time = time.time()
        print('{} video chunk: (Step2) {}sec'.format(chunk_idx, end_time - start_time))

        # step 3 : generate a cache profile
        start_time = time.time()
        log_dir = os.path.join(self.dataset_dir, 'log', self.lr_video_name, self.model.name, \
                '{}_{}'.format(self.NAME1, self.threshold), postfix)
        os.makedirs(log_dir, exist_ok=True)
        quality_log_file = os.path.join(log_dir, 'quality.txt')

        found = False
        with open(quality_log_file, 'w') as f:
            for cache_profile in ordered_cache_profiles:
                # log video qualities
                cache_profile.save()
                quality_cache = libvpx.offline_cache_quality(self.vpxdec_file, self.dataset_dir, self.lr_video_name, self.hr_video_name, \
                                                    self.model.name, cache_profile.path, lr_video_profile['height'], start_idx, end_idx, postfix)
                cache_profile.remove()
                quality_diff = np.asarray(quality_dnn) - np.asarray(quality_cache)
                quality_error =  np.percentile(np.asarray(quality_dnn) - np.asarray(quality_cache) \
                                                            ,[95, 99, 100], interpolation='nearest')
                #frame_count_1 = sum(map(lambda x : x >= 0.5, quality_diff))
                #frame_count_2 = sum(map(lambda x : x >= 1.0, quality_diff))
                frame_count_3 = sum(map(lambda x : x >= 2.0, quality_diff))
                #frame_count_4 = sum(map(lambda x : x >= 3.0, quality_diff))
                quality_log = '{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\n'.format(len(cache_profile.anchor_points), np.average(quality_cache), np.average(quality_dnn), np.average(quality_bilinear), np.average(cache_profile.estimated_quality))
                f.write(quality_log)

                print('{} video chunk, {} anchor points: PSNR(Cache)={:.2f}, PSNR(SR)={:.2f}, PSNR(Bilinear)={:.2f}'.format( \
                                        chunk_idx, len(cache_profile.anchor_points), np.average(quality_cache), np.average(quality_dnn), \
                                        np.average(quality_bilinear)))

                # check quality difference
                if np.average(quality_diff) <= self.threshold and found == False:
                    cache_profile.name = '{}_{}.profile'.format(self.NAME1, self.threshold)
                    cache_profile.save()
                    libvpx.offline_cache_quality(self.vpxdec_file, self.dataset_dir, self.lr_video_name, self.hr_video_name, \
                                        self.model.name, cache_profile.path, lr_video_profile['height'], start_idx, end_idx, postfix)
                    break

        end_time = time.time()
        print('{} video chunk: (Step3) {}sec'.format(chunk_idx, end_time - start_time))

        # remove images
        lr_image_dir = os.path.join(self.dataset_dir, 'image', self.lr_video_name, postfix)
        hr_image_dir = os.path.join(self.dataset_dir, 'image', self.hr_video_name, postfix)
        sr_image_dir = os.path.join(self.dataset_dir, 'image', self.lr_video_name, self.model.name, postfix)
        shutil.rmtree(lr_image_dir, ignore_errors=True)
        shutil.rmtree(hr_image_dir, ignore_errors=True)
        shutil.rmtree(sr_image_dir, ignore_errors=True)

    # merge (per-chunk) log files & cache profiles
    def summary(self, start_idx, end_idx):
        log_dir = os.path.join(self.dataset_dir, 'log', self.lr_video_name, self.model.name, '{}_{}'.format(self.NAME1, self.threshold))
        profile_dir = os.path.join(self.dataset_dir, 'profile', self.lr_video_name, self.model.name)

        # merge log files
        quality_summary_file = os.path.join(log_dir, 'quality.txt')
        error_summary_file = os.path.join(log_dir, 'error.txt')
        mac_summary_file = os.path.join(log_dir, 'mac.txt')
        with open(quality_summary_file, 'w') as sf0, open(error_summary_file, 'w') as sf1, open(mac_summary_file, 'w') as sf2:
            for chunk_idx in range(start_idx, end_idx + 1):
                chunk_log_dir = os.path.join(log_dir, 'chunk{:04d}'.format(chunk_idx))
                if not os.path.exists(chunk_log_dir):
                    break
                else:
                    quality_log_file = os.path.join(chunk_log_dir, 'quality.txt')
                    error_log_file = os.path.join(chunk_log_dir, 'error.txt')
                    mac_log_file = os.path.join(chunk_log_dir, 'mac.txt')
                    with open(quality_log_file, 'r') as lf0, open(error_log_file, 'r') as lf1, open(mac_log_file, 'r') as lf2:
                        q_lines = lf0.readlines()
                        e_lines = lf1.readlines()
                        m_lines = lf2.readlines()
                        sf0.write('{}\t{}\n'.format(chunk_idx, q_lines[-1].strip()))
                        sf1.write('{}\t{}\n'.format(chunk_idx, e_lines[-1].strip()))
                        sf2.write('{}\t{}\n'.format(chunk_idx, m_lines[-1].strip()))

        # merge cache profiles
        cache_profile = os.path.join(profile_dir, '{}_{}.profile'.format(self.NAME1, self.threshold))
        cache_data = b''
        with open(cache_profile, 'wb') as f0:
            for chunk_idx in range(start_idx, end_idx):
                chunk_cache_profile = os.path.join(profile_dir, 'chunk{:04d}'.format(chunk_idx), '{}_{}.profile'.format(self.NAME1, self.threshold))
                with open(chunk_cache_profile, 'rb') as f1:
                    f0.write(f1.read())
