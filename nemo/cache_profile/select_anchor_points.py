import os
import sys
import argparse
import tensorflow as tf
from nemo.tool.video import get_video_profile
from nemo.dnn.utility import build_model
from anchor_point_selector import AnchorPointSelector

if __name__ == '__main__':

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

    #anchor point selector
    parser.add_argument('--quality_margin', type=float, default=0.5)
    parser.add_argument('--gop', type=int, default=120)
    parser.add_argument('--chunk_idx', type=str, default=None)
    parser.add_argument('--num_decoders', default=8, type=int)
    parser.add_argument('--algorithm', choices=['nemo','uniform', 'random'])

    args = parser.parse_args()

    if args.vpxdec_path is None:
        args.vpxdec_path = os.path.join(os.environ['NEMO_CODE_ROOT'], 'third_party', 'libvpx', 'bin', 'vpxdec_nemo_ver2_x86')
        print(args.vpxdec_path)
        assert(os.path.exists(args.vpxdec_path))

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

    #run aps
    print('content - {}, video - {}, dnn - {}'.format(args.content, args.lr_video_name, model.name))
    aps = AnchorPointSelector(ckpt.model, args.vpxdec_path, dataset_dir, args.lr_video_name, args.hr_video_name, args.gop, \
                              args.output_width, args.output_height, args.quality_margin, args.num_decoders)
    aps.select_anchor_point_set(args.algorithm, args.chunk_idx)
    if args.chunk_idx is None:
        aps.aggregate_per_chunk_results(args.algorithm)
