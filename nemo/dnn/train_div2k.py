import time
import argparse
import os
import sys

import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Mean
from tensorflow.keras.losses import MeanAbsoluteError
from tensorflow.keras.optimizers.schedules import PiecewiseConstantDecay

from nemo.dnn.dataset import train_div2k_dataset, test_div2k_dataset, sample_and_save_images
import nemo.dnn.model
from nemo.dnn.trainer import NEMOTrainer
from nemo.tool.video import profile_video

if __name__ == '__main__':
    tf.enable_eager_execution()

    parser = argparse.ArgumentParser()

    #dataset
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--scale', type=int, required=True)

    #training & testing
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--patch_size', type=int, default=64)
    parser.add_argument('--num_epochs', type=int, default=300)
    parser.add_argument('--num_steps_per_epoch', type=int, default=1000)
    parser.add_argument('--load_on_memory', action='store_true')
    parser.add_argument('--num_samples', type=int, default=10)

    #dnn
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int, required=True)
    parser.add_argument('--num_blocks', type=int, required=True)
    parser.add_argument('--upsample_type', type=str, default='deconv')

    #tool
    parser.add_argument('--ffmpeg_path', type=str, default='/usr/bin/ffmpeg')

    args = parser.parse_args()

    lr_image_dir = os.path.join(args.data_dir, 'DIV2K_train_LR_bicubic', 'X{}'.format(args.scale))
    hr_image_dir = os.path.join(args.data_dir, 'DIV2K_train_HR')

    train_ds = train_div2k_dataset(lr_image_dir, hr_image_dir, args.scale, args.batch_size, args.patch_size, args.load_on_memory)
    test_ds = test_div2k_dataset(lr_image_dir, hr_image_dir, args.scale, args.num_samples, args.load_on_memory)

    """
    check patches are generated correctly
    for idx, imgs in enumerate(train_ds.take(3)):
        lr_img = tf.image.encode_png(tf.cast(tf.squeeze(imgs[0]), tf.uint8))
        hr_img = tf.image.encode_png(tf.cast(tf.squeeze(imgs[1]), tf.uint8))
        tf.io.write_file('train_lr_{}.png'.format(idx), lr_img)
        tf.io.write_file('train_hr_{}.png'.format(idx), hr_img)
    for idx, imgs in enumerate(test_ds.take(3)):
        lr_img = tf.image.encode_png(tf.cast(tf.squeeze(imgs[0]), tf.uint8))
        hr_img = tf.image.encode_png(tf.cast(tf.squeeze(imgs[1]), tf.uint8))
        tf.io.write_file('test_lr_{}.png'.format(idx), lr_img)
        tf.io.write_file('test_hr_{}.png'.format(idx), hr_img)
    """

    model = nemo.dnn.model.build(args.model_type, args.num_blocks, args.num_filters, args.scale, args.upsample_type)

    checkpoint_dir = os.path.join(args.data_dir, 'DIV2K', 'checkpoint', 'DIV2K_X{}'.format(args.scale), model.name)
    log_dir = os.path.join(args.data_dir, 'DIV2K', 'log', 'DIV2K_X{}'.format(args.scale),  model.name)
    NEMOTrainer(model, checkpoint_dir, log_dir).train(train_ds, test_ds, args.num_epochs, args.num_steps_per_epoch)
