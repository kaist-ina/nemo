#!/bin/bash

function _usage()
{
cat << EOF
_usage: $(basename ${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}) [-g GPU_INDEX] [-c CONTENT] [-q QUALITY] [-i INPUT_RESOLUTION] [-o OUTPUT_RESOLUTION]
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
    fi
}

function _set_num_blocks(){
    num_blocks=8
}

function _set_num_filters(){
    num_filters=32
}

[[ ($# -ge 1)  ]] || { echo "[ERROR] Invalid number of arguments. See -h for help."; exit 1;  }

while getopts ":g:c:q:i:o:h" opt; do
    case $opt in
        h) _usage; exit 0;;
        g) gpu_index="$OPTARG";;
        c) content=("$OPTARG");;
        q) quality=("$OPTARG");;
        i) input_resolution=("$OPTARG");;
        o) output_resolution="$OPTARG";;
        \?) exit 1;
    esac
done

if [ -z "${gpu_index+x}" ]; then
    echo "[ERROR] gpu_index is not set"
    exit 1;
fi

if [ -z "${content+x}" ]; then
    echo "[ERROR] content is not set"
    exit 1;
fi

if [ -z "${quality+x}" ]; then
    echo "[ERROR] quality is not set"
    exit 1;
fi

if [ -z "${input_resolution}" ]; then
    echo "[ERROR] input_resolution is not set"
    exit 1;
fi

if [ -z "${output_resolution+x}" ]; then
    echo "[ERROR] output_resolution is not set"
    exit 1;
fi

_set_conda
_set_bitrate ${input_resolution}
_set_num_blocks ${input_resolution} ${quality}
_set_num_filters ${input_resolution} ${quality}
CUDA_VISIBLE_DEVICES=${gpu_index} python ${NEMO_CODE_ROOT}/nemo/dnn/convert_tf_to_snpe.py --data_dir ${NEMO_DATA_ROOT} --content ${content}${index} --lr_video_name ${input_resolution}p_${bitrate}kbps_s0_d300.webm  --num_blocks ${num_blocks} --num_filters ${num_filters} --output_height ${output_resolution} --train_type train_video
