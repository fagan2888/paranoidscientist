Paranoid Scientist
==================

## What is Paranoid Scientist?

Paranoid Scientist is a Python module which provides allows runtime
verification for Python programs.  More specifically, it provides the
following:

- A strong type system, which emphasizes the *meaning* of the type
  instead of the *data structure* of the type.
- Verification of arbitrary entry and exit conditions, including more
  complex expressions with universal quantification.
- Automated testing of individual functions to determine, before
  execution of the program, whether functions conform to their
  specification.
- A simple and clear function decorator notation

It shares inspiration (but is still quite distinct) from
contract-based programming, type classes, and automated fuzz testing,

## What is the point?

Paraoid Scientist is a tool to make sure scientific code is correct.
Traditional program verification asks the question, "If I run my code,
will it run correctly?"  It can be used to verify, for instance, that
a compiler will always produce the expected output.  In practice, it
can take a lot of time to verify programs and requires the use of
specific programming languages and constructs.

In scientific programming, verification is especially important
because we do not know the expected results of a computation, so it is
difficult to know whether any results are due to software bugs.  Thus,
with a slightly different goal, we can relax the question above and
instead ask, "If I ran my code, did it run correctly?"  In other
words, it is not as important to know before executing the program
whether it will run correctly, but if the program gives a result, we
want to know that this result is correct.

## Is Paranoid Scientist "Pythonic"?

Paranoid Scientist is Pythonic in most aspects, but not at all in the
type system.  Pythonic code relies on duck typing, which is great in
many situations but is a nightmare for scientific programming.  As an
example, consider the following:

```python
M = get_data_as_matrix()
M_squared = M**2
print(M_squared.tolist())
```

What is the result of this computation?  Duck typing tells us that we
have squared the matrix, and thus everything is okay.  However, if we
look more closely, the result depends on the matrix type returned by
`get_data_as_matrix`:

```python
M = numpy.matrix([[1, 2], [3, 4]])
M_squared = M**2
print(M_squared.tolist())

M = numpy.array([[1, 2], [3, 4]])
M_squared = M**2
print(M_squared.tolist())
```

which outputs

```
[[7, 10], [15, 22]]
[[1, 4], [9, 16]]
```

As we can see, the result of this computation depends on whether the
matrix is a numpy array or a numpy matrix, both of which are common
datatypes in practice.  The former implement element-wise
multiplication, while the latter implements matrix multiplication.
Forgetting to cast an array to a matrix (or vice versa) can introduce
subtle bugs into your code that could easily go undetected.

## System requirements

- Python 3.6 or above
- Optional: Numpy (for Numpy types support)

## Introduction to Types

The term "type" in Paranoid Scientist does not mean "type" in the same
sense that a programming language might use the word.  "Types" here do
not depend on the internal respresentation of variables, but rather,
on the way that they will be interpreted by humans.

As an example, suppose we want to implement a function which takes a
decimal number.  In a static-typed language, which uses
compiler/interpreter datatypes, this function would take a float as a
parameter.  However, it is not clear whether the function's behavior
is defined for NaN or Inf values.  While these are valid floats, they
are not valid decimal numbers.  Additionally, in a statically types
language, even though the function may also be valid for integers, the
code will require function polymorphism.  Thus, there is a disconnect
between what it means for a variable to be a "number"; a single
datatype is neither necessary nor sufficient to capture this concept.

By contrast, Paranoid Scientist considers "types" to be those which
are most useful in helping humans to reason about code.  For instance,
consider the following function:

```python
def add(n, m):
    """Compute n + m"""
    return n+m
```

This function works for any number, whether it is an integer or a
floating point, but it doesn't work for NaN or Inf.  So, we can
annotate the function as follows:

```python
@accepts(Number, Number)
@returns(Number)
def add(n, m):
    """Compute n + m"""
    return n+m
```

The "Number" type includes both floating points and integers, but
excludes NaN and Inf.

Similarly, we can use other human-undestandable types.  The following
function computes the expected number of "heads" in a biased coin,
when we flip a coin with a `p_heads` probability of showing heads
`flips` number of times.

```python
@accepts(Natural1, Range(0, 1))
@returns(Natural0)
def biased_coin(flips, p_heads):
    return round(flips * p_heads)
```

