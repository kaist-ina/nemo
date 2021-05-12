import os
import sys
import argparse
from shutil import copyfile

if os.path.exists('libvpx'):
    os.remove('libvpx')
    os.symlink('../../../third_party/libvpx', 'libvpx')
else:
    os.symlink('../../../third_party/libvpx', 'libvpx')
