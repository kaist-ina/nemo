import os
import sys
import re

import tensorflow as tf
from tensorflow.python.framework import tensor_shape
from tensorflow.python.data.experimental import AUTOTUNE

"""
image dataset used for training and testing DNNs
"""

def sample_and_save_images(video_path, image_dir, sample_fps, ffmpeg_path='/usr/bin/ffmpeg'):
    log_path = os.path.join(image_dir, 'ffmpeg.log')

    if not os.path.exists(log_path):
        os.makedirs(image_dir, exist_ok=True)
        video_name = os.path.basename(video_path)
        if sample_fps is not None:
            cmd = '{} -i {} -vf fps={} {}/%04d.png'.format(ffmpeg_path, video_path, sample_fps, image_dir)
        else:
            cmd = '{} -i {} {}/%04d.png'.format(ffmpeg_path, video_path, image_dir)
        os.system(cmd)
        os.mknod(log_path)

def random_crop(lr_image, hr_image, lr_crop_size, scale):
    lr_image_shape = tf.shape(lr_image)[:2]

    lr_w = tf.random.uniform(shape=(), maxval=lr_image_shape[1] - lr_crop_size + 1, dtype=tf.int32)
    lr_h = tf.random.uniform(shape=(), maxval=lr_image_shape[0] - lr_crop_size + 1, dtype=tf.int32)

    hr_crop_size = lr_crop_size * scale
    hr_w = lr_w * scale
    hr_h = lr_h * scale

    lr_image_cropped = lr_image[lr_h:lr_h + lr_crop_size, lr_w:lr_w + lr_crop_size]
    hr_image_cropped = hr_image[hr_h:hr_h + hr_crop_size, hr_w:hr_w + hr_crop_size]

    return lr_image_cropped, hr_image_cropped

def decode_and_resize_image(image_file, image_shape):
    img = tf.image.decode_image(image_file, channels=image_shape[2])
    img = tf.expand_dims(img, 0)
    img = tf.image.resize_bilinear(img, (image_shape[0], image_shape[1]), half_pixel_centers=True)
    img = tf.clip_by_value(img, 0, 255)
    img = tf.round(img)
    img = tf.squeeze(img)
    img = tf.cast(img, tf.uint8)
    return img

def image_dataset(image_dir, image_shape, image_format, num_samples=None):
    m = re.compile(image_format)
    if num_samples is None:
        img_paths = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if m.search(f)])
    else:
        img_paths = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if m.search(f)])
        skip = len(img_paths) // num_samples
        img_paths = img_paths[0:-1:skip]
    ds = tf.data.Dataset.from_tensor_slices(img_paths)
    ds = ds.map(tf.io.read_file)
    if image_shape is None:
        ds = ds.map(lambda x: tf.image.decode_image(x, channels=3), num_parallel_calls=AUTOTUNE)
    else:
        ds = ds.map(lambda x: decode_and_resize_image(x, image_shape=image_shape), num_parallel_calls=AUTOTUNE)
    return ds, len(img_paths)

def single_image_dataset(image_dir, image_format='.png'):
    ds, _ = image_dataset(image_dir, image_format)
    ds = ds.batch(1)
    ds = ds.repeat(1)
    ds = ds.prefetch(buffer_size=AUTOTUNE)
    return ds

def train_video_dataset(lr_image_dir, hr_image_dir, lr_image_shape, hr_image_shape, batch_size, patch_size, load_on_memory, repeat_count=None, image_format='.png'):
    assert(hr_image_shape[0] / lr_image_shape[0] == hr_image_shape[1] / lr_image_shape[1])
    assert(hr_image_shape[0] % lr_image_shape[0] == 0)
    assert(hr_image_shape[1] % lr_image_shape[1] == 0)

    scale = hr_image_shape[0] // lr_image_shape[0]

    lr_ds, num_imgs = image_dataset(lr_image_dir, lr_image_shape, image_format)
    hr_ds, _ = image_dataset(hr_image_dir, hr_image_shape, image_format)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    if load_on_memory: ds = ds.cache()
    ds = ds.shuffle(buffer_size=num_imgs)
    ds = ds.map(lambda lr, hr: random_crop(lr, hr, patch_size, scale), num_parallel_calls=AUTOTUNE)
    ds = ds.batch(batch_size)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)

    print('number of train images: {}'.format(num_imgs))
    return ds