The `Natural1` type represents a natural number excluding zero, the
`Natural0` type is a natural number including zero, and `Range` is any
number within the range.

Additionally, the same syntax can be used in class methods, as long as
the class is flagged with the `@verifiedclass` decorator.  The special
type `Self` should be used for the `self` arguments in class methods.

``` python
@verifiedclass
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    @accepts(Self, Number, Number, Number, Number)
    @returns(Boolean)
    def is_in_box(self, xmin, xmax, ymin, ymax):
        if self.x > xmin and \
           self.x < xmax and \
           self.y > ymin and \
           self.y < ymax:
            return True
        return False
```

Currently, Paranoid Scientist does not operate on the `__init__`
method.  This is because, unlike all other methods in a class, the
`self` argument does not represent a fully instantiated class.  In
other words, the purpose of the `__init__` function is to help create
the `self` object, and therefore it does not make sense to test
whether the `self` object is valid, because clearly it is not.

## Creating types

It is relatively easy to create new types, and expected that you will
need to make several new types for each script you use with Paranoid
Scientist.

There are two ways to make new types.  They can either be created from
scratch, or an existing class can be converted into a type.

### Creating types from scratch

A type is a class which can be used to evaluate whether an arbitrary
value is a part of the type, and to generate new values of the type. 

The simplest types consist of two main components: 

- A function called `test` to test values to see if they are a part of
  the type.  This function should accept one argument (the value to be
  tested), and should use **assert statements only** to test whether
  the value is of the correct type.  The function should have only two
  behaviors: executing successfully retuning nothing (if the value is
  of the correct type), or throwing an assertion error (if the value
  is not of the correct type).
- A generator called `generate` to create test cases for the type.  It
  should use Python's yield statement for each test case.  It should
  not throw any errors.

All types should inherit from `paranoid.base.Type`.

Consider the following simple type:

```python
from paranoid.types.base import Type

class BinaryString(Type):
    """A binary number in the form of a string"""
    def test(self, v):
        """Test is `v` is a string of 0's and 1's."""
        # Use assert statements to verify the type
        assert set(v).difference({'0', '1'}) == set()
    def generate(self):
        """Generate some edge case binary strings"""
        yield "" # Empty list
        yield "0" # Just 0
        yield "1" # Just 1
        yield "01"*1000 # Long list
```

This works as expected

    >>> BinaryString().test("001")
    >>> "110101" in BinaryString()
    True
    >>> "012" in BinaryString()
    False
    >>> all([v in BinaryString() for v in BinaryString().generate()])
    True

Notice that in the constructor, we use the `in` syntax.  The syntax `x
in Natural0()` returns True if `Natural0().test(x)` does not raise an
exception.

A type may also contain arguments, in which case a constructor must
also be defined.  For instance, let's create a type for a binary
string of some particular length.  Since these must by definition also
be binary strings, we can inherit from the BinaryString type.

```python
from paranoid.types.numeric import Natural0

class FixedLengthBinaryString(BinaryString):
    """A binary number of specified length in the form of a string."""
    def __init__(self, length):
        super().__init__()
        assert length in Natural0() # Length must be a natural number
        self.length = length
    def test(self, v):
        """Test if `v` is a binary string of length `length`."""
        super().test(v) # Make sure it is a binary string
        assert len(v) == self.length # Make sure it is the right length
    def generate(self):
        """Generate binary strings of length `length`."""
        yield "0"*self.length # All 0's
        yield "1"*self.length # All 1's
        if self.length % 2 == 0:
            yield "01"*(self.length//2)
        else:
            yield "01"*(self.length//2) + "0"
```

Again, this works as we expect it to.

    >>> FixedLengthBinaryString(4).test("0010")
    >>> "001" in FixedLengthBinaryString(3)
    True
    >>> "001" in FixedLengthBinaryString(4)
    False
    >>> all([v in FixedLengthBinaryString(4) \
             for v in FixedLengthBinaryString(4).generate()])
    True

### Creating types from an existing class

Any normal Python class can be converted into a type.  In essence,
this allows the data within the class to be validated and tested.  Any
class can be turned into a type by adding two static methods:
`_test(v)`, and `_generate()`, which are analogous to the `test(self,
v)` and `generate(self)` functions described previously.

Let's look back at our example of the point in 2D space and turn this
into a type.

