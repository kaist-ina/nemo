#!/bin/bash

function _usage()
{
cat << EOF
_usage: $(basename ${BASH_SOURCE[${#BASH_SOURCE[@]} - 1]}) [-g GPU_INDEX] [-q QUALITIES] [-r RESOLUTIONS]

mandatory arguments:
 -g GPU_INDEX               Specifies GPU index to use

optional multiple arguments:
-q QUALITIES                Specifies qualities (e.g., low)
-s SCALES                   Specifies scales (e.g., 4)

EOF
}

function _set_conda(){
    source ~/anaconda3/etc/profile.d/conda.sh
    conda deactivate
    conda activate nemo_py3.6
}

function _set_num_blocks(){
    if [ "$1" == 4 ];then
        if [ "$2" == "low" ];then
            num_blocks=4
        elif [ "$2" == "medium" ];then
            num_blocks=8
        elif [ "$2" == "high" ];then
            num_blocks=8
        fi
    elif [ "$1" == 3 ];then
        if [ "$2" == "low" ];then
            num_blocks=4
        elif [ "$2" == "medium" ];then
            num_blocks=4
        elif [ "$2" == "high" ];then
            num_blocks=4
        fi
    elif [ "$1" == 2 ];then
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
    if [ "$1" == 4 ];then
        if [ "$2" == "low" ];then
            num_filters=9
        elif [ "$2" == "medium" ];then
            num_filters=21
        elif [ "$2" == "high" ];then
            num_filters=32
        fi
    elif [ "$1" == 3 ];then
        if [ "$2" == "low" ];then
            num_filters=8
        elif [ "$2" == "medium" ];then
            num_filters=18
        elif [ "$2" == "high" ];then
            num_filters=29
        fi
    elif [ "$1" == 2 ];then
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

while getopts ":g:q:s:h" opt; do
    case $opt in
        h) _usage; exit 0;;
        g) gpu_index="$OPTARG";;
        q) qualities+=("$OPTARG");;
        s) scales+=("$OPTARG");;
        \?) exit 1;
    esac
done

if [ -z "${gpu_index+x}" ] ; then
    echo "[ERROR] gpu_index must be set"
    exit 1;
fi

if [ -z "${qualities+x}" ]; then
    qualities=("low" "medium" "high")
fi

if [ -z "${scales+x}" ]; then
    scales=("4" "3" "2")
fi

_set_conda

for quality in "${qualities[@]}"
do
    for scale in "${scales[@]}";
    do
        _set_num_blocks ${scale} ${quality}
        _set_num_filters ${scale} ${quality}
        CUDA_VISIBLE_DEVICES=${gpu_index} python ${NEMO_ROOT}/dnn/train_div2k.py --data_dir ${NEMO_ROOT}/data --num_blocks ${num_blocks} --num_filters ${num_filters} --load_on_memory --scale ${scale}
    done
done