def test_video_dataset(lr_image_dir, hr_image_dir, lr_image_shape, hr_image_shape, num_samples, load_on_memory, repeat_count=1, image_format='.png'):
    lr_ds, num_imgs = image_dataset(lr_image_dir, lr_image_shape, image_format, num_samples)
    hr_ds, _ = image_dataset(hr_image_dir, hr_image_shape, image_format, num_samples)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    if load_on_memory: ds = ds.cache()
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    ds = ds.batch(1)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)

    ds.num_images= num_imgs
    print('number of test images: {}'.format(num_imgs))
    return ds

def train_video_dataset(lr_image_dir, hr_image_dir, lr_image_shape, hr_image_shape, batch_size, patch_size, load_on_memory, repeat_count=None, image_format='.png'):
    assert(hr_image_shape[0] / lr_image_shape[0] == hr_image_shape[1] / lr_image_shape[1])
    assert(hr_image_shape[0] % lr_image_shape[0] == 0)
    assert(hr_image_shape[1] % lr_image_shape[1] == 0)

    scale = hr_image_shape[0] // lr_image_shape[0]

    lr_ds, num_imgs = image_dataset(lr_image_dir, lr_image_shape, image_format)
    hr_ds, _ = image_dataset(hr_image_dir, hr_image_shape, image_format)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    if load_on_memory: ds = ds.cache()
    ds = ds.shuffle(buffer_size=num_imgs)
    ds = ds.map(lambda lr, hr: random_crop(lr, hr, patch_size, scale), num_parallel_calls=AUTOTUNE)
    ds = ds.batch(batch_size)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)

    ds.num_images = num_imgs
    print('number of train images: {}'.format(num_imgs))
    return ds

def test_video_dataset(lr_image_dir, hr_image_dir, lr_image_shape, hr_image_shape, num_samples, load_on_memory, repeat_count=1, image_format='.png'):
    lr_ds, num_imgs = image_dataset(lr_image_dir, lr_image_shape, image_format, num_samples)
    hr_ds, _ = image_dataset(hr_image_dir, hr_image_shape, image_format, num_samples)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    if load_on_memory: ds = ds.cache()
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    ds = ds.batch(1)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)

    ds.num_images = num_imgs
    print('number of test images: {}'.format(num_imgs))
    return ds

def train_div2k_dataset(lr_image_dir, hr_image_dir, scale, batch_size, patch_size, load_on_memory, repeat_count=None, image_format='.png'):
    lr_ds, num_imgs = image_dataset(lr_image_dir, None, image_format)
    hr_ds, _ = image_dataset(hr_image_dir, None, image_format)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    if load_on_memory: ds = ds.cache()
    ds = ds.shuffle(buffer_size=num_imgs)
    ds = ds.map(lambda lr, hr: random_crop(lr, hr, patch_size, scale), num_parallel_calls=AUTOTUNE)
    ds = ds.batch(batch_size)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)

    ds.num_images = num_imgs
    print('number of train images: {}'.format(num_imgs))
    return ds

def test_div2k_dataset(lr_image_dir, hr_image_dir, scale, num_samples, load_on_memory, repeat_count=1, image_format='.png'):
    lr_ds, num_imgs = image_dataset(lr_image_dir, None, image_format, num_samples)
    hr_ds, _ = image_dataset(hr_image_dir, None, image_format, num_samples)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    if load_on_memory: ds = ds.cache()
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    ds = ds.batch(1)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)

    ds.num_images = num_imgs
    print('number of test images: {}'.format(num_imgs))
    return ds

"""
raw image dataset to apply DNNs to libvpx frames
"""
#TODO: refactor below functions as above

