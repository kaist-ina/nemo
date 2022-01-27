import os
import shutil
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--libvpx_dir', type=str, required=True)
    parser.add_argument('--snpe_dir', type=str, required=True)
    parser.add_argument('--jni_dir', type=str, required=True)
    parser.add_argument('--binary_dir', type=str, required=True)
    parser.add_argument('--ndk_dir', type=str, required=True)
    args = parser.parse_args()

    # libvpx link
    src = args.libvpx_dir
    dest = os.path.join(args.jni_dir, 'libvpx')
    if not os.path.exists(dest):
        cmd = 'ln -s {} {}'.format(src, dest)

    # snpe link
    src = args.snpe_dir
    dest = os.path.join(args.jni_dir, 'snpe')
    if not os.path.exists(dest):
        cmd = 'ln -s {} {}'.format(src, dest)
        os.system(cmd)

    # configure
    cmd = 'cd {} && make distclean'.format(args.libvpx_dir)
    os.system(cmd)
    cmd = 'cd {} && ./nemo_client_arm64.sh'.format(args.jni_dir)
    os.system(cmd)

    # build
    build_dir = os.path.join(args.jni_dir, '..')
    cmd = 'cd {} && ndk-build NDK_TOOLCHAIN_VERSION=clang APP_STL=c++_shared NDK_DEBUG=0'.format(build_dir)
    os.system(cmd)
