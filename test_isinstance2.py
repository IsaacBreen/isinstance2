import typing

import pytest

from isinstance2 import GenericAlias, isinstance2, issubclass2, register_instance_checker
from typing import *

def test_isinstance2_with_int():
    assert isinstance2(1, int)
    assert not isinstance2(1, str)


def test_isinstance2_with_subscripted_generic():
    assert isinstance2([1, 2, 3], list[int])
    assert not isinstance2([1, 2, 3], list[str])


def test_isinstance2_with_union_type():
    assert isinstance2(1, Union[int, str])
    assert isinstance2("hello", Union[int, str])
    # This might be surprising, bool is a subclass of int, so the following assertion passes
    assert isinstance2(True, Union[int, str])


def test_isinstance2_with_tuple():
    assert isinstance2((1, 2, 3), tuple[int, int, int])
    assert not isinstance2((1, 2, 3), tuple[int, int, str])
    assert isinstance2((1, 2, 3), tuple[int, ...])
    assert not isinstance2((1, 2, 3), tuple[str, ...])


def test_isinstance2_with_literal():
    assert isinstance2("hello", Literal["hello"])
    assert not isinstance2("world", Literal["hello"])


def test_isinstance2_with_nested_subscripted_generics():
    assert isinstance2([[(1, 2), (3, 4)], [(5, 6), (7, 8)]], list[list[tuple[int, int]]])
    assert not isinstance2([[(1, "2"), (3, 4)], [(5, 6), (7, 8)]], list[list[tuple[int, int]]])
    assert not isinstance2({1, (2, 3), frozenset(4,5,6)}, set[int, tuple[int, int], frozenset[int]])


def test_isinstance2_with_complex_unions():
    assert isinstance2({"a": 1, "b": 2}, Union[dict[str, int], dict[str, str]])
    assert not isinstance2({"a": 1, "b": "2"}, Union[dict[str, int], dict[str, str]])
    assert isinstance2(["a", "b"], Union[list[str], list[int]])


def test_isinstance2_with_custom_classes_with_generic_subclasses():
    class MyList(list[int]):
        pass

    my_list = MyList([1, 2, 3])
    assert isinstance2(my_list, list[int])
    assert not isinstance2(my_list, list[str])


def test_isinstance2_with_recursive_generics():
    T = TypeVar("T")

    class TreeNode(Generic[T]):
        def __init__(self, value: T, children: list["TreeNode[T]"]):
            self.value = value
            self.children = children

    @register_instance_checker(TreeNode)
    def _tree_node_is_instance_of(obj: object, arg: Optional[type | GenericAlias]) -> bool:
        if not isinstance(obj, TreeNode):
            return False
        return arg is None or isinstance2(obj.value, arg)

    node = TreeNode(1, [TreeNode(2, []), TreeNode(3, [])])
    assert isinstance2(node, TreeNode[int])
    assert not isinstance2(node, TreeNode[str])


def test_isinstance2_with_dictionaries_with_subscripted_generics():
    assert isinstance2({"a": 1, "b": 2}, dict[str, int])
    assert not isinstance2({"a": 1, "b": "2"}, dict[str, int])


def test_isinstance2_with_nested_lists_with_different_types():
    assert isinstance2([[1, 2, 3], ["a", "b", "c"]], list[list[int] | list[str]])


def test_issubclass2_with_int():
    assert issubclass2(int, int)
    assert not issubclass2(int, str)


def test_issubclass2_with_subscripted_generic():
    assert issubclass2(list[int], list[int])
    assert not issubclass2(list[int], list[str])


def test_issubclass2_with_union_type():
    assert issubclass2(Union[int, str], Union[int, str])
    assert not issubclass2(Union[int, str], Union[int, bool])


def test_issubclass2_with_tuple():
    assert issubclass2(tuple[int, int, int], tuple[int, int, int])
    assert not issubclass2(tuple[int, int, int], tuple[int, int, str])
    assert issubclass2(tuple[int, int, int], tuple[int, ...])
    assert not issubclass2(tuple[int, int, int], tuple[str, ...])


def test_issubclass2_with_literal():
    assert issubclass2(Literal["hello"], Literal["hello"])
    assert not issubclass2(Literal["hello"], Literal["world"])


def test_issubclass2_with_nested_subscripted_generics():
    assert issubclass2(
        list[list[tuple[int, int]]], list[list[tuple[int, int]]]
    )
    assert not issubclass2(
        list[list[tuple[int, int]]], list[list[tuple[int, str]]]
    )


def test_issubclass2_with_complex_unions():
    assert issubclass2(
        Union[dict[str, int], dict[str, str]],
        Union[dict[str, int], dict[str, str]]
    )
    assert not issubclass2(
        Union[dict[str, int], dict[str, str]],
        Union[dict[str, int], dict[str, bool]]
    )
    assert issubclass2(
        Union[list[str], list[int]], Union[list[str], list[int]]
    )
    assert not issubclass2(
        Union[list[str], list[int]], Union[list[str], list[bool]]
    )
    assert issubclass2(Union[list[str], list[int]], list[Union[str, int]])
    assert not issubclass2(Union[list[str], list[int]], list[Union[str, bool]])
    assert issubclass2(Union[list[str], list[int]], list[Any])

    # Set and frozenset are not considered to be subclasses of each other
    assert not issubclass2(set, frozenset)
    assert not issubclass2(frozenset, set)
    assert issubclass2(Union[set, frozenset], Union[set, frozenset])
    assert not issubclass2(set[int], set[str] | frozenset[int])


@pytest.mark.xfail(reason="Support for custom classes with generic subclasses is not implemented yet")
def test_issubclass2_with_custom_classes_with_generic_subclasses():
    class MyList(list[int]):
        pass

    assert issubclass2(MyList, list[int])
    assert not issubclass2(MyList, list[str])


@pytest.mark.xfail(reason="Support for recursive generics is not implemented yet")
def test_issubclass2_with_recursive_generics():
    T = TypeVar("T")

    class TreeNode(Generic[T]):
        def __init__(self, value: T, children: list["TreeNode[T]"]):
            self.value = value
            self.children = children

    @register_subclass_checker(TreeNode)
    def _tree_node_is_subclass_of(obj: object, arg: Optional[type | GenericAlias]) -> bool:
        if not issubclass(obj, TreeNode):
            return False
        return arg is None or issubclass2(obj.__args__[0], arg)

    assert issubclass2(TreeNode[int], TreeNode[int])
    assert not issubclass2(TreeNode[int], TreeNode[str])


def test_issubclass2_with_dictionaries_with_subscripted_generics():
    assert issubclass2(dict[str, int], dict[str, int])
    assert not issubclass2(dict[str, int], dict[str, str])
    assert issubclass2(dict[str, int], dict[str, Union[int, str]])
    assert issubclass2(dict[str, int | str], dict[str, Union[int, str]])
