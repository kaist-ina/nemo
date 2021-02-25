import time
import argparse
import os
import sys

import tensorflow as tf

from nemo.dnn.dataset import train_video_dataset, test_video_dataset, sample_and_save_images
from nemo.dnn.trainer import NEMOTrainer
from nemo.dnn.utility import build_model, resolve_bilinear
from nemo.tool.video import get_video_profile

if __name__ == '__main__':
    tf.enable_eager_execution()

    parser = argparse.ArgumentParser()

    #dataset
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--lr_video_name', type=str, required=True)
    parser.add_argument('--hr_video_name', type=str, required=True)
    parser.add_argument('--sample_fps', type=float, default=1.0)
    parser.add_argument('--output_height', type=int, default=1080)

    #testing
    parser.add_argument('--load_on_memory', action='store_true')
    parser.add_argument('--train_type', type=str, required=True)

    #dnn
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int, required=True)
    parser.add_argument('--num_blocks', type=int, required=True)
    parser.add_argument('--upsample_type', type=str, default='deconv')

    #tool
    parser.add_argument('--ffmpeg_path', type=str, default='/usr/bin/ffmpeg')

    args = parser.parse_args()

    lr_video_path = os.path.join(args.data_dir, args.content, 'video', args.lr_video_name)
    hr_video_path = os.path.join(args.data_dir, args.content, 'video', args.hr_video_name)
    lr_video_profile = get_video_profile(lr_video_path)
    hr_video_profile = get_video_profile(hr_video_path)
    scale = args.output_height// lr_video_profile['height'] #NEMO upscales a LR image to a 1080p version
    lr_image_shape = [lr_video_profile['height'], lr_video_profile['width'], 3]
    hr_image_shape = [lr_video_profile['height'] * scale, lr_video_profile['width'] * scale, 3]


    lr_image_dir = os.path.join(args.data_dir, args.content, 'image', args.lr_video_name, '{}fps'.format(args.sample_fps))
    hr_image_dir = os.path.join(args.data_dir, args.content, 'image', args.hr_video_name, '{}fps'.format(args.sample_fps))
    sample_and_save_images(lr_video_path, lr_image_dir, args.sample_fps, args.ffmpeg_path)
    sample_and_save_images(hr_video_path, hr_image_dir, args.sample_fps, args.ffmpeg_path)

    test_ds = test_video_dataset(lr_image_dir, hr_image_dir, lr_image_shape, hr_image_shape, None, args.load_on_memory)

    model = build_model(args.model_type, args.num_blocks, args.num_filters, scale, args.upsample_type)
    if args.train_type == 'train_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.lr_video_name, model.name)
        result_dir = os.path.join(args.data_dir, args.content, 'result', args.lr_video_name, model.name)
    elif args.train_type == 'finetune_video':
        checkpoint_dir = os.path.join(args.data_dir, args.content, 'checkpoint', args.lr_video_name, '{}_finetune'.format(model.name))
        result_dir = os.path.join(args.data_dir, args.content, 'result', args.lr_video_name, '{}_finetune'.format(model.name))
    elif args.train_type == 'train_div2k':
        checkpoint_dir = os.path.join(args.data_dir, 'DIV2K', 'checkpoint', 'DIV2K_X{}'.format(scale), model.name)
        result_dir = os.path.join(args.data_dir, args.content, 'result', 'DIV2K_X{}'.format(scale), model.name)
    else:
        raise ValueError('Unsupported training types')
    ckpt = tf.train.Checkpoint(model=model)
    ckpt_path = tf.train.latest_checkpoint(checkpoint_dir)
    ckpt.restore(ckpt_path)

    os.makedirs(result_dir, exist_ok=True)
    log_path = os.path.join(result_dir, 'quality_{}fps.txt'.format(args.sample_fps))
    with open(log_path, 'w') as f:
        progbar = tf.keras.utils.Progbar(test_ds.num_images)
        for idx, imgs in enumerate(test_ds):
            lr_img = imgs[0]
            hr_img = imgs[1]

            lr_img = tf.cast(lr_img, tf.float32)
            sr_img = ckpt.model(lr_img)
            sr_img = tf.clip_by_value(sr_img, 0, 255)
            sr_img = tf.round(sr_img)
            sr_img = tf.cast(sr_img, tf.uint8)
            sr_psnr = tf.image.psnr(sr_img, hr_img, max_val=255)[0]

            height = tf.shape(hr_img)[1]
            width = tf.shape(hr_img)[2]
            bilinear_img = resolve_bilinear(lr_img, height, width)
            bilinear_psnr = tf.image.psnr(bilinear_img, hr_img, max_val=255)[0]

            if tf.math.is_inf(bilinear_psnr):
                bilinear_psnr = 100
            if tf.math.is_inf(sr_psnr):
                sr_psnr = 100

            f.write('{:.4f}\t{:.4f}\t{:.4f}\n'.format(sr_psnr, bilinear_psnr, sr_psnr - bilinear_psnr))
            progbar.update(idx+1)

            """
            sr_img = tf.squeeze(sr_img)
            sr_img = tf.image.encode_png(tf.cast(sr_img, tf.uint8))
            bilinear_img = tf.squeeze(bilinear_img)
            bilinear_img = tf.image.encode_png(tf.cast(bilinear_img, tf.uint8))
            image_dir = os.path.join(args.data_dir, args.content, 'image', args.lr_video_name, model.name)
            os.makedirs(image_dir, exist_ok=True)
            tf.io.write_file(os.path.join(image_dir, 'sr_{:04d}.png'.format(idx)), sr_img)
            tf.io.write_file(os.path.join(image_dir, 'bilinear_{:04d}.png'.format(idx)), bilinear_img)
            print(sr_psnr, bilinear_psnr)
            """
