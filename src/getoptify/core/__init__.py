import dataclasses
import functools
import os
import sys
import types
import warnings
from typing import *

import click

from makefunc import makefunc

__all__ = ["Parser"]

NO_ARGUMENT = 0
REQUIRED_ARGUMENT = 1
OPTIONAL_ARGUMENT = 2


@dataclasses.dataclass(kw_only=True)
class Parser:
    optdict: Any = None
    prog: Any = None
    deabbreviate: Any = True
    permutate: Any = True
    posix: Any = "infer"

    def __post_init__(self):
        if self.optdict is None:
            self.optdict = dict()
        if self.prog is None:
            self.prog = os.path.basename(sys.argv[0])
        if self.posix == "infer":
            self.posix = os.environ.get("POSIXLY_CORRECT")

    @makefunc
    class clickBind:
        def __call__(_self, self, target: Any, reflect: Any):
            if isinstance(target, types.FunctionType):
                f = _self.f
            elif isinstance(target, types.MethodType):
                f = _self.m
            elif isinstance(target, type):
                f = _self.t
            else:
                f = _self.o
            return f(parser=self, target=target, reflect=reflect)

        def f(_self, parser, target, reflect):
            @functools.wraps(target)
            def ans(self, ctx, args):
                if reflect:
                    parser.clickReflect(self)
                return target(self, ctx, parser.parse_args(args))

            return ans

        def m(_self, target, **kwargs):
            func = _self.f(target=target.__func__, **kwargs)
            ans = types.MethodType(func, target.__self__)
            return ans

        def t(_self, target, **kwargs):
            target.parse_args = _self.f(target=target.parse_args, **kwargs)
            return target

        def o(_self, target, **kwargs):
            target.parse_args = _self.m(target=target.parse_args, **kwargs)
            return target

    def clickReflect(self, command: click.Command):
        optdict = dict()
        for p in command.params:
            if not isinstance(p, click.Option):
                continue
            if p.is_flag or p.nargs == 0:
                optn = 0
            elif p.nargs == 1:
                optn = 1
            else:
                optn = 2
            for o in p.opts:
                optdict[o] = optn
        self.optdict.clear()
        self.optdict.update(optdict)

    def copy(self):
        return dataclasses.replace(self)

    def parse_args(self, args: Optional[Iterable] = None) -> List[str]:
        if args is None:
            args = sys.argv[1:]
        return _Parsing(
            parser=self.copy(),
            args=list(args),
        ).ans

    def warn(self, message):
        warnings.warn("%s: %s" % (self.prog, message))

    def warnAboutUnrecognizedOption(self, option):
        self.warn("unrecognized option %r" % option)

    def warnAboutInvalidOption(self, option):
        self.warn("invalid option -- %r" % option)

    def warnAboutAmbigousOption(self, option, possibilities):
        msg = "option %r is ambiguous; possibilities:" % option
        for x in possibilities:
            msg += " %r" % x
        self.warn(msg)

    def warnAboutNotAllowedArgument(self, option):
        self.warn("option %r doesn't allow an argument" % option)

    def warnAboutRequiredArgument(self, option):
        self.warn("option requires an argument -- %r" % option)


@dataclasses.dataclass
class _Parsing:
    parser: Parser
    args: list[str]

    def __post_init__(self):
        self.ans = list()
        self.spec = list()
        optn = 0
        while self.args:
            optn = self.tick(optn)
        if optn == 1:
            self.parser.warnAboutRequiredArgument(self.ans[-1])
        self.ans += self.spec

    def possibilities(self, opt):
        if opt in self.parser.optdict.keys():
            return [opt]
        ans = list()
        for k in self.parser.optdict.keys():
            if k.startswith(opt):
                ans.append(k)
        return ans

    def tick(self, optn):
        arg = self.args.pop(0)
        if optn == "break":
            self.spec.append(arg)
            return "break"
        if optn == 1:
            self.ans.append(arg)
            return 0
        elif arg == "--":
            self.ans.append("--")
            return "break"
        elif arg.startswith("-") and arg != "-":

            if arg.startswith("--"):
                return self.tick_long(arg)
            else:
                return self.tick_short(arg)
        else:
            if self.parser.posix:
                self.spec.append(arg)
                return "break"
            elif self.parser.permutate:
                self.spec.append(arg)
                return 0
            else:
                self.ans.append(arg)
                return 0

    def tick_long(self, arg: str):
        try:
            i = arg.index("=")
        except ValueError:
            i = len(arg)
        opt = arg[:i]
        possibilities = self.specsibilities(opt)
        if len(possibilities) == 0:
            self.parser.warnAboutUnrecognizedOption(arg)
            self.ans.append(arg)
            return 0
        if len(possibilities) > 1:
            self.parser.warnAboutAmbigousOption(arg, possibilities)
            self.ans.append(arg)
            return 0
        opt = possibilities[0]
        if "=" in arg:
            if self.parser.optdict[opt] == 0:
                self.parser.warnAboutNotAllowedArgument(opt)
            self.ans.append(opt + arg[i:])
            return 0
        else:
            self.ans.append(opt)
            return self.parser.optdict[opt]

    def tick_short(self, arg: str):
        self.ans.append(arg)
        for i in range(1 - len(arg), 0):
            optn = self.parser.optdict.get("-" + arg[i])
            if optn is None:
                self.parser.warnAboutInvalidOption(arg[i])
                optn = 0
            if i != -1 and optn != 0:
                return 0
            if i == -1 and optn == 1:
                return 1
        return 0
