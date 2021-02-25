#!/bin/bash

function _usage()
{
cat << EOF
_usage: $(basename ${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}) [-c CONTENTS]

mandatory arguments:
-c CONTENTS                 Specifies contents (e.g., product_review)

EOF
}

function _transcode()
{
    #cut and encode (2160p)
    python $NEMO_CODE_ROOT/nemo/tool/encode_video.py --output_video_dir $NEMO_DATA_ROOT/$1/video --input_video_path $NEMO_DATA_ROOT/video/$1.webm --start 0 --duration 300 --bitrate 12000 --mode cut_and_resize_and_encode --output_width 3840 --output_height 2160

    #encode (240p)
    python $NEMO_CODE_ROOT/nemo/tool/encode_video.py --output_video_dir $NEMO_DATA_ROOT/$1/video --input_video_path $NEMO_DATA_ROOT/$1/video/2160p_12000kbps_s0_d300.webm --bitrate 512 --output_width 426 --output_height 240 --start 0 --duration 300 --mode resize_and_encode

    #encode (360p)
    python $NEMO_CODE_ROOT/nemo/tool/encode_video.py --output_video_dir $NEMO_DATA_ROOT/$1/video --input_video_path $NEMO_DATA_ROOT/$1/video/2160p_12000kbps_s0_d300.webm --bitrate 1024 --output_width 640 --output_height 360 --start 0 --duration 300 --mode resize_and_encode

    #encode (480p)
    python $NEMO_CODE_ROOT/nemo/tool/encode_video.py --output_video_dir $NEMO_DATA_ROOT/$1/video --input_video_path $NEMO_DATA_ROOT/$1/video/2160p_12000kbps_s0_d300.webm --bitrate 1600 --output_width 854 --output_height 480 --start 0 --duration 300 --mode resize_and_encode

    #encode (720p)
    python $NEMO_CODE_ROOT/nemo/tool/encode_video.py --output_video_dir $NEMO_DATA_ROOT/$1/video --input_video_path $NEMO_DATA_ROOT/$1/video/2160p_12000kbps_s0_d300.webm --bitrate 2640 --output_width 1280 --output_height 720 --start 0 --duration 300 --mode resize_and_encode

    #encode (1080p)
    python $NEMO_CODE_ROOT/nemo/tool/encode_video.py --output_video_dir $NEMO_DATA_ROOT/$1/video --input_video_path $NEMO_DATA_ROOT/$1/video/2160p_12000kbps_s0_d300.webm --bitrate 4400 --output_width 1920 --output_height 1080 --start 0 --duration 300 --mode resize_and_encode
}

[[ ($# -ge 1)  ]] || { echo "[ERROR] Invalid number of arguments. See -h for help."; exit 1;  }

while getopts "c:h" opt; do
    case $opt in
        h) _usage; exit 0;;
        c) contents+=("$OPTARG");;
        \?) exit 1;
    esac
done

if [ -z "${contents}" ] ; then
    echo "[ERROR] contents is not set"
    exit 1;
fi

for content in "${contents[@]}"; do
    _transcode $content
done
