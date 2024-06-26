# compose-operator

This module allows adding function composition
with the `|` operator to any function, method,
class, or other callable.

[`compose`](https://pypi.org/project/compose)
is used for the function composition.
[`wrapt`](https://pypi.org/project/wrapt) is
used to add the operator as transparently and
unintrusively as possible. This ensures that:

1. The `|` composition operator does not interfere at
   runtime with any introspection, other operators, and
   (optionally) Python 3.10's `|` type union operator.

2. `|`-composed functions still work with signature
   introspection, method binding, pickling, and so on.


## Versioning

This library's version numbers follow the
[SemVer 2.0.0 specification](https://semver.org/spec/v2.0.0.html).


## Installation

```sh
pip install compose-operator
```


## Usage

### Basics

Import `composable`:

```python
>>> from compose_operator import composable

```

A simple inline composition:

```python
>>> stringify_as_integer = composable(int) | str
>>> stringify_as_integer(12.3)
'12'

```

Naturally, the result of `|` on a composable
function is also composable, so you can chain it:

```python
>>> (composable(int) | str | list)(12.3)
['1', '2']

```

You can also use `composable` as a decorator:

```python
>>> @composable
... def my_stringify(thing):
...     return f'hello {thing}'
... 
>>> stringify_as_integer = int | my_stringify
>>> stringify_as_integer(12.3)
'hello 12'

```

### `composable` is "sticky"

`composable` will stick to callable return
values, so it **works out-of-the-box with
currying**, partial application, and so on:

```python
>>> import functools
>>> import operator
>>> import toolz
>>> 
>>> partial = composable(functools.partial)
>>> add1 = partial(operator.add, 1)
>>> (add1 | str)(2)
'3'
>>> curry = composable(toolz.curry)
>>> add = curry(operator.add)
>>> (add(2) | float)(2)
4.0

```

`composable` also sticks to the results of
method binding, so if you make a composable
method, or assign a function composed with
the `|` operator as a method, it "just works":

```python
>>> class Adder:
...     def __init__(self, value):
...         self._value = value
... 
...     @composable
...     def add(self, thing):
...         return thing + self._value
... 
...     add_then_stringify = add | str
... 
>>> adder = Adder(42)
>>> (adder.add | str)(8)
'50'
>>> adder.add_then_stringify(9)
'51'

```

### Composable Classes

If you want to decorate a class so that the class
is composable, use `@composable_constructor` -
that way, normal class functionality such as `|`
for **type unions** still works:

```python
>>> from compose_operator import composable_constructor
>>> 
>>> from dataclasses import dataclass
>>> 
>>> @composable_constructor
... @dataclass
... class MyClass:
...     x: int
... 
>>> isinstance(1, int | MyClass)
True
>>> isinstance("hello!", int | MyClass)
False
>>> isinstance(MyClass(0), int | MyClass)
True
>>> (operator.add | MyClass)(3, 2)
MyClass(x=5)

```

`composable` takes precedence over
`composable_constructor`, so you can
still force `|` to do composition
instead of type union if you need to:

```python
>>> (composable(int) | MyClass)("6")
MyClass(x=6)
>>> (int | composable(MyClass))("7")
MyClass(x=7)

```

### Composable Callable Objects

If you are defining a class with a `__call__` method,
you can make its instances automatically `composable`
by using `composable_instances`:

```python
>>> from compose_operator import composable_instances
>>> 
>>> @composable_instances
... class Greeter:
...     def __init__(self, target):
...         self._target = target
...     def __call__(self):
...         return f"Hello, {self._target}!"
... 
>>> world_greeter = Greeter("world")
>>> world_greeter()
'Hello, world!'
>>> (world_greeter | list)()
['H', 'e', 'l', 'l', 'o', ',', ' ', 'w', 'o', 'r', 'l', 'd', '!']

```
