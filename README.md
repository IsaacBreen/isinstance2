# isinstance2

`isinstance2` is a module that provides a powerful runtime type checker for Python's built-in generic classes and
generic type hints. It allows you to perform runtime instance type checks on objects that are instances of a generic
class, as well as subclass checks on generic classes, even if you don't know the exact type of the generic parameters.

## Features

- Perform runtime instance and subclass checks on generic classes
- Supports built-in generic classes such as `list`, `tuple`, `dict`, `set`, and `frozenset`, as well as `Optional`
  and `Literal`.
- Check if an object is an instance of a `tuple` with variadic arguments.
- Register custom class or function with `isinstance2`'s instance checker registry.

## Installation

```sh
pip install isinstance2
```

## Basic Usage

### Instance Checks

```python
from typing import Iterable, Literal
from isinstance2 import isinstance2

# Basic instance checks
assert isinstance2([1, 2, 3], list[int])
assert isinstance2((1, 2.0, 'three'), tuple[int, float, str])
assert isinstance2({1, 2, 3}, set[int])
assert isinstance2({"foo": 1, "bar": 2}, dict[str, int])
assert isinstance2(frozenset([1, 2, 'Hi! 😊', 'literally amazing']), frozenset[int | Literal['Hi! 😊', 'literally amazing']])

# Ellipses in tuples work
assert isinstance2((1, 'two', 3.0, 'four'), tuple[int | float | str, ...])

# You can also check against abstract generic classes
assert isinstance2(range(10), Iterable[int])
assert not isinstance2(range(10), Iterable[float])
```

### Subclass Checks

```python
from typing import Collection, Iterable
from isinstance2 import issubclass2

# Basic subclass checks
assert issubclass2(list[int], list[int | float])
assert issubclass2(tuple[int, float], tuple[int | float, ...])

# Classes without generic parameters are presumed to match
assert issubclass2(list, list[int])
assert issubclass2(list[int], list)

# Abstract generic classes
assert issubclass2(list[int], Iterable[int])
assert issubclass2(Collection[bool], Iterable[int])  # Yes, bool is a subclass of int
```

## Advanced Usage

To check if an object is an instance of a custom generic class, register it with `isinstance2`'s instance checker

```python
from typing import Generic, TypeVar, Any
from isinstance2 import isinstance2, register_instance_checker

T = TypeVar('T')


class MyClass(Generic[T]):
    ...


@register_instance_checker
def is_instance_of_my_class(obj: Any) -> bool:
    return isinstance(obj, MyClass)


assert isinstance2(MyClass(), MyClass)
```

If you'd prefer not to add your checkers globally, you can use `isinstance2`'s `register` instead and pass a custom registry (which is just a `dict`).

```python
from typing import Generic, TypeVar
from isinstance2 import register, instance_checker_registry
from functools import partial

# Copy the default registry
my_registry = instance_checker_registry.copy()

# Make a custom registration function
my_register = partial(register, registry=my_registry)
```

Now you can use `my_register` in place of `register_instance_checker`.

## Limitations

- Does not yet support
    - `TypeVar`
    - `Container`
    - And likely quite a few other generic classes that I've missed. Please open an issue if you find one.
- Subclass checks for custom classes (instance checks are supported)
  - Requires Python 3.11 or later

## License

`isinstance2` is released under the [MIT License](https://github.com/python-isinstance/isinstance2/blob/master/LICENSE).
