from paranoid import *
from paranoid.testfunctions import test_function

def fails(f):
    failed = False
    try:
        f()
    except:
        failed = True
    if failed == False:
        raise ValueError("Error, function did not fail")

# Tests
@accepts(Number())
@returns(Number())
def add_three(n):
    return n+3

add_three(4)
add_three(-10)
fails(lambda : add_three("hello"))

@accepts(Number(), Number())
@returns(Number())
def add(n, m):
    return n+m

add(4, 5)

@accepts(Range(-1, 1))
@returns(Range(0, .9))
def square(n):
    return n*n

square(.3)
fails(lambda : square(.999))

@accepts(RangeClosedOpen(-1, 1))
@returns(Range(0, 1))
def square(n):
    return n*n

square(-1)
fails(lambda : square(1))

@accepts(RangeOpenClosed(-1, 1))
@returns(Range(0, 1))
def square(n):
    return n*n

square(1)
fails(lambda : square(-1))

@accepts(RangeOpen(-1, 1))
@returns(RangeOpen(0, 1))
def square(n):
    return n*n

square(.99999)
fails(lambda : square(1))

@accepts(List(Integer()))
@returns(Integer())
def sumlist(l):
    return sum(l)

sumlist([3, 6, 2, 1])

@accepts(Dict(String(), Number()))
@returns(Dict(String(), Number()))
def ident(d):
    return d

ident({"a" : 3, "b" : 901.90})
fails(lambda : ident({"a" : "a", "b" : 901.90, "c" : 22}))
fails(lambda : ident({"a" : 33, "b" : 901.90, 22 : 22}))

class MyType:
    def __init__(self, val):
        self.val = val
    @staticmethod
    def _generate():
        yield MyType(1)
        yield MyType("string")
    @staticmethod
    def _test(v):
        Integer().test(v.val)

@accepts(MyType)
@returns(MyType)
def myfun(mt):
    return MyType(3)

myfun(MyType(1))
fails(lambda : myfun("abc"))
fails(lambda : myfun(MyType("abc")))

@accepts(And(Natural0(), Range(low=4, high=7)))
@returns(Natural1())
def addthree(a):
    return a+3

addthree(4)
addthree(5)
fails(lambda : addthree(9))
fails(lambda : addthree(2))

@accepts(String)
@returns(Nothing)
def pass_it(s):
    pass

pass_it("ars")

@accepts(String)
@returns(Nothing)
def dont_pass_it(s):
    return False

fails(lambda : dont_pass_it("ars"))

@accepts(Number())
@returns(Number())
@ensures("n` <= n <--> return` <= return")
def monotonic(n):
    return n**3

monotonic(-3)
monotonic(-2)
monotonic(-1)

test_function(monotonic)

@accepts(Number(), Number())
@returns(Number())
@ensures("return == n + m")
@ensures("return >= m + n")
@ensures("m > 0 and n > 0 --> return > 0")
@ensures("m` >= m and n` >= n --> return` >= return")
def add(n, m):
    return n+m

add(0, 5)
add(0, 6)
add(0, 3)
add(7, 3)

test_function(add)


@accepts(MyType)
@returns(Nothing)
@ensures("1==1")
@immutable_argument
def dontmod_mytype(mt):
    dummy = 3

dontmod_mytype(MyType(10))

@accepts(MyType)
@returns(Nothing)
@ensures("1==1")
@immutable_argument
def mod_mytype(mt):
    mt.val = 3



mod_mytype(MyType(3))
fails(lambda : mod_mytype(MyType(1)))

@accepts(Identifier, Alphanumeric, Latin)
def test_strings(s1, s2, s3):
    return True

test_strings("---", "tftf932", "tsrat")
fails(lambda : test_strings("---", "tftf932", "tsrat3"))
fails(lambda : test_strings("---", "tftf-932", "tsrat"))
fails(lambda : test_strings("x y", "tftf932", "tsrat"))