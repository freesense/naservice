#! /usr/bin/env python3

from inspect import getmembers
from basic import yaml_to_obj
from datetime import datetime
import exifread, re, os, os.path, shutil, time, hashlib, traceback

# 是否为测试，测试时不会真正创建目录、拷贝和删除文件
test = False

class parseTime:
    def __init__(self):
        self.p = [
            [re.compile(r'(\d{4}):(\d{2}):(\d{2})\s+(\d{2}):(\d{2}):(\d{2})'), self.on_regex],
            [re.compile(r'(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})'), self.on_regex],
            [re.compile(r'(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})'), self.on_regex],
            [re.compile(r'_(\d{4})_(\d{2})_(\d{2})_(\d{9})'), self.on_regex3],
            [re.compile(r'(19\d{6}\d{6})'), self.on_regex1],
            [re.compile(r'(20\d{6}\d{6})'), self.on_regex1],
            [re.compile(r'(19\d{6})_(\d{6})'), self.on_regex2],
            [re.compile(r'(20\d{6})_(\d{6})'), self.on_regex2],
            [re.compile(r'mmexport(\d{13})'), self.on_timestamp1],
            [re.compile(r'notepad(\d{13})'), self.on_timestamp1],
            [re.compile(r'wx_camera_(\d{13})'), self.on_timestamp1],
            [re.compile(r'_(\d{13})'), self.on_timestamp1],
            [re.compile(r'^(\d{13})$'), self.on_timestamp1],
        ]

    def _check(self, *d):
        y = int(d[0])
        m = int(d[1])
        day = int(d[2])
        h = int(d[3])
        minute = int(d[4])
        s = int(d[5])
        if y<1980 or y>2050 or m<=0 or m>12 or day<=0 or day>31 or h<0 or h>23 or minute<0 or minute>59 or s<0 or s>59:
            return None
        return [f'{int(x):02d}' for x in d]

    def on_timestamp1(self, g):
        d = datetime.fromtimestamp(int(g.group(1))/1000)
        return self._check(d.year, d.month, d.day, d.hour, d.minute, d.second)

    def on_regex(self, g):
        return self._check(g.group(1), g.group(2), g.group(3), g.group(4), g.group(5), g.group(6))

    def on_regex1(self, g):
        dt = g.group(1)
        return self._check(dt[:4], dt[4:6], dt[6:8], dt[8:10], dt[10:12], dt[12:])

    def on_regex2(self, g):
        d = g.group(1)
        t = g.group(2)
        return self._check(d[:4], d[4:6], d[6:], t[:2], t[2:4], t[4:])

    def on_regex3(self, g):
        tm = g.group(4)
        return self._check(g.group(1), g.group(2), g.group(3), tm[:2], tm[2:4], tm[4:6])

    def run(self, fpath):
        dt = None
        with open(fpath, 'rb') as f:
            tags = exifread.process_file(f)
            dt = tags.get('EXIF DateTimeOriginal')
            if dt is None:
                dt = tags.get('EXIF DateTimeDigitized')
                if dt is None:
                    dt = tags.get('Image DateTime')
        dt = os.path.basename(fpath).split('.')[0] if dt is None else str(dt)
        for p, func in self.p:
            x = re.search(p, dt)
            if x is None:
                continue
            g = func(x)
            if g is not None:
                return g

class PhotoMoveHandler:
    def __init__(self, mycfg):
        self.cfg = mycfg
        self.fname_pattern = re.compile(r'(.*)\((\d+)\)\.(.*)$')
        self.on_startup()

    def on_startup(self):
        for root, dirs, files in os.walk(self.cfg.path):
            for name in [x for x in files if not x.startswith('.')]:
                self.md5_source = None
                self.target = None
                self.on_file(os.path.join(root, name))

    def on_file(self, path):
        print('>>>', path)
        try:
            dt = parser.run(path)
        except:
            print(traceback.format_exc())
            return
        print('DATE:', dt)

        def newtarget():
            basename = os.path.basename(self.target)
            newfname = re.search(self.fname_pattern, basename)
            if newfname is None:
                l = basename.split('.')
                self.target = os.path.join(os.path.dirname(self.target), f'{".".join(l[:-1])}(1).{l[-1]}')
            else:
                self.target = f'{newfname[1]}({int(newfname[2])+1}).{newfname[3]}'

        def check():
            if os.path.exists(self.target):
                if os.stat(path).st_size == os.stat(self.target).st_size:
                    if self.md5_source is None:
                        with open(path, 'rb') as f:
                            self.md5_source = hashlib.md5(f.read()).hexdigest()
                    with open(self.target, 'rb') as f:
                        md5_target = hashlib.md5(f.read()).hexdigest()
                    if self.md5_source == md5_target:
                        print(f'目标文件 {self.target} 存在且完全一致，删除源文件')
                        if not test:
                            os.remove(path)
                        return False
                newtarget()
                return check()
            return True

        if dt is not None:
            fpath = os.path.join(self.cfg.target, *dt[:2])
            if not test:
                os.makedirs(fpath, 0o755, True)
            self.target = os.path.join(fpath, os.path.basename(path))
            if check():
                print(f'{path} -> {self.target}')
                if not test:
                    shutil.copy(path, self.target)
                if self.cfg.remove_after_operation:
                    print(f'rm {path}')
                    if not test:
                        os.remove(path)

if __name__ == '__main__':
    print('>>>', f"{'测试模式，不会真正创建目录、拷贝和删除文件' if test else '真实模式'}")
    cfg = yaml_to_obj(os.path.dirname(os.path.abspath(__file__)), 'fsyncd.yaml')
    parser = parseTime()
    for obj in [obj for name, obj in getmembers(cfg) if not name.startswith('__')]:
        if obj.mode == 'photo_move':
            handler = PhotoMoveHandler(obj)

