import time
import shlex
import subprocess
import json
import os
import math

import numpy as np
import tensorflow as tf

from nemo.dnn.dataset import valid_raw_dataset, summary_raw_dataset
import nemo.dnn.nemo_s as nemo_s

# ---------------------------------------
# Model
# ---------------------------------------

def build_model(model_type, num_blocks, num_filters, scale, upsample_type, apply_clip=None, output_shape=None):
    if model_type == 'nemo_s':
        model = nemo_s.NEMO_S(num_blocks, num_filters, scale, upsample_type).build(output_shape=output_shape, apply_clip=apply_clip)
    else:
        raise NotImplementedError('Unsupported model: {}'.format(model_type))
    return model

# ---------------------------------------
# Video
# ---------------------------------------


# ---------------------------------------
# Inference
# ---------------------------------------

def raw_bilinear_quality(lr_raw_dir, hr_raw_dir, nhwc, scale):
    bilinear_psnr_values = []
    valid_raw_ds = valid_raw_dataset(lr_raw_dir, hr_raw_dir, nhwc[1], nhwc[2],
                                                    scale, precision=tf.float32)
    for idx, imgs in enumerate(valid_raw_ds):
        lr = imgs[0][0]
        hr = imgs[1][0]

        bilinear = resolve_bilinear(lr, nhwc[1] * scale, nhwc[2] * scale)
        bilinear = tf.cast(bilinear, tf.uint8)
        hr = tf.clip_by_value(hr, 0, 255)
        hr = tf.round(hr)
        hr = tf.cast(hr, tf.uint8)

        bilinear_psnr_value = tf.image.psnr(bilinear, hr, max_val=255)[0].numpy()
        bilinear_psnr_values.append(bilinear_psnr_value)

    return bilinear_psnr_values

def raw_sr_quality(sr_raw_dir, hr_raw_dir, nhwc, scale):
    sr_psnr_values = []
    valid_raw_ds = valid_raw_dataset(sr_raw_dir, hr_raw_dir, nhwc[1] * scale,
                                                    nhwc[2] * scale,
                                                    1, precision=tf.float32)
    for idx, imgs in enumerate(valid_raw_ds):
        sr = imgs[0][0]
        hr = imgs[1][0]

        sr = tf.clip_by_value(sr, 0, 255)
        sr = tf.round(sr)
        sr = tf.cast(sr, tf.uint8)
        hr = tf.clip_by_value(hr, 0, 255)
        hr = tf.round(hr)
        hr = tf.cast(hr, tf.uint8)

        sr_psnr_value = tf.image.psnr(sr, hr, max_val=255)[0].numpy()
        sr_psnr_values.append(sr_psnr_value)

    return sr_psnr_values

def raw_quality(lr_raw_dir, sr_raw_dir, hr_raw_dir, nhwc, scale, precision=tf.float32):
    bilinear_psnr_values= []
    sr_psnr_values = []
    summary_raw_ds = summary_raw_dataset(lr_raw_dir, sr_raw_dir, hr_raw_dir, nhwc[1], nhwc[2],
                                                    scale, precision=precision)
    for idx, imgs in enumerate(summary_raw_ds):
        lr = imgs[0][0]
        sr = imgs[1][0]
        hr = imgs[2][0]

        if precision == tf.float32:
            hr = tf.clip_by_value(hr, 0, 255)
            hr = tf.round(hr)
            hr = tf.cast(hr, tf.uint8)
            sr = tf.clip_by_value(sr, 0, 255)
            sr = tf.round(sr)
            sr = tf.cast(sr, tf.uint8)

        bilinear = resolve_bilinear_tf(lr, nhwc[1] * scale, nhwc[2] * scale)
        bilinear_psnr_value = tf.image.psnr(bilinear, hr, max_val=255)[0].numpy()
        bilinear_psnr_values.append(bilinear_psnr_value)
        sr_psnr_value = tf.image.psnr(sr, hr, max_val=255)[0].numpy()
        sr_psnr_values.append(sr_psnr_value)
        print('{} frame: PSNR(SR)={:.2f}, PSNR(Bilinear)={:.2f}'.format(idx, sr_psnr_value, bilinear_psnr_value))
    print('Summary: PSNR(SR)={:.2f}, PSNR(Bilinear)={:.2f}'.format(np.average(sr_psnr_values), np.average(bilinear_psnr_values)))

    return sr_psnr_values, bilinear_psnr_values

def resolve(model, lr_batch):
    lr_batch = tf.cast(lr_batch, tf.float32)
    sr_batch = model(lr_batch)
    sr_batch = tf.clip_by_value(sr_batch, 0, 255)
    sr_batch = tf.round(sr_batch)
    sr_batch = tf.cast(sr_batch, tf.uint8)
    return sr_batch

def resolve_bilinear(lr_batch, height, width):
    lr_batch = tf.cast(lr_batch, tf.float32)
    bilinear_batch = tf.image.resize_bilinear(lr_batch, (height, width), half_pixel_centers=True)
    bilinear_batch = tf.clip_by_value(bilinear_batch, 0, 255)
    bilinear_batch = tf.round(bilinear_batch)
    bilinear_batch = tf.cast(bilinear_batch, tf.uint8)
    return bilinear_batch
