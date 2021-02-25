import os
import argparse
from nemo.tool.video import LibvpxEncoder, get_video_profile

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #path
    parser.add_argument('--ffmpeg_path', type=str, default='/usr/bin/ffmpeg')
    parser.add_argument('--input_video_path', type=str, required=True)
    parser.add_argument('--output_video_dir', type=str, required=True)

    #video
    parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--bitrate', type=int, default=None)
    parser.add_argument('--output_width', type=int, default=None)
    parser.add_argument('--output_height', type=int, default=None)
    parser.add_argument('--gop', type=int, default=120)
    parser.add_argument('--start', type=int, default=None)
    parser.add_argument('--duration', type=int, default=None)

    args = parser.parse_args()

    print(args.input_video_path)
    input_video_height = get_video_profile(args.input_video_path)['height']

    if args.mode == 'cut_and_resize_and_encode':
        assert(args.start is not None and args.duration is not None)
        enc = LibvpxEncoder(args.output_video_dir, args.input_video_path, input_video_height, args.start, args.duration, args.ffmpeg_path)
        enc.cut_and_resize_and_encode(args.output_width, args.output_height, args.bitrate, args.gop)
    elif args.mode == 'resize_and_encode':
        assert(args.bitrate is not None and args.output_height is not None and args.output_width is not None)
        enc = LibvpxEncoder(args.output_video_dir, args.input_video_path, input_video_height, args.start,
                            args.duration, args.ffmpeg_path)
        enc.resize_and_encode(args.output_width, args.output_height, args.bitrate, args.gop)
    else:
        raise ValueError('Unsupported mode')
