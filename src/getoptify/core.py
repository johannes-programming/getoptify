import functools
import getopt
import sys
import types
from typing import *

__all__ = ["command", "decorator", "process"]


def command(*_args: Any, **_kwargs: Any) -> functools.partial:
    "This function returns a decorator with set arguments."
    return functools.partial(decorator, *_args, **_kwargs)


def decorator(old: Callable, /, *_args: Any, **_kwargs: Any) -> types.FunctionType:
    "This decorator is the precursor of commands."

    @functools.wraps(old)
    def new(args: Any = None):
        args = process(args, *_args, **_kwargs)
        return old(args)

    return new


def process(
    args: Optional[Iterable] = None,
    shortopts: Any = "",
    longopts: Iterable = [],
    allow_argv: Any = True,
    gnu: Any = True,
) -> List[str]:
    "This function preparses args."
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
