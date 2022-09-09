#!/usr/bin/python3
# 修改媒体文件名，避免出现“20季21集”这种情况

import os, sys, re

def remove_year(x, fname):
    newfname, _ = re.subn(r'\.19\d{2}\.|\.20\d{2}\.', '.', fname)
    if newfname != fname:
        fpath = os.path.join(x, newfname)
        os.rename(os.path.join(x, fname), fpath)

if __name__ == '__main__':
    for root, dirs, files in os.walk(sys.argv[-1]):
        for name in files:
            remove_year(root, name)
