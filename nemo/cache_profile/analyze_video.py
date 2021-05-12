import os
import argparse
import sys
from video_analyzer import VideoAnalyzer
from nemo.tool.video import get_video_profile
from nemo.dnn.utility import build_model
from nemo.tool.libvpx import offline_cache_metadata

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Frame Dependency Analyzer')

    #directory, path
    parser.add_argument('--vpxdec_path', type=str, default=None)
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--lr_video_name', type=str, required=True)
    parser.add_argument('--hr_video_name', type=str, required=True)

    #codec
    parser.add_argument('--output_width', type=int, required=True)
    parser.add_argument('--output_height', type=int, required=True)

    #dnn
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int, required=True)
    parser.add_argument('--num_blocks', type=int, required=True)
    parser.add_argument('--upsample_type', type=str, default='deconv')

    #anchor point selector
    parser.add_argument('--quality_margin', type=float, default=0.5)
    parser.add_argument('--algorithm', choices=['nemo','uniform', 'random'], required=True)

    args = parser.parse_args()

    if args.vpxdec_path is None:
        args.vpxdec_path = os.path.join(os.environ['NEMO_CODE_ROOT'], 'third_party', 'libvpx', 'bin', 'vpxdec_nemo_ver2_x86')
        assert(os.path.exists(args.vpxdec_path))

    # setup
    dataset_dir = os.path.join(args.data_dir, args.content)
    lr_video_path = os.path.join(dataset_dir, 'video', args.lr_video_name)
    hr_video_path = os.path.join(dataset_dir, 'video', args.hr_video_name)
    lr_video_profile = get_video_profile(lr_video_path)
    hr_video_profile = get_video_profile(hr_video_path)
    scale = args.output_height // lr_video_profile['height']
    model = build_model(args.model_type, args.num_blocks, args.num_filters, scale, args.upsample_type)

    # prepare metadata
    metadata_file = os.path.join(dataset_dir, 'log', args.lr_video_name, model.name, 'metadata.txt' )
    cache_profile_name = '{}_{}'.format(args.algorithm, args.quality_margin)
    if not os.path.exists(metadata_file):
        offline_cache_metadata(args.vpxdec_path, dataset_dir, args.lr_video_name, model.name, cache_profile_name, args.output_width, args.output_height)

    # run the video analyzer
    log_dir = os.path.join(args.data_dir, args.content, 'log', args.lr_video_name, model.name, '{}_{}'.format(args.algorithm, args.quality_margin))
    va = VideoAnalyzer(log_dir)
    va.all()