``` python
@verifiedclass
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    @accepts(Self, Number, Number, Number, Number)
    @returns(Boolean)
    def is_in_box(self, xmin, xmax, ymin, ymax):
        if self.x > xmin and \
           self.x < xmax and \
           self.y > ymin and \
           self.y < ymax:
            return True
        return False
    @staticmethod
    def _test(v):
        assert v.x in Number(), "Invalid X coordinate"
        assert v.y in Number(), "Invalid Y coordinate"
    @staticmethod
    def _generate():
        yield Point(0, 0)
        yield Point(1, 4/7)
        yield Point(-10, -1.99)
```

Types based on classes do not override the `in` syntax.

    >>> Point._test(Point(3, 4))
    >>> Point._test(Point(3, "4"))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 18, in _test
    AssertionError: Invalid Y coordinate
    >>> [Point._test(v) for v in Point._generate()]
    [None, None, None]

As you can see, the `_test(v)` function takes a single variable input,
and tests to see if it is a valid member of this class.  Valid
instances of this class should have `self.x` and `self.y` values which
are numbers.  It would not be valid to use a string for an x position.

Likewise, the `_generate()` function yields valid instances of this
class.

Unlike when we create types from scratch, we do **not** pass the
`self` argument to these functions because they are static methods.
This is because the type is defined based on the class, not based on
the instance of the class.

Using this syntax makes these types valid for all argument and return
types.  For example, we can define a function which takes Points as
arguments and returns a Point:

```python
@accepts(Point, Point)
@returns(Point)
def midpoint(p1, p2):
    xmid = p2.x + (p1.x - p2.x)/2
    ymid = p2.y + (p1.y - p2.y)/2
    return Point(xmid, ymid)
```

Running the standard tests on this, we see:

    >>> mp = midpoint(Point(0, 0), Point(1, 2))
    >>> mp.x, mp.y
    (0.5, 1.0)
    >>> midpoint(3, 5)
    Traceback (most recent call last):
      ...
    paranoid.exceptions.ArgumentTypeError: Invalid argument type: p1=3 is not of type Generic(<class '__main__.Point'>) in midpoint
    >>> [Point._test(midpoint(v1, v2)) \
           for v1 in Point._generate() for v2 in Point._generate()]
    [None, None, None, None, None, None, None, None, None]

## Automated testing

As you can see from many of the examples given here, it makes sense to
test functions by generating values to pass to the function using the
`accepts` type information, and checking that the return values fit
the `returns` type information.  Indeed, Paranoid Scientist will
automate this process.

Basic automatic unit-test--like functionality is available in Paranoid
Scientist.  To use this feature on a file "myfile.py", run the
following at the command line:

    $ python3 -m paranoid myfile.py

This will look through the file at each function containing "accepts"
annotations, and generate a number of test cases for each function to
ensure that the function doesn't fail, and ensure that it satisfies
the "returns"/"ensures" exit conditions.

This should **not** be used as a replacement for unit tests.

## Entry conditions

In addition to the `accepts` and `returns` conditions, we can also
specify more complex relationships among variables.  No type can
define interactions between multiple variables.  For this, we can use
the `requires` operator to specify entry conditions.  This takes a
string of valid Python describing the relationship between the
variables.

Consider for instance the following:

``` python
@accepts(Number, Number)
def invert_difference(x, y):
    return 1/(x-y)
```

As you can see, this function is not defined when x and y are equal to
each other.  There is no way to define types for x and y without
taking into account their values.  Instead, Paranoid Scientist allows
us to write:

``` python
@accepts(Number, Number)
@requires("x != y")
def invert_difference(x, y):
    return 1/(x-y)
```

It is also possible to use the `requires` decorator to simplify highly
redundant types.  For example, we could write:

``` python
@accepts(Number)
@requires("x != 0")
def invert(x):
    return 1/x
```

There is no type that means "all numbers except zero".  While it would
be possible to create such a type for the purposes of this function,
it would start to get messy very quickly to have distinct but nearly
identical types for each function. It is more practical in this
example to put a constraint on the function's domain using the
`requires` condition.

Automated tests will only test functions if their entry conditions are
satisfied.

## Exit conditions

In addition to entry conditions, it is also possible to specify exit
conditions in a similar manner.  Exit conditions are notated similarly
to entry conditions (i.e. Python code inside a string) using the
`ensures` decorator, and specify what must hold after the function
executes.  Exit conditions use the magic variable "return" to describe
how the arguments must relate to return values.  For example,

