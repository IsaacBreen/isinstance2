"""
This module provides two functions - `isinstance2` and `issubclass2` - which extend the built-in `isinstance` and
`issubclass` functions in Python to work with subscripted generics.
"""
import types
import typing
from collections.abc import Collection, Iterable, Mapping, MutableMapping, Sequence
from functools import partial
from types import UnionType
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, TypeVar, TypeVarTuple, Union, get_args, get_origin

GenericAlias = types.GenericAlias | typing.GenericAlias | typing._GenericAlias | typing._SpecialGenericAlias | types.UnionType  # type: ignore

T = TypeVar("T")
Ts = TypeVarTuple("Ts")

instance_checker_registry: dict[type, callable] = {}


def register(registry, key):
    def decorator(func):
        registry[key] = func
        return func

    return decorator


register_instance_checker = partial(register, instance_checker_registry)


@register(instance_checker_registry, Union)
@register(instance_checker_registry, UnionType)
def _is_instance_of_union(obj: Any, *args: type | GenericAlias) -> bool:
    for arg in args:
        if isinstance2(obj, arg):
            return True
    return False


@register(instance_checker_registry, Literal)
def _is_instance_of_literal(obj: Any, *args: type | GenericAlias) -> bool:
    for arg in args:
        if obj == arg:
            return True
    return False


# Tuple instance checks must be treated separately from other iterables because
# they have variadic arguments.
@register(instance_checker_registry, tuple)
@register(instance_checker_registry, Tuple)
def _is_instance_of_tuple(obj: Any, *args: type | GenericAlias) -> bool:
    if not isinstance(obj, tuple):
        return False
    if Ellipsis in args:
        if len(args) != 2:
            raise TypeError(f"Tuple with Ellipsis must have exactly two arguments; got {len(args)}")
        return all(isinstance2(item, args[0]) for item in obj)
    else:
        return len(obj) == len(args) and all(isinstance2(item, arg) for item, arg in zip(obj, args))


def _is_instance_of_iterable(obj: Any, arg: Optional[type | GenericAlias], *, IterableSubtype: type) -> bool:
    if not isinstance(obj, IterableSubtype):
        return False
    return arg is None or all(isinstance2(item, arg) for item in obj)


for IterableSubtype in (Iterable, Collection, Sequence, List, list, Set, set, frozenset):
    register(instance_checker_registry, IterableSubtype)(
        partial(_is_instance_of_iterable, IterableSubtype=IterableSubtype)
    )


def _is_instance_of_mapping(
    obj: Any, key_type: Optional[type | GenericAlias], value_type: Optional[type | GenericAlias], *,
    MappingSubtype: type
) -> bool:
    if not isinstance(obj, MappingSubtype):
        return False
    if key_type is None and value_type is None:
        return True
    if key_type is None or value_type is None:
        raise TypeError(f"Got only one of key_type and value_type, expected both or neither")
    return all(isinstance2(key, key_type) and isinstance2(value, value_type) for key, value in obj.items())


for MappingSubtype in (Mapping, MutableMapping, Dict, dict):
    register(instance_checker_registry, MappingSubtype)(
        partial(_is_instance_of_mapping, MappingSubtype=MappingSubtype)
    )


def isinstance2(
    obj: Any, cls: type | GenericAlias, instance_check_registry: Dict[type, callable] = instance_checker_registry
) -> bool:
    """
    Check if an object is an instance of a subscripted superclass.

    Args:
        obj: The object to check.
        cls: The type to check against.

    Returns:
        True if the object is an instance of the superclass, False otherwise.
    """
    if isinstance(cls, GenericAlias):
        origin_cls = get_origin(cls)

        if origin_cls is None:
            raise TypeError(f"Got no origin for {cls}")

        args = get_args(cls)

        if len(args) > 0:
            if origin_cls in instance_checker_registry:
                return instance_checker_registry[origin_cls](obj, *args)
            else:
                raise TypeError(f"Did not find a checker for {origin_cls}")
        else:
            return True

    elif cls is Any:
        return True

    elif isinstance(cls, type):
        return isinstance(obj, cls)

    else:
        raise TypeError(f"Expected a type or a GenericAlias; got {cls} of type {type(cls)}")


