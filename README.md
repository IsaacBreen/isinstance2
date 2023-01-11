# Subscripted Generics

This is a library for handling subscripted generics in Python.

## Overview

Subscripted generics are a feature of the [typing module](https://docs.python.org/3/library/typing.html) in Python which allow for more expressive typing. They allow you to define generic types with type parameters, such as `List[int]` or `Dict[str, int]`.

This library provides two functions, `isinstance2` and `issubclass2`, which extend the built-in `isinstance` and `issubclass` functions in Python to work with subscripted generics.

## Installation

To install this library, simply run `pip install subscripted-generics`.

## Usage

The two functions provided by this library are `isinstance2` and `issubclass2`. They both work in the same way as the built-in `isinstance` and `issubclass` functions, with the added ability to handle subscripted generics.

For example, the following code will work in Python 3.7 and above:

```python
from subscripted_generics import isinstance2

# Check if an object is an instance of a subscripted type
isinstance2(5, int) # True
isinstance2([1, 2, 3], List[int]) # True
```

Similarly, the following code will work in Python 3.7 and above:

```python
from subscripted_generics import issubclass2

# Check if a class is a subclass of a subscripted type
issubclass2(list, List[int]) # True
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)