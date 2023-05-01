#! /usr/bin/env python3

import os, random, signal, threading, time, yaml, inspect, json, logging
from timeit import default_timer


class mytimerit:
    def __init__(self):
        self._stats = {}
        self._now = default_timer()

    def timer(self, tag=None):
        current = default_timer()
        elapse = current - self._now
        if tag is not None:
            obj = self._stats.get(tag)
            if obj is None:
                self._stats[tag] = [elapse, 1]
            else:
                obj[0] += elapse
                obj[1] += 1
        self._now = default_timer()
        return elapse

    def avg(self, tag=None):
        if tag is not None:
            x = self._stats.get(tag)
            if x is None:
                return None
            return x[0]/x[1]
        else:
            r = {}
            for k, v in self._stats.items():
                r[k] = (v[1], v[0]/v[1])
            return r


def functimer(level, fmt):
    def _outer_func_(func):
        def __wrapper_func__(*args, **kwargs):
            begin = default_timer()
            result = func(*args, **kwargs)
            logging.log(level, fmt.format(default_timer() - begin))
            return result
        return __wrapper_func__
    return _outer_func_


class MyException(Exception):
    def __init__(self, errmsg, errcode=None) -> None:
        super().__init__()
        self.errmsg, self.errcode = errmsg, errcode

    def __str__(self) -> str:
        if self.errcode is None:
            return self.errmsg
        return f'{self.errcode}: {self.errmsg}'

    def __repr__(self) -> str:
        if self.errcode is None:
            return self.errmsg
        return f'{self.errcode}: {self.errmsg}'


def check_return(func):
    def __wrapper_func__(*args, **kwargs):
        obj, ok = func(*args, **kwargs)
        if ok:
            return obj
        logging.warning(f"{func.__name__}, args: {args}, kwargs: {kwargs}, return: {obj}")
        raise MyException(obj)
    return __wrapper_func__


def setup_signal(func):
    signal.signal(signal.SIGINT, func)
    signal.signal(signal.SIGTERM, func)


def synchronized(func):
    func.__lock__ = threading.Lock()
    def synced_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)
    return synced_func


def singleton(cls):
    instances = {}
    @synchronized
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return get_instance


def dict_to_obj(TypeName, d, *exclude):
    top = type(TypeName, (object,), d)
    seqs = tuple, list, set, frozenset
    for i, j in d.items():
        if i in exclude:
            setattr(top, i, j)
            continue
        if not isinstance(i, str):
            i = str(i)
        if isinstance(j, dict):
            setattr(top, i, dict_to_obj(TypeName, j))
        elif isinstance(j, seqs):
            setattr(top, i, type(j)(dict_to_obj(TypeName, sj) if isinstance(sj, dict) else sj for sj in j))
        else:
            setattr(top, i, j)

    # 支持pickle,但是跨进程pickle不支持,因为跨进程后,utils.basic命名空间不存在type(top)
    setattr(inspect.getmodule(top), TypeName, top)

    # 提供一个成员函数__dumps__,实现json.dumps
    def jsonencode(encoder, obj):
        if isinstance(obj, type(top)):
            d = {}
            for k, v in obj.__dict__.items():
                if isinstance(k, str) and not k.startswith('__') and not inspect.ismethod(getattr(obj, k)):
                    d[k] = v
            return d
        return json.JSONEncoder.default(encoder, obj)
    jsontop = type(f'{TypeName}Encoder', (json.JSONEncoder,), {'default': jsonencode})
    setattr(inspect.getmodule(top), f'{TypeName}Encoder', jsontop)

    setattr(top, '__dumps__', classmethod(lambda x: json.dumps(x, cls=jsontop)))
    return top


def yaml_to_obj(path, fname='config.yml', typename='YamlConfig', exclude=()):
    cfgpath = os.path.join(path, fname)
    with open(cfgpath, 'rt', encoding='utf8') as f:
        config = yaml.safe_load(f.read())
        obj = dict_to_obj(typename, config, *exclude)
        return obj
    return None


def tsplit(ts):
    """ convert ts to (yyyymmdd, hhmm)
    """
    ts = time.localtime(ts)
    return time.strftime('%Y%m%d-%H%M').split('-')


def randstr(length):
    """
    return: 长度为length的字符串(首字符不为数字)
    """
    alls = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s = random.choice(alls)
    alls += '1234567890'
    for _ in range(length-1):
        s += random.choice(alls)
    return s


def lazy_import(dirname, fname=None, onmod=None):
    """
    延迟导入

    :param dirname: 模块目录相对路径,也支持xxx.yyy格式
    :param fname: 模块文件名称（不包括扩展名）
    :param onmod: mod扩展函数
    :return: 模块对象, 模块不存在则返回None
    """
    if fname is None:
        dirname, fname = dirname.split('.')
    name = f'{dirname}.{fname}'
    mod = __import__(name)
    if onmod is not None:
        onmod(mod)
    return getattr(mod, fname, None)


def get_runfunc(dirname, fname=None, funcname='run'):
    """ 从其他模块中动态加载attr
    dirname: 模块名称
    fname: 模块文件名
    funcname: 模块方法或属性名
    """
    mod = lazy_import(dirname, fname)
    if mod is not None:
        runfunc = getattr(mod, funcname, None)
        if runfunc is not None:
            return runfunc
    return None
