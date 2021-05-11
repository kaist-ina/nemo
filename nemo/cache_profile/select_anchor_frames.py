import argparse
import os
import math
from nemo.cache_profile.anchor_point_selector_nemo_bound import APS_NEMO
from nemo.model.nemo_s import NEMO_S

#TODO: make a shell file

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # params for directory, path
    parser.add_argument('--vpxdec_file', type=str, required=True)
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--lr_video_name', type=str, required=True)
    parser.add_argument('--hr_video_name', type=str, required=True)

    # params for a dnn
    parser.add_argument('--num_filters', type=int, required=True)
    parser.add_argument('--num_blocks', type=int, required=True)

    # params for a cache profile
    parser.add_argument('--threshold', type=float, default=None)
    parser.add_argument('--gop', type=int, required=True)
    parser.add_argument('--max_num_anchor_points', type=int, default=None)
    parser.add_argument('--chunk_idx', default=None, type=str)
    parser.add_argument('--num_decoders', default=16, type=int)
    parser.add_argument('--num_anchor_points', default=None, type=int)
    parser.add_argument('--num_iterations', default=None, type=int)
    parser.add_argument('--mode', required=True)
    parser.add_argument('--task', choices=['profile','summary'], required=True)
    parser.add_argument('--profile_all', action='store_true')

    args = parser.parse_args()
    args.dataset_dir = os.path.join(args.dataset_rootdir, args.content)

    # setup scale, nhwc
    lr_video_file = os.path.join(dataset_dir, 'video', args.lr_video_name)
    hr_video_file = os.path.join(dataset_dir, 'video', args.hr_video_name)
    lr_video_info = profile_video(lr_video_file)
    hr_video_info = profile_video(hr_video_file)
    scale = int(hr_video_info['height'] / lr_video_info['height'])
    nhwc = [1, lr_video_info['height'], lr_video_info['width'], 3]

    # setup the model
    checkpoint_dir = os.path.join(dataset_dir, 'checkpoint', args.lr_video_name, model.name)
    checkpoint = NEMO_S(args.num_blocks, args.num_filters, scale).load_checkpoint(checkpoint_dir)
    args.model = checkpoint.model

    #TODO: check
    sys.exit()

    # setup the anchor point selector
    aps = None
    if args.mode == 'nemo':
        aps = APS_NEMO(args)
    else:
        raise NotImplementedError

    #TODO: check
    sys.exit()

    # run the anchor point selector
    if args.task == 'profile': # generate a cache profile
        if args.chunk_idx is None:
            num_chunks = int(math.ceil(lr_video_info['duration'] / (args.gop / lr_video_info['frame_rate'])))
            for i in range(num_chunks):
                aps.run(i)
        else:
            if ',' in args.chunk_idx:
                start_index = int(args.chunk_idx.split(',')[0])
                end_index = int(args.chunk_idx.split(',')[1])
                for i in range(start_index, end_index + 1):
                    aps.run(i)
            else:
                aps.run(int(args.chunk_idx))
    elif args.task == 'summary': # merge a cache profile
        if args.chunk_idx is None:
            num_chunks = int(math.ceil(lr_video_info['duration'] / (args.gop / lr_video_info['frame_rate'])))
            aps.summary(0, num_chunks)
        else:
            if ',' in args.chunk_idx:
                start_index = int(args.chunk_idx.split(',')[0])
                end_index = int(args.chunk_idx.split(',')[1])
                aps.summary(start_index, end_index + 1)
            else:
                aps.summary(int(args.chunk_idx), int(args.chunk_idx) + 1)
    else:
        raise NotImplementedError