def issubclass2(cls: type | GenericAlias, superclass: type | GenericAlias) -> bool:  # type: ignore
    """
    Check if a class is a subclass of a subscripted superclass.

    Args:
        cls: The class to check.
        superclass: The type to check against.

    Returns:
        True if the class is a subclass of the superclass, False otherwise.
    """
    # NOTE: This function needs a lot of work. It's way too long.
    # TODO: Separate out the logic into smaller functions.
    if superclass is Any:
        return True
    elif isinstance(cls, GenericAlias) and get_origin(cls) in (Union, UnionType):
        # Each argument of the union must be a subclass of the superclass
        return all(issubclass2(arg, superclass) for arg in get_args(cls))
    elif isinstance(cls, GenericAlias) and get_origin(cls) == Literal:
        # Each argument of the literal must be an instance of the superclass
        return all(isinstance2(obj, superclass) for obj in get_args(cls))
    elif isinstance(superclass, GenericAlias) and get_origin(superclass) in (Union, UnionType):
        # The class must be a subclass of at least one argument of the union
        return any(issubclass2(cls, arg) for arg in get_args(superclass))
    elif isinstance(cls, GenericAlias) and isinstance(superclass, GenericAlias):
        # Get the origins of each superclass
        origin_cls: type = get_origin(cls)
        origin_superclass: type = get_origin(superclass)

        # Get the arguments of each superclass
        args_cls = get_args(cls)
        args_superclass = get_args(superclass)

        # Check for special cases
        if origin_cls is None:
            raise TypeError(f"Got no origin for {cls}")
        if origin_superclass is None:
            raise TypeError(f"Got no origin for {superclass}")
        if origin_cls != tuple and issubclass(origin_cls, tuple):
            raise NotImplementedError(f"Got subclass of tuple for {cls}")
        if origin_superclass != tuple and issubclass(origin_superclass, tuple):
            raise NotImplementedError(f"Got subclass of tuple for {superclass}")

        if origin_cls == tuple and origin_superclass == tuple:
            # We must be careful to handle Ellipsis. There are four cases:
            #
            #   1. Ellipsis in cls and not in superclass
            #     - The cls tuple can be arbitrarily long, but the superclass tuple must have exactly two arguments.
            #       So, cls cannot be a subclass of superclass.
            #
            #   2. Ellipsis not in cls and in superclass
            #     - Each argument of cls must be a subclass of the first argument of superclass.
            #
            #   3. Ellipsis in both cls and superclass
            #     - The first argument of cls must be a subclass of the first argument of superclass.
            #
            #   4. Ellipsis not in either cls or superclass
            #     - The two tuples must have the same length and each argument of cls must be a subclass of the
            #       corresponding argument of superclass.
            #
            if Ellipsis in args_cls:
                if len(args_cls) != 2:
                    raise TypeError(f"Tuple with Ellipsis must have exactly two arguments; got {len(args_cls)}")
            if Ellipsis in args_superclass:
                if len(args_superclass) != 2:
                    raise TypeError(
                        f"Tuple with Ellipsis must have exactly two arguments; got {len(args_superclass)}"
                    )
            if Ellipsis in args_cls and Ellipsis not in args_superclass:
                return False
            elif Ellipsis not in args_cls and Ellipsis in args_superclass:
                return all(issubclass2(arg_cls, args_superclass[0]) for arg_cls in args_cls)
            elif Ellipsis in args_cls and Ellipsis in args_superclass:
                return issubclass2(args_cls[0], args_superclass[0])
            elif Ellipsis not in args_cls and Ellipsis not in args_superclass:
                return len(args_cls) == len(args_superclass) and all(
                    issubclass2(arg_cls, arg_superclass) for arg_cls, arg_superclass in zip(args_cls, args_superclass)
                )

        # If the superclass is a tuple, the origin of cls must be a subclass of the origin of superclass
        if origin_superclass == tuple and not issubclass(origin_cls, tuple):
            return False

        # TODO: can this be combined with the above? Or otherwise simplified?
        if origin_superclass != tuple and origin_cls == tuple and issubclass(origin_superclass, Iterable):
            if Ellipsis in args_cls:
                if len(args_cls) != 2:
                    raise TypeError(f"Tuple with Ellipsis must have exactly two arguments; got {len(args_cls)}")
                if args_cls[0] is Ellipsis:
                    raise TypeError("Tuple with Ellipsis must have exactly two arguments and the first argument must not be Ellipsis")
                if args_cls[1] is Ellipsis:
                    return issubclass(origin_cls, origin_superclass) and issubclass2(args_cls[0], args_cls[0])
            else:
                return issubclass(origin_cls, origin_superclass) and all(issubclass2(arg_cls, args_superclass[0]) for arg_cls in args_cls)

        # If, by this point, either class is a subclass of tuple, we cannot handle it
        if issubclass(origin_cls, tuple):
            raise NotImplementedError(f"Got subclass of tuple for {cls}")
        if issubclass(origin_superclass, tuple):
            raise NotImplementedError(f"Got subclass of tuple for {superclass}")

        # Check for the mapping cases
        if issubclass(origin_superclass, Mapping):
            # The origin of cls must be a subclass of the origin of superclass
            if not issubclass(origin_cls, origin_superclass):
                return False

            # If one of the classes lacks arguments, we presume a match
            if len(args_cls) == 0 or len(args_superclass) == 0:
                return True

            # Otherwise, both classes must have exactly two arguments
            if len(args_cls) != 2 or len(args_superclass) != 2:
                raise TypeError(f"Expected two arguments; got {len(args_cls)} and {len(args_superclass)}")

            # The first argument of cls (the key) must be a subclass of the first argument of superclass,
            # and likewise for the second argument (the value)
            return issubclass2(args_cls[0], args_superclass[0]) and issubclass2(args_cls[1], args_superclass[1])

        # Get the single argument of superclass
        if len(args_superclass) != 1:
            raise TypeError(f"Got {len(args_superclass)} arguments for {origin_superclass}; expected 1")
        arg_superclass = args_superclass[0]

        # If the origin of cls is a tuple and the origin of superclass is not a tuple, the origin of cls must be a
        # subclass of the origin of superclass
        if origin_cls == tuple and origin_superclass != tuple:
            return issubclass(origin_cls, origin_superclass) and all(
                issubclass2(arg_cls, arg_superclass) for arg_cls in args_cls
            )

        # Get the single argument of cls
        if len(args_cls) != 1:
            raise TypeError(f"Got {len(args_cls)} arguments for {origin_cls}, expected 1")
        arg_cls = args_cls[0]

        # Neither cls nor superclass are a tuple or union
        if not issubclass(origin_cls, origin_superclass):
            return False
        # Other builtin collections
        if origin_cls in (Iterable, Collection, Sequence, List, list, Set, set, frozenset):
            return issubclass2(arg_cls, arg_superclass)
        else:
            raise NotImplementedError(f"Got unknown origin {origin_cls} for {cls}")
    if cls == str:
        if isinstance(superclass, type):
            return issubclass(str, superclass)
        elif isinstance(superclass, GenericAlias):
            args_superclass = get_args(superclass)
            if get_origin(superclass) == Iterable and args_superclass and not issubclass(str, args_superclass[0]):
                return False
            return issubclass(str, get_origin(superclass))
        else:
            raise NotImplementedError(f"Got unknown superclass {superclass} for {cls}")
    elif isinstance(cls, GenericAlias) and isinstance(superclass, type):
        # The origin of cls must be a subclass of superclass
        return issubclass(get_origin(cls), superclass)
    elif isinstance(cls, type) and isinstance(superclass, GenericAlias):
        # cls must be a subclass of the origin of superclass
        return issubclass(cls, get_origin(superclass))
    elif isinstance(cls, type) and isinstance(superclass, type):
        # cls must be a subclass of superclass
        return issubclass(cls, superclass)

    else:
        # cls and superclass must be either a type or a GenericAlias
        raise TypeError(
            f"Expected both arguments to be either a type or a GenericAlias; got {cls} of type {type(cls)} and "
            f"{superclass} of type {type(superclass)}"
        )
