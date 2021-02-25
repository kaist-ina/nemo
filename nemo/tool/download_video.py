import os
import argparse
from nemo.tool.video import get_video_url

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_dir', type=str, required=True)
    parser.add_argument('--youtubedl_path', type=str, default='/usr/local/bin/youtube-dl')
    parser.add_argument('--content', type=str, required=True)

    args = parser.parse_args()

    url = get_video_url(args.content)
    assert(url is not None)
    video_path= os.path.join(args.video_dir, '{}.webm'.format(args.content))
    cmd = "{} -f 'bestvideo[height=2160][fps=30][ext=webm]' -o {} {}".format(args.youtubedl_path, video_path, url)
    print(cmd)
    os.system(cmd)
