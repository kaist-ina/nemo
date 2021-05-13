#
# Copyright (C) 2016 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Copyright (C) 2016 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

WORKING_DIR := $(call my-dir)

# build libvpx.so
LOCAL_PATH := $(WORKING_DIR)
include $(LOCAL_PATH)/libvpx.mk

# build libwebm.so
LIBVPX_ROOT := $(WORKING_DIR)/libvpx
LOCAL_PATH := $(WORKING_DIR)
include $(LIBVPX_ROOT)/third_party/libwebm/Android.mk

# build libvpxJNI.so
LIBVPX_SRCS := libvpx/md5_utils.c \
                libvpx/args.c \
                libvpx/ivfdec.c \
                libvpx/tools_common.c \
                libvpx/y4menc.c \
                libvpx/webmdec.cc
LIBYUV_SRCS :=  libvpx/third_party/libyuv/source/convert_argb.cc \
                 libvpx/third_party/libyuv/source/convert_from_argb.cc \
                 libvpx/third_party/libyuv/source/convert_from.cc \
                 libvpx/third_party/libyuv/source/convert_to_argb.cc \
                 libvpx/third_party/libyuv/source/convert_to_i420.cc \
                 libvpx/third_party/libyuv/source/convert.cc \
                 libvpx/third_party/libyuv/source/cpu_id.cc \
                 libvpx/third_party/libyuv/source/planar_functions.cc \
                 libvpx/third_party/libyuv/source/row_any.cc \
                 libvpx/third_party/libyuv/source/rotate.cc \
                 libvpx/third_party/libyuv/source/rotate_any.cc \
                 libvpx/third_party/libyuv/source/rotate_argb.cc \
                 libvpx/third_party/libyuv/source/rotate_common.cc \
                 libvpx/third_party/libyuv/source/rotate_gcc.cc \
                 libvpx/third_party/libyuv/source/rotate_mips.cc \
                 libvpx/third_party/libyuv/source/rotate_neon.cc \
                 libvpx/third_party/libyuv/source/rotate_neon64.cc \
                 libvpx/third_party/libyuv/source/rotate_win.cc \
                 libvpx/third_party/libyuv/source/row_common.cc \
                 libvpx/third_party/libyuv/source/row_gcc.cc \
                 libvpx/third_party/libyuv/source/row_mips.cc \
                 libvpx/third_party/libyuv/source/row_neon.cc \
                 libvpx/third_party/libyuv/source/row_neon64.cc \
                 libvpx/third_party/libyuv/source/row_win.cc \
                 libvpx/third_party/libyuv/source/scale.cc \
                 libvpx/third_party/libyuv/source/scale_any.cc \
                 libvpx/third_party/libyuv/source/scale_common.cc \
                 libvpx/third_party/libyuv/source/scale_gcc.cc \
                 libvpx/third_party/libyuv/source/scale_mips.cc \
                 libvpx/third_party/libyuv/source/scale_neon.cc \
                 libvpx/third_party/libyuv/source/scale_neon64.cc \
                 libvpx/third_party/libyuv/source/scale_win.cc \
                 libvpx/third_party/libyuv/source/video_common.cc

include $(CLEAR_VARS)
LOCAL_PATH := $(WORKING_DIR)
#LOCAL_MODULE := libvpxtestJNI
LOCAL_MODULE := libvpxJNI
LOCAL_ARM_MODE := arm
LOCAL_CPP_EXTENSION := .cc .cpp
CONFIG_DIR := $(LOCAL_PATH)/libvpx_android_configs/$(TARGET_ARCH_ABI)
LOCAL_C_INCLUDES := $(CONFIG_DIR)
LOCAL_C_INCLUDES += $(LOCAL_PATH)/libvpx/third_party/libyuv/include/
#LOCAL_SRC_FILES := vpxdec_wrapper.cpp vpxdec_android.c
LOCAL_SRC_FILES := vpx_jni.cc
LOCAL_SRC_FILES += $(LIBVPX_SRCS)
LOCAL_SRC_FILES += $(LIBYUV_SRCS)
LOCAL_SRC_FILES += $(libvpx_test_codes)
LOCAL_LDLIBS := -llog -lz -lm -landroid
LOCAL_SHARED_LIBRARIES := libvpx
LOCAL_STATIC_LIBRARIES := cpufeatures libwebm
include $(BUILD_SHARED_LIBRARY)

$(call import-module,android/cpufeatures)