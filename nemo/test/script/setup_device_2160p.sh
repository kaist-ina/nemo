#!/bin/bash

function _usage()
{
cat << EOF
_usage: $(basename ${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}) [-c CONTENT] [-q QUALITY] [-r RESOLUTION] [-a ALGORITHM] [-d DEVICE_ID]
EOF
}

function _set_conda(){
    # >>> conda initialize >>>
    # !! Contents within this block are managed by 'conda init' !!
    __conda_setup="$('/opt/conda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
            . "/opt/conda/etc/profile.d/conda.sh"
        else
            export PATH="/opt/conda/bin:$PATH"
        fi
    fi
    unset __conda_setup
    # <<< conda initialize <<<
    conda deactivate
    conda activate nemo_py3.5
}

function _set_bitrate(){
    if [ "$1" == 240 ];then
        bitrate=512
    elif [ "$1" == 360 ];then
        bitrate=1024
    elif [ "$1" == 480 ];then
        bitrate=1600
    elif [ "$1" == 720 ];then
        bitrate=2640
    elif [ "$1" == 2160 ];then
        bitrate=12000
    fi
}

function _set_num_blocks(){
    num_blocks=8
}

function _set_num_filters(){
    num_filters=32
}

[[ ($# -ge 1)  ]] || { echo "[ERROR] Invalid number of arguments. See -h for help."; exit 1;  }

while getopts ":c:a:d:h" opt; do
    case $opt in
        h) _usage; exit 0;;
        a) algorithm="$OPTARG";;
        c) content=("$OPTARG");;
        d) device_id="$OPTARG";;
        \?) exit 1;
    esac
done


if [ -z "${content+x}" ]; then
    echo "[ERROR] content is not set"
    exit 1;
fi

if [ -z "${algorithm+x}" ]; then
    echo "[ERROR] algorithm is not set"
    exit 1;
fi

if [ -z "${device_id+x}" ]; then
    echo "[ERROR] device_id is not set"
    exit 1;
fi

resolution=2160
_set_conda
_set_bitrate ${resolution}
_set_num_blocks ${resolution}
_set_num_filters ${resolution}
CUDA_VISIBLE_DEVICES=${gpu_index} python ${NEMO_CODE_ROOT}/nemo/test/setup_device_2160p.py --data_dir ${NEMO_DATA_ROOT} --content ${content} --video_name ${resolution}p_${bitrate}kbps_s0_d300.webm --lib_dir ${NEMO_CODE_ROOT}/nemo/test/libs/arm64-v8a --num_blocks ${num_blocks} --num_filters ${num_filters} --algorithm=${algorithm} --device_id=${device_id} --output_width=3840 --output_height=2160
