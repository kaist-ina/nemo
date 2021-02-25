import time
import argparse
import os

import tensorflow as tf

from nemo.dnn.utility import build_model
from nemo.tool.video import get_video_profile

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #directory, path
    parser.add_argument('--dataset_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--video_name', type=str, required=True)

    #architecture
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int, required=True)
    parser.add_argument('--num_blocks', type=int, required=True)
    parser.add_argument('--upsample_type', type=str, default='deconv')
    parser.add_argument('--scale', type=int, required=True)

    args = parser.parse_args()

    #scale, dnn
    video_path = os.path.join(args.dataset_dir, args.content, 'video', args.video_name)
    video_profile = get_video_profile(video_path)

    with tf.Graph().as_default(), tf.Session() as sess:
        init = tf.global_variables_initializer()
        sess.run(init)
        model = build_model(args.model_type, args.num_blocks, args.num_filters, args.scale, args.upsample_type)

        log_dir = os.path.join(args.dataset_dir, args.content, 'log', args.video_name,  model.name)
        os.makedirs(log_dir, exist_ok=True)
        summary_writer = tf.summary.FileWriter(log_dir, sess.graph)
