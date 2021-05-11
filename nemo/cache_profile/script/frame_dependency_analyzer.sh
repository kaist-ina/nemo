#!/bin/bash

function _usage()
{
cat << EOF
_usage: $(basename ${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}) [-c CONTENT] [-i INDEX] [-q QUALITIY] [-r RESOLUTION] [-a ALGORITHM] [-m DECODE_MODE]

mandatory arguments:
-c CONTENT                 Specifies content (e.g., product_review)
-i INDEX                   Specifies index (e.g., 0)
-r RESOLUTION              Specifies resolution (e.g., 240)
-m DECODE_MODE             Specifies decode_mode (e.g., decode)

optional multiple arguments:
-q QUALITIY                 Specifies quality (e.g., low)
-a ALGORITHM                Specifies algorithm (e.g., nemo)

EOF
}

function _set_conda(){
    source ~/anaconda3/etc/profile.d/conda.sh
    conda deactivate
    conda activate nemo_py3.6
}

function _set_bitrate(){
    if [ "$1" == 240 ];then
        bitrate=512
    elif [ "$1" == 360 ];then
        bitrate=1024
    elif [ "$1" == 480 ];then
        bitrate=1600
    fi
}

function _set_num_blocks(){
    if [ "$1" == 240 ];then
        if [ "$2" == "low" ];then
            num_blocks=4
        elif [ "$2" == "medium" ];then
            num_blocks=8
        elif [ "$2" == "high" ];then
            num_blocks=8
        fi
    elif [ "$1" == 360 ];then
        if [ "$2" == "low" ];then
            num_blocks=4
        elif [ "$2" == "medium" ];then
            num_blocks=4
        elif [ "$2" == "high" ];then
            num_blocks=4
        fi
    elif [ "$1" == 480 ];then
        if [ "$2" == "low" ];then
            num_blocks=4
        elif [ "$2" == "medium" ];then
            num_blocks=4
        elif [ "$2" == "high" ];then
            num_blocks=4
        fi
    fi
}

function _set_num_filters(){
    if [ "$1" == 240 ];then
        if [ "$2" == "low" ];then
            num_filters=9
        elif [ "$2" == "medium" ];then
            num_filters=21
        elif [ "$2" == "high" ];then
            num_filters=32
        fi
    elif [ "$1" == 360 ];then
        if [ "$2" == "low" ];then
            num_filters=8
        elif [ "$2" == "medium" ];then
            num_filters=18
        elif [ "$2" == "high" ];then
            num_filters=29
        fi
    elif [ "$1" == 480 ];then
        if [ "$2" == "low" ];then
            num_filters=4
        elif [ "$2" == "medium" ];then
            num_filters=9
        elif [ "$2" == "high" ];then
            num_filters=18
        fi
    fi
}

[[ ($# -ge 1)  ]] || { echo "[ERROR] Invalid number of arguments. See -h for help."; exit 1;  }

while getopts ":c:i:q:r:a:m:h" opt; do
    case $opt in
        h) _usage; exit 0;;
        a) algorithm="$OPTARG";;
        c) content="$OPTARG";;
        i) index="$OPTARG";;
        q) quality="$OPTARG";;
        m) decode_mode="$OPTARG";;
        r) resolution="$OPTARG";;
        \?) exit 1;
    esac
done

if [ -z "${content+x}" ]; then
    echo "[ERROR] content is not set"
    exit 1;
fi

if [ -z "${resolution+x}" ]; then
    echo "[ERROR] resolution is not set"
    exit 1;
fi

if [ -z "${index+x}" ]; then
    echo "[ERROR] index is not set"
    exit 1;
fi

if [ -z "${decode_mode+x}" ]; then
    echo "[ERROR] decode_mode is not set"
    exit 1;
fi

_set_conda
_set_bitrate ${resolution}
_set_num_blocks ${resolution} ${quality}
_set_num_filters ${resolution} ${quality}
python ${NEMO_ROOT}/cache_profile/frame_dependency_analyzer.py --data_dir ${NEMO_ROOT}/data --content ${content}${index} --video_name ${resolution}p_${bitrate}kbps_s0_d300.webm --num_blocks ${num_blocks} --num_filters ${num_filters} --algorithm=${algorithm} --decode_mode=${decode_mode}
