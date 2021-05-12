#!/bin/bash

python ${NEMO_CODE_ROOT}/nemo/test/setup_local.py --libvpx_dir ${NEMO_CODE_ROOT}/third_party/libvpx --binary_dir ${NEMO_CODE_ROOT}/nemo/cache_profile/bin --jni_dir ${NEMO_CODE_ROOT}/nemo/test/jni --ndk_dir /android-ndk-r14b --snpe_dir ${NEMO_CODE_ROOT}/third_party/snpe
