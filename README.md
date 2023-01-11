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
from subscripted