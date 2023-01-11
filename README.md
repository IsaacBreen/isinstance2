
# isinstance2

`isinstance2` is a module that provides a runtime type checker that is more powerful than the built-in `isinstance` function. It allows you to perform runtime type checks on objects that are instances of a generic class, but you don't know the exact type of the generic parameters. This is particularly useful when working with Python's built-in generic classes and generic type hints.

## Installation

To install `isinstance2`, you can use pip:

```
pip install isinstance2
```

## Usage

Here is an example of how to use `isinstance2`:

```python
from typing import List, Union
from isinstance2 import isinstance2

def foo(x: List[Union[int, str]]):
    if isinstance2(x, List[Union[int, str]]):
        print("x is a list of integers or strings")
    else:
        print("x is not a list of integers or strings")

foo([1, 2, 3])  # prints "x is a list of integers or strings"
foo(["a", "b", "c"])  # prints "x is a list