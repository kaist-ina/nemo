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

LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
CONFIG_DIR := $(LOCAL_PATH)/libvpx_android_configs/$(TARGET_ARCH_ABI)
libvpx_source_dir := $(LOCAL_PATH)/libvpx

include $(CONFIG_DIR)/config.mk
include $(CONFIG_DIR)/libs-$(TOOLCHAIN).mk

ifeq ($(CONFIG_SNPE), yes)
#    SNPE_ROOT := $(LOCAL_PATH)/libvpx/third_party/snpe
	SNPE_ROOT := $(LOCAL_PATH)/../../../../../../../../third_party/snpe
    SNPE_INCLUDE_DIR:= $(SNPE_ROOT)/include/zdl
    ifeq ($(TARGET_ARCH_ABI), arm64-v8a)
        ifeq ($(APP_STL), c++_shared)
           SNPE_LIB_DIR := $(SNPE_ROOT)/lib/aarch64-android-clang6.0
        else
           $(error Unsupported APP_STL: '$(APP_STL)')
        endif
    else ifeq ($(TARGET_ARCH_ABI), armeabi-v7a)
        ifeq ($(APP_STL), c++_shared)
           SNPE_LIB_DIR := $(SNPE_ROOT)/lib/arm-android-clang6.0
        else
           $(error Unsupported APP_STL: '$(APP_STL)')
        endif
    else
        $(error Unsupported TARGET_ARCH_ABI: '$(TARGET_ARCH_ABI)')
    endif
endif

LOCAL_MODULE := libvpx
LOCAL_MODULE_CLASS := STATIC_LIBRARIES
LOCAL_CFLAGS := -DHAVE_CONFIG_H=vpx_config.h
LOCAL_ARM_MODE := arm
LOCAL_CFLAGS += -O3
LOCAL_CPP_EXTENSION := .cpp .cc

# config specific include should go first to pick up the config specific rtcd.
LOCAL_C_INCLUDES := $(CONFIG_DIR) $(libvpx_source_dir) $(LOCAL_PATH)/libvpx/third_party/libyuv/include/

# generate source file list
libvpx_codec_srcs := $(sort $(shell cat $(CONFIG_DIR)/libvpx_srcs.txt))
LOCAL_SRC_FILES := libvpx_android_configs/$(TARGET_ARCH_ABI)/vpx_config.c
LOCAL_SRC_FILES += $(addprefix libvpx/, $(filter-out vpx_config.c, \
                     $(filter %.c, $(libvpx_codec_srcs))))
LOCAL_SRC_FILES += $(addprefix libvpx/, $(filter-out vpx_config.c, \
                     $(filter %.cc, $(libvpx_codec_srcs))))
LOCAL_SRC_FILES += $(addprefix libvpx/, $(filter-out vpx_config.c, \
                     $(filter %.cpp, $(libvpx_codec_srcs))))

# include assembly files if they exist
# "%.asm.[sS]" covers neon assembly and "%.asm" covers x86 assembly
LOCAL_SRC_FILES += $(addprefix libvpx/, \
                     $(filter %.asm.s %.asm.S %.asm, $(libvpx_codec_srcs)))

ifneq ($(findstring armeabi-v7a, $(TARGET_ARCH_ABI)),)
# append .neon to *_neon.c and *.[sS]
LOCAL_SRC_FILES := $(subst _neon.c,_neon.c.neon,$(LOCAL_SRC_FILES))
LOCAL_SRC_FILES := $(subst .s,.s.neon,$(LOCAL_SRC_FILES))
LOCAL_SRC_FILES := $(subst .S,.S.neon,$(LOCAL_SRC_FILES))
endif

LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/libvpx \
                           $(LOCAL_PATH)/libvpx/vpx
LOCAL_LDFLAGS := -Wl,--version-script=$(CONFIG_DIR)/libvpx.ver
LOCAL_LDLIBS := -llog -lz -lm -landroid

#include SNPE as shared library
ifeq ($(CONFIG_SNPE), yes)
    LOCAL_CPP_FEATURES += exceptions
	LOCAL_SHARED_LIBRARIES := libSNPE 
	LOCAL_LDLIBS += -lGLESv2 -lEGL
#    LOCAL_C_INCLUDES += $(LOCAL_PATH)/libvpx/third_party/snpe/include
	LOCAL_C_INCLUDES += $(SNPE_ROOT)/include
endif
include $(BUILD_SHARED_LIBRARY)

#include prebuilt SNPE library
ifeq ($(CONFIG_SNPE), yes)
    include $(CLEAR_VARS)
    LOCAL_MODULE := libSNPE
    LOCAL_SRC_FILES := $(SNPE_LIB_DIR)/libSNPE.so
#    LOCAL_EXPORT_C_INCLUDES += $(LOCAL_PATH)/libvpx/third_party/snpe/include/zdl
	LOCAL_EXPORT_C_INCLUDES += $(SNPE_ROOT)/include/zdl
    include $(PREBUILT_SHARED_LIBRARY)
endif