def decode_raw(filepath, width, height, channel, precision):
    file = tf.io.read_file(filepath)
    if tf.__version__.startswith('2'):
        image = tf.io.decode_raw(file, precision)
    else:
        image = tf.decode_raw(file, precision)
    image = tf.reshape(image, [height, width, channel])
    #return image, filepath
    return image

def decode_raw_with_name(filepath, width, height, channel, precision):
    file = tf.io.read_file(filepath)
    if tf.__version__.startswith('2'):
        image = tf.io.decode_raw(file, precision)
    else:
        image = tf.decode_raw(file, precision)
    image = tf.reshape(image, [height, width, channel])
    return image, filepath

def raw_dataset(image_dir, width, height, channel, exp, precision):
    m = re.compile(exp)
    images = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if m.search(f)])
    #images = sorted(glob.glob('{}/{}'.format(image_dir, pattern)))
    #images = sorted(glob.glob('{}/[0-9][0-9][0-9][0-9].raw'.format(image_dir)))
    ds = tf.data.Dataset.from_tensor_slices(images)
    ds = ds.map(lambda x: decode_raw(x, width, height, channel, precision), num_parallel_calls=AUTOTUNE)
    return ds, len(images)

def single_raw_dataset(image_dir, width, height, channel, exp, repeat_count=1, precision=tf.uint8):
    ds, length = raw_dataset(image_dir, width, height, channel, exp, precision)
    ds = ds.batch(1)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)
    return ds

def single_raw_dataset_with_name(image_dir, width, height, channel, exp, repeat_count=1, precision=tf.uint8):
    m = re.compile(exp)
    images = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if m.search(f)])
    ds = tf.data.Dataset.from_tensor_slices(images)
    ds = ds.map(lambda x: decode_raw_with_name(x, width, height, channel, precision), num_parallel_calls=AUTOTUNE)
    ds = ds.batch(1)
    ds = ds.repeat(1)
    ds = ds.prefetch(buffer_size=AUTOTUNE)
    return ds

def train_raw_dataset(lr_image_dir, hr_image_dir, width, height, channel, scale, batch_size, patch_size, load_on_memory, exp, repeat_count=None, precision=tf.uint8):
    lr_ds, length = raw_dataset(lr_image_dir, width, height, channel, exp, precision)
    hr_ds, _ = raw_dataset(hr_image_dir, width * scale, height * scale, channel, exp, precision)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    if load_on_memory: ds = ds.cache()
    ds = ds.shuffle(buffer_size=length)
    ds = ds.map(lambda lr, hr: random_crop(lr, hr, patch_size, scale), num_parallel_calls=AUTOTUNE)
    ds = ds.batch(batch_size)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)
    return ds

def valid_raw_dataset(lr_image_dir, hr_image_dir, width, height, channel, scale, exp, repeat_count=1, precision=tf.uint8):
    lr_ds, length = raw_dataset(lr_image_dir, width, height, channel, exp, precision)
    hr_ds, _ = raw_dataset(hr_image_dir, width * scale, height * scale, channel, exp, precision)
    ds = tf.data.Dataset.zip((lr_ds, hr_ds))
    ds = ds.batch(1)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)
    return ds

def summary_raw_dataset(lr_image_dir, sr_image_dir, hr_image_dir, width, height, channel, scale, exp, repeat_count=1, precision=tf.uint8):
    lr_ds, length = raw_dataset(lr_image_dir, width, height, channel, exp, precision)
    hr_ds, _ = raw_dataset(hr_image_dir, width * scale, height * scale, channel, exp, precision)
    sr_ds, _ = raw_dataset(sr_image_dir, width * scale, height * scale, channel, exp, precision)
    ds = tf.data.Dataset.zip((lr_ds, sr_ds, hr_ds))
    ds = ds.batch(1)
    ds = ds.repeat(repeat_count)
    ds = ds.prefetch(buffer_size=AUTOTUNE)
    return ds
