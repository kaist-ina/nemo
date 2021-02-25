import shlex
import subprocess
import json
import os

def profile_video(video_path):
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
