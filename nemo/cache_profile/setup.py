import os
import shutil
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--libvpx_dir', type=str, required=True)
    parser.add_argument('--binary_dir', type=str, required=True)
    args = parser.parse_args()

    # configure
    cmd = 'cd {} && ./nemo_server.sh'.format(args.libvpx_dir)
    os.system(cmd)

    # build
    cmd = 'cd {} && make'.format(args.libvpx_dir)
    os.system(cmd)
