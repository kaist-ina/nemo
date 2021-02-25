import os
import subprocess
import shlex
import json

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

def get_video_profile(video_path):
    assert(os.path.exists(video_path))

    cmd = "ffprobe -v quiet -print_format json -show_streams -show_entries format"
    args = shlex.split(cmd)
    args.append(video_path)

    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)

    #height, width
    height = ffprobeOutput['streams'][0]['height']
    width = ffprobeOutput['streams'][0]['width']
    duration = float(ffprobeOutput['format']['duration'])

    #fps
    fps_line = ffprobeOutput['streams'][0]['avg_frame_rate']
    frame_rate = float(fps_line.split('/')[0]) / float(fps_line.split('/')[1])

    result = {}
    result['height'] = height
    result['width'] = width
    result['frame_rate'] = frame_rate
    result['duration'] = duration

    return result

class LibvpxEncoder():
    def __init__(self, output_video_dir, input_video_path, input_height, start, duration, ffmpeg_path):
        self.output_video_dir = output_video_dir
        self.input_video_path = input_video_path
        self.input_height = input_height
        self.start = start
        self.duration = duration
        self.ffmpeg_path = ffmpeg_path

        if os.path.exists(self.ffmpeg_path) is None:
            raise ValueError('ffmpeg does not exist')
        if os.path.exists(self.input_video_path) is None:
            raise ValueError('Video does not exist')
        self._check_ffmpeg()
        os.makedirs(self.output_video_dir, exist_ok=True)

    def _check_ffmpeg(self):
        ffmpeg_cmd = []
        ffmpeg_cmd.append(self.ffmpeg_path)
        ffmpeg_cmd.append("-buildconf")
        result = subprocess.check_output(ffmpeg_cmd).decode('utf-8')
        configuration = result.split()
        map(lambda x: x.strip(), configuration)
        if "--enable-libvpx" not in configuration:
            raise ValueError('ffmpeg is not build correctly')

    def _threads(self, height):
        cmd = ''
        if height < 360:
            cmd += '-tile-columns 0 -threads 2'
        elif height >= 360 and height < 720:
            cmd += '-tile-columns 1 -threads 4'
        elif height >= 720 and height < 1440:
            cmd += '-tile-columns 2 -threads 8'
        elif height >= 1440:
            cmd += '-tile-columns 3 -threads 16'
        return cmd

    def _speed(self, height, pass_):
        cmd = ''
        if pass_ == 1:
            cmd += '-speed 4'
        elif pass_ == 2:
            if height < 720:
                cmd += '-speed 1'
            else:
                cmd += '-speed 2'
        return cmd

    def _name(self, start, duration):
        name = ''
        if start is not None:
            name += '_s{}'.format(start)
        if duration is not None:
            name += '_d{}'.format(duration)
        return name

    def cut_and_resize_and_encode(self, width, height, bitrate, gop):
        int_video_name = '{}p{}.webm'.format(self.input_height, self._name(self.start, self.duration))
        int_video_path = os.path.join(self.output_video_dir, int_video_name)
        cut_opt = '-ss {} -t {}'.format(self.start, self.duration)
        cmd = '{} -i {} -y -c:v libvpx-vp9 -c copy {} {} {}'.format(self.ffmpeg_path,
            self.input_video_path, self._threads(self.input_height), cut_opt, int_video_path)
        os.system(cmd)

        height = get_video_profile(int_video_path)['height']
        output_video_name = '{}p_{}kbps{}.webm'.format(height, bitrate, self._name(self.start, self.duration))
        output_video_path = os.path.join(self.output_video_dir, output_video_name)
        target_bitrate = '{}k'.format(bitrate)
        min_bitrate = '{}k'.format(int(bitrate * 0.5))
        max_bitrate = '{}k'.format(int(bitrate * 1.45))
        passlog_name = '{}_{}'.format(self.output_video_dir.split('/')[-2], output_video_name) #assume output videos are saved as ".../[content]/video/*.webm"

        base_cmd = '{} -i {} -c:v libvpx-vp9 -vf scale={}x{}:out_color_matrix=bt709 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range 1 \
                    -b:v {} -minrate {} -maxrate {} -keyint_min {} -g {} -quality good {} -passlogfile {} -y'.format(
                        self.ffmpeg_path, int_video_path, width, height, target_bitrate, min_bitrate, max_bitrate, gop, gop,
                        self._threads(height), passlog_name)

        cmd = '{} -pass 1 {} {} && {} -pass 2 {} {}'.format(base_cmd, self._speed(height, 1),
                            output_video_path, base_cmd, self._speed(height, 2), output_video_path)
        os.system(cmd)

        passlog_path = os.path.join('./', '{}-0.log'.format(passlog_name))

        if os.path.exists(passlog_path): os.remove(passlog_path)
        if os.path.exists(int_video_path): os.remove(int_video_path)

    def resize_and_encode(self, width, height, bitrate, gop):
        output_video_name = '{}p_{}kbps{}.webm'.format(height, bitrate, self._name(self.start, self.duration))
        output_video_path = os.path.join(self.output_video_dir, output_video_name)
        target_bitrate = '{}k'.format(bitrate)
        min_bitrate = '{}k'.format(int(bitrate * 0.5))
        max_bitrate = '{}k'.format(int(bitrate * 1.45))
        passlog_name = '{}_{}'.format(self.output_video_dir.split('/')[-2], output_video_name) #assume output videos are saved as ".../[content]/video/*.webm"

        base_cmd = '{} -i {} -c:v libvpx-vp9 -vf scale={}x{}:out_color_matrix=bt709 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range 1 \
                    -b:v {} -minrate {} -maxrate {} -keyint_min {} -g {} -quality good {} -passlogfile {} -y'.format(
                        self.ffmpeg_path, self.input_video_path, width, height, target_bitrate, min_bitrate, max_bitrate, gop, gop,
                        self._threads(height), passlog_name)

        cmd = '{} -pass 1 {} {} && {} -pass 2 {} {}'.format(base_cmd, self._speed(height, 1),
                            output_video_path, base_cmd, self._speed(height, 2), output_video_path)
        os.system(cmd)

        passlog_path = os.path.join('./', '{}-0.log'.format(passlog_name))
        os.remove(passlog_path)
