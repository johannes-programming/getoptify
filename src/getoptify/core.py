import functools
import getopt
import sys

__all__ = ["command", "decorator", "process"]


def command(*_args, **_kwargs):
    return functools.partial(decorator, *_args, **_kwargs)


def decorator(old, /, *_args, **_kwargs):
    @functools.wraps(old)
    def new(args=None):
        args = process(args, *_args, **_kwargs)
        return old(args)

    return new


def process(args=None, shortopts="", longopts=[], allow_argv=True, gnu=True):
    if allow_argv and args is None:
        args = sys.argv[1:]
    args = [str(x) for x in args]
    shortopts = str(shortopts)
    longopts = [str(x) for x in longopts]
    if gnu:
        g = getopt.gnu_getopt
    else:
        g = getopt.getopt
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
