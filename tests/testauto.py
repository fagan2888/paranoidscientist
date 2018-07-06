from paranoid import *
from paranoid.testfunctions import test_function

@accepts(Number())
@returns(Number())
def add_three(n):
    return n+3

@accepts(Integer(), Integer())
@returns(Integer())
def add(n, m):
    return n+m

@accepts(Number(), Number())
@requires("n >= m")
@returns(Number())
@ensures("return >= 0")
def subtract(n, m):
    return n - m

@accepts(Range(-1, 1))
@returns(Range(0, 1))
def square(n):
    return n*n

@accepts(RangeClosedOpen(-1, 1))
@returns(Range(0, 1))
def square(n):
    return n*n

@accepts(RangeOpenClosed(-1, 1))
@returns(Range(0, 1))
def square2(n):
    return n*n

@accepts(RangeOpen(-1, 1))
@returns(RangeClosedOpen(0, 1))
def square3(n):
    return n*n

@accepts(List(Integer()))
@returns(Integer())
def sumlist(l):
    return sum(l)

@accepts(Dict(String(), Number()))
@returns(Dict(String(), Number()))
def ident(d):
    return d

class MyType:
    def __init__(self, val):
        self.val = val
    @staticmethod
    def _generate():
        vals = ["string", 3, 11]
        return [MyType(v) for v in vals]

@accepts(MyType)
@returns(MyType)
def myfun(mt):
    return MyType(3)

@accepts(And(Natural0(), Or(Range(low=4, high=7), Range(low=12, high=15))))
@returns(Natural1())
def addthree(a):
    return a+3

@accepts(String)
@returns(Nothing)
def pass_it(s):
    pass

@accepts(Number())
@returns(Number())
@ensures("n` <= n <--> return` <= return")
def monotonic(n):
    return n**3

@accepts(Number(), Number())
@returns(Number())
@ensures("return == n + m")
@ensures("return >= m + n")
@ensures("m > 0 and n > 0 --> return > 0")
@ensures("m` >= m and n` >= n --> return` >= return")
def add(n, m):
    return n+m

@paranoidclass
class MyClass:
    def __init__(self, val, **kwargs):
        self.val = val
        self.extraargs = kwargs
    @staticmethod
    def _test(v):
        Number().test(v.val)
        Dict(String(), String()).test(v.extraargs)
    @staticmethod
    def _generate():
        vals = [3, 11, -3.1]
        return [MyClass(v, extraarg='ata') for v in vals]
    @accepts(Self, Number)
    def testfun(self, x):
        return self.val + x
    @accepts(Self, Number)
    @returns(Number)
    def testfun2(self, x, **kwargs):
        return self.val + x

import time

@accepts(Number)
@returns(Number)
@paranoidconfig(max_runtime=.1)
def long_running(a):
    time.sleep(5)
    return a
