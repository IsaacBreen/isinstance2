"""
Extensions of `isinstance` and `issubclass` that work with subscripted generics.

Example:

```python
assert isinstance_generic((1, 2.0, "three", "four"), tuple[int, float, str, Literal["four"]])
assert issubclass_generic([1, 2.0 "three", "four"], Sequence[int | float | str])
```
"""
import types
import typing
from collections.abc import Collection
from collections.abc import Iterable
from collections.abc import Sequence
from types import UnionType
from typing import Any
from typing import Literal
from typing import Union
from typing import get_args
from typing import get_origin

GenericAlias = types.GenericAlias | typing.GenericAlias | typing._GenericAlias | types.UnionType  # type: ignore


def isinstance_generic(obj: Any, generic_type: type | GenericAlias) -> bool:  # type: ignore
    """
    Check if an object is an instance of a subscripted generic type.

    Args:
        obj: The object to check.
        generic_type: The subscripted generic type.

    Returns:
        True if the object is an instance of the generic type, False otherwise.
    """
    if isinstance(generic_type, GenericAlias):
        origin_generic_type = get_origin(generic_type)

        if origin_generic_type is None:
            raise TypeError(f"Got no origin for {generic_type}")

        args = get_args(generic_type)

        if origin_generic_type in (Union, UnionType):
            return any(isinstance_generic(obj, arg) for arg in args)
        elif origin_generic_type == Literal:
            return any(obj == arg for arg in args)
        elif origin_generic_type == tuple:
            if not isinstance(obj, origin_generic_type):
                return False
            if Ellipsis in args:
                if len(args) != 2:
                    raise TypeError(f"Tuple with Ellipsis must have exactly two arguments, got {len(args)}")
                return all(isinstance_generic(item, args[0]) for item in obj)
            else:
                return len(obj) == len(args) and all(isinstance_generic(item, arg) for item, arg in zip(obj, args))

        if len(args) != 1:
            raise TypeError(f"Got {len(args)} arguments for {origin_generic_type}, expected 1")
        arg = args[0]

        if not isinstance(obj, origin_generic_type):
            return False
        elif origin_generic_type in (list, Sequence, Iterable, Collection):
            return all(isinstance_generic(item, arg) for item in obj)
        else:
            raise NotImplementedError(f"Got unknown origin {origin_generic_type} for {generic_type}")

    elif isinstance(generic_type, type):
        return isinstance(obj, generic_type)

    else:
        raise TypeError(f"Expected a type or a GenericAlias, got {generic_type} of type {type(generic_type)}")


def issubclass_generic(cls: type | GenericAlias, generic_type: type | GenericAlias) -> bool:  # type: ignore
    """
    Check if a class is a subclass of a subscripted generic type.

    Args:
        cls: The class to check.
        generic_type: The subscripted generic type.

    Returns:
        True if the class is a subclass of the generic type, False otherwise.
    """
    if isinstance(cls, GenericAlias) and get_origin(cls) in (Union, UnionType):
        return all(issubclass_generic(arg, generic_type) for arg in get_args(cls))
    elif isinstance(cls, GenericAlias) and get_origin(cls) == Literal:
        return all(isinstance_generic(obj, generic_type) for obj in get_args(cls))
    elif isinstance(generic_type, GenericAlias) and get_origin(generic_type) in (Union, UnionType):
        return any(issubclass_generic(cls, arg) for arg in get_args(generic_type))
    elif isinstance(cls, GenericAlias) and isinstance(generic_type, GenericAlias):
        origin_cls: type = get_origin(cls)
        origin_generic_type: type = get_origin(generic_type)

        if origin_cls is None:
            raise TypeError(f"Got no origin for {cls}")
        if origin_generic_type is None:
            raise TypeError(f"Got no origin for {generic_type}")

        args_cls = get_args(cls)
        args_generic_type = get_args(generic_type)

        if origin_cls != tuple and issubclass(origin_cls, tuple):
            raise NotImplementedError(f"Got subclass of tuple for {cls}")
        if origin_generic_type != tuple and issubclass(origin_generic_type, tuple):
            raise NotImplementedError(f"Got subclass of tuple for {generic_type}")
        if origin_cls == tuple and origin_generic_type == tuple:
            if Ellipsis in args_cls:
                if len(args_cls) != 2:
                    raise TypeError(f"Tuple with Ellipsis must have exactly two arguments, got {len(args_cls)}")
            if Ellipsis in args_generic_type:
                if len(args_generic_type) != 2:
                    raise TypeError(
                        f"Tuple with Ellipsis must have exactly two arguments, got {len(args_generic_type)}"
                    )
            if Ellipsis in args_cls and Ellipsis not in args_generic_type:
                return False
            elif Ellipsis not in args_cls and Ellipsis in args_generic_type:
                return all(issubclass_generic(arg_cls, args_generic_type[0]) for arg_cls in args_cls)
            elif Ellipsis in args_cls and Ellipsis in args_generic_type:
                return issubclass_generic(args_cls[0], args_generic_type[0])
            elif Ellipsis not in args_cls and Ellipsis not in args_generic_type:
                return len(args_cls) == len(args_generic_type) and all(
                    issubclass_generic(arg_cls, arg_generic_type) for arg_cls, arg_generic_type in
                    zip(args_cls, args_generic_type)
                )

        if origin_generic_type == tuple and not issubclass(origin_cls, tuple):
            return False

        if len(args_generic_type) != 1:
            raise TypeError(f"Got {len(args_generic_type)} arguments for {origin_generic_type}, expected 1")
        arg_generic_type = args_generic_type[0]

        if origin_cls == tuple and origin_generic_type != tuple:
            return issubclass(origin_cls, origin_generic_type) and all(
                issubclass_generic(arg_cls, arg_generic_type) for arg_cls in args_cls
            )

        if len(args_cls) != 1:
            raise TypeError(f"Got {len(args_cls)} arguments for {origin_cls}, expected 1")
        arg_cls = args_cls[0]

        # Neither cls nor generic_type are a tuple or union
        if not issubclass(origin_cls, origin_generic_type):
            return False
        if origin_cls in (list, Sequence, Iterable, Collection):
            return issubclass_generic(arg_cls, arg_generic_type)
        else:
            raise NotImplementedError(f"Got unknown origin {origin_cls} for {cls}")
    elif isinstance(cls, GenericAlias) and isinstance(generic_type, type):
        return issubclass(get_origin(cls), generic_type)
    elif isinstance(cls, type) and isinstance(generic_type, GenericAlias):
        return issubclass(cls, get_origin(generic_type))
    elif isinstance(cls, type) and isinstance(generic_type, type):
        return issubclass(cls, generic_type)

    else:
        raise TypeError(
            f"Expected both arguments to be either a type or a GenericAlias, got {cls} of type {type(cls)} and {generic_type} of type {type(generic_type)}"
        )
