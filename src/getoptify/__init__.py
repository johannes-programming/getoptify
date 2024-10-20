import functools as _functools
import getopt as _getopt
import sys as _sys

import click as _click

__all__ = ["command", "decorator", "process"]


def _longopt(x, /):
    v = str(x)
    if v == "" or v.startswith("-"):
        raise ValueError("%r is not a valid longopt" % x)
    return v


def command(*_args, **_kwargs):
    return _functools.partial(decorator, *_args, **_kwargs)


def decorator(old, /, *_args, **_kwargs):
    @_functools.wraps(old)
    def new(args=None):
        args = process(args, *_args, **_kwargs)
        return old(args)

    return new


def process(args=None, shortopts="", longopts=[], allow_argv=True, gnu=True):
    if allow_argv and args is None:
        args = _sys.argv[1:]
    args = [str(x) for x in args]
    shortopts = str(shortopts)
    longopts = [_longopt(x) for x in longopts]
    if gnu:
        g = _getopt.gnu_getopt
    else:
        g = _getopt.getopt
    pairlist, poslist = g(args=args, shortopts=shortopts, longopts=longopts)
    ans = []
    for k, v in pairlist:
        if not k.startswith("--"):
            ans.append(k + v)
        elif v != "":
            ans.append(k + "=" + v)
        elif k[2:] in longopts:
            ans.append(k)
        else:
            ans.append(k + "=")
    ans.append("--")
    ans += poslist
    return ans
