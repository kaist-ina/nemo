import os
import logging
import shutil
import sys
import argparse

def get_download_cmd(url):
    return cmd

def get_video_url(content):
    url = None
    if content == 'product_review': #keywork: product_review
        url = "https://www.youtube.com/watch?v=YhysZu9jOt0"
    elif content == 'how_to': #keyword: how-to
        url = "https://www.youtube.com/watch?v=2ecqslqwXLQ"
    elif content == 'vlogs':
        url = "https://www.youtube.com/watch?v=eCz-IixxR_k"
    elif content == 'skit':
        url = "https://www.youtube.com/watch?v=V0f3IXzc530"
    elif content == 'game_play': #keyword: gameplay
        url = "https://www.youtube.com/watch?v=_56DGiboFF8"
    elif content == 'haul':
        url = "https://www.youtube.com/watch?v=PMfGJGmokqE"
    elif content == 'challenge':
        url = "https://www.youtube.com/watch?v=ZCg9xHNPR3k"
    elif content == 'education': #keyword: education
        url = "https://www.youtube.com/watch?v=0eaf6bUMd4U"
    elif content == 'favorite':
        url = "https://www.youtube.com/watch?v=9ALj1JxO7e0"
    elif content == 'unboxing':
        url = "https://www.youtube.com/watch?v=l0DoQYGZt8M"
    return url

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