``` python
@accepts(List(Number))
@returns(Number)
@ensures('min(l) < return < max(l)')
def mean(l):
    return sum(l)/len(l)
```

    >>> mean([1, 3, 2, 4])
    2.5
    >>> mean([1, 1, 1, 1])
    Traceback (most recent call last):
        ...
    paranoid.exceptions.ExitConditionsError: Ensures statement 'min(l) < return < max(l)' failed in mean
    params: {'l': [1, 1, 1, 1], '__RETURN__': 1.0}

For convenience, exit conditions also allow two new pseudo-operators,
`-->` and `<-->`, which mean "if" and "if and only if" respectively.
For example,

``` python
@accepts(Number)
@returns(Number)
@ensures('return == 0 <--> x == 0')
def quadratic(x):
    return x*x
```

Among the four types of conditions which can be imposed upon functions
(argument types, return types, entry conditions, and exit conditions),
exit conditions are unique in that they can also use *previous* values
from a function's execution to test more complex properties of the
function.

In order to use a previous value within exit conditions, add a
backtick after the variable name, e.g. `x` is the current value and
`x\`` is any previous value of x.  (The pneumonic for this is $$x$$
for the variable and $$x'$$ for previous values as might be written in
a universal quantifier, e.g. $$\forall x,x' \in S : \ldots$$.

Why is this useful?  Now, we can test complex properties like a
function's monotonicity:

``` python
@accepts(Number)
@returns(Number)
@ensures("x > x` --> return >= return`")
def monotonic(x):
    return x**3
```

## License

All code is available under the MIT license.  See LICENSE.txt for more
information.

## FAQs

### Is Paranoid Scientist only for scientific code?

Paranoid Scientist was created with scientific code in mind.
Therefore, design decisions have focused on the idea that incorrect
behavior is infinitely worse than exiting with a runtime error.  The
main implication for this is that there is no exception handling;
errors cause the program to crash.  It is not only unnecessary, but
also very undesirable, to handle errors automatically in scientific
code.  If they are handled incorrectly, the result of the program
could be incorrect. It is better to kill the program and let an expert
analyze and fix the problem.

There are many places where it is important to have correct code, and
Paranoid Scientist is only applicable to a small subset of them.  **Do
not** use it to steer a car, operate a laparoscope, or control a
nuclear reactor.  **Do** use it to increase your confidence that your
data analysis or computational model is not giving incorrect results
due to software bugs.

### So if I just want to reduce the number of bugs in my code, Paranoid Scientist is useless?

Paranoid Scientist may also be used as a development tool.  Keeping it
enabled at runtime probably not the best choice for user-facing
software, but it can still be useful to catch bugs early by, e.g.,
using it only as a contract-oriented programming library for Python.
However, there are better tools for this job.

Also, just to state this explicitly, do **not** use the
automatically-generated test cases as a replacement for unit tests.

### Is Paranoid Scientist fast?

No.  Depending on which options you enable, which features you use,
and how your code is written, your code will run 10%--1000% slower.
The biggest culprits for slow runtime in Paranoid Scientist are
verification conditions involving more than one variable
(e.g. `return\`\``), asserting arguments are immutable, and functions
with many arguments.

However, Paranoid Scientist can easily be enabled or disabled at
runtime with a single line of code.  When it is disabled, there is no
performance loss.  Additionally, the automated unit tests described
above may still be run when it is disabled at runtime.

### Why are Python lists and numpy 1D arrays different types?

These types behave differently in many common situation which can lead
to bugs.  For instance, consider the following function:

```python
def add_lists(a, b):
    return a + b
```

Does this concatenate the lists or does it perform element-wise
addition?  The answer depends on the datatype passed.

### Why are Numpy numbers different types than Python numbers?

As you may know, integers and floats in Python are different from
integers and floats in Numpy.  While both behave similarly in most
circumstances, Paranoid Scientist treats these as different types.

First, Numpy claims that their numeric type system is fully compatible
with Python's, however there are subtle differences, such as a failure
to pickle in some circumstances.

Second, and more importantly, incorporating Numpy features into a core
module for Paranoid Scientist would introduce an unnecessary
dependency on Numpy.
