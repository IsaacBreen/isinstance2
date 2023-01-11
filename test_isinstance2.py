import pytest
import typing

from isinstance2 import GenericAlias
from isinstance2 import isinstance2, issubclass2, register_instance_checker


def test_isinstance2_with_int():
    assert isinstance2(1, int)
    assert not isinstance2(1, str)


def test_isinstance2_with_subscripted_generic():
    assert isinstance2([1, 2, 3], typing.List[int])
    assert not isinstance2([1, 2, 3], typing.List[str])


def test_isinstance2_with_union_type():
    assert isinstance2(1, typing.Union[int, str])
    assert isinstance2("hello", typing.Union[int, str])
    # This might be surprising, bool is a subclass of int, so the following assertion passes
    assert isinstance2(True, typing.Union[int, str])


def test_isinstance2_with_tuple():
    assert isinstance2((1, 2, 3), typing.Tuple[int, int, int])
    assert not isinstance2((1, 2, 3), typing.Tuple[int, int, str])
    assert isinstance2((1, 2, 3), typing.Tuple[int, ...])
    assert not isinstance2((1, 2, 3), typing.Tuple[str, ...])


def test_isinstance2_with_literal():
    assert isinstance2("hello", typing.Literal["hello"])
    assert not isinstance2("world", typing.Literal["hello"])


def test_isinstance2_with_nested_subscripted_generics():
    assert isinstance2([[(1, 2), (3, 4)], [(5, 6), (7, 8)]], typing.List[typing.List[typing.Tuple[int, int]]])
    assert not isinstance2([[(1, "2"), (3, 4)], [(5, 6), (7, 8)]], typing.List[typing.List[typing.Tuple[int, int]]])


def test_isinstance2_with_complex_unions():
    assert isinstance2({"a": 1, "b": 2}, typing.Union[typing.Dict[str, int], typing.Dict[str, str]])
    assert not isinstance2({"a": 1, "b": "2"}, typing.Union[typing.Dict[str, int], typing.Dict[str, str]])
    assert isinstance2(["a", "b"], typing.Union[typing.List[str], typing.List[int]])


def test_isinstance2_with_custom_classes_with_generic_subclasses():
    class MyList(typing.List[int]):
        pass

    my_list = MyList([1, 2, 3])
    assert isinstance2(my_list, typing.List[int])
    assert not isinstance2(my_list, typing.List[str])


def test_isinstance2_with_recursive_generics():
    T = typing.TypeVar("T")

    class TreeNode(typing.Generic[T]):
        def __init__(self, value: T, children: typing.List["TreeNode[T]"]):
            self.value = value
            self.children = children

    @register_instance_checker(TreeNode)
    def _tree_node_is_instance_of(obj: object, arg: typing.Optional[type | GenericAlias]) -> bool:
        if not isinstance(obj, TreeNode):
            return False
        return arg is None or isinstance2(obj.value, arg)


    node = TreeNode(1, [TreeNode(2, []), TreeNode(3, [])])
    assert isinstance2(node, TreeNode[int])
    assert not isinstance2(node, TreeNode[str])


def test_isinstance2_with_dictionaries_with_subscripted_generics():
    assert isinstance2({"a": 1, "b": 2}, typing.Dict[str, int])
    assert not isinstance2({"a": 1, "b": "2"}, typing.Dict[str, int])


def test_isinstance2_with_nested_lists_with_different_types():
    assert isinstance2([[1, 2, 3], ["a", "b", "c"]], typing.List[typing.Union[typing.List[int], typing.List[str]]])


def test_issubclass2_with_int():
    assert issubclass2(int, int)
    assert not issubclass2(int, str)


def test_issubclass2_with_subscripted_generic():
    assert issubclass2(typing.List[int], typing.List[int])
    assert not issubclass2(typing.List[int], typing.List[str])


def test_issubclass2_with_union_type():
    assert issubclass2(typing.Union[int, str], typing.Union[int, str])
    assert not issubclass2(typing.Union[int, str], typing.Union[int, bool])


def test_issubclass2_with_tuple():
    assert issubclass2(typing.Tuple[int, int, int], typing.Tuple[int, int, int])
    assert not issubclass2(typing.Tuple[int, int, int], typing.Tuple[int, int, str])
    assert issubclass2(typing.Tuple[int, int, int], typing.Tuple[int, ...])
    assert not issubclass2(typing.Tuple[int, int, int], typing.Tuple[str, ...])


def test_issubclass2_with_literal():
    assert issubclass2(typing.Literal["hello"], typing.Literal["hello"])
    assert not issubclass2(typing.Literal["hello"], typing.Literal["world"])


def test_issubclass2_with_nested_subscripted_generics():
    assert issubclass2(typing.List[typing.List[typing.Tuple[int, int]]], typing.List[typing.List[typing.Tuple[int, int]]])
    assert not issubclass2(typing.List[typing.List[typing.Tuple[int, int]]], typing.List[typing.List[typing.Tuple[int, str]]])


def test_issubclass2_with_complex_unions():
    assert issubclass2(typing.Union[typing.Dict[str, int], typing.Dict[str, str]], typing.Union[typing.Dict[str, int], typing.Dict[str, str]])
    assert not issubclass2(typing.Union[typing.Dict[str, int], typing.Dict[str, str]], typing.Union[typing.Dict[str, int], typing.Dict[str, bool]])
    assert issubclass2(typing.Union[typing.List[str], typing.List[int]], typing.Union[typing.List[str], typing.List[int]])
    assert not issubclass2(typing.Union[typing.List[str], typing.List[int]], typing.Union[typing.List[str], typing.List[bool]])
    assert issubclass2(typing.Union[typing.List[str], typing.List[int]], typing.List[typing.Union[str, int]])
    assert not issubclass2(typing.Union[typing.List[str], typing.List[int]], typing.List[typing.Union[str, bool]])


@pytest.mark.xfail(reason="Support for custom classes with generic subclasses is not implemented yet")
def test_issubclass2_with_custom_classes_with_generic_subclasses():
    class MyList(typing.List[int]):
        pass

    assert issubclass2(MyList, typing.List[int])
    assert not issubclass2(MyList, typing.List[str])


@pytest.mark.xfail(reason="Support for recursive generics is not implemented yet")
def test_issubclass2_with_recursive_generics():
    T = typing.TypeVar("T")

    class TreeNode(typing.Generic[T]):
        def __init__(self, value: T, children: typing.List["TreeNode[T]"]):
            self.value = value
            self.children = children

    @register_subclass_checker(TreeNode)
    def _tree_node_is_subclass_of(obj: object, arg: typing.Optional[type | GenericAlias]) -> bool:
        if not issubclass(obj, TreeNode):
            return False
        return arg is None or issubclass2(obj.__args__[0], arg)

    assert issubclass2(TreeNode[int], TreeNode[int])
    assert not issubclass2(TreeNode[int], TreeNode[str])


def test_issubclass2_with_dictionaries_with_subscripted_generics():
    assert issubclass2(typing.Dict[str, int], typing.Dict[str, int])
    assert not issubclass2(typing.Dict[str, int], typing.Dict[str, str])
    assert issubclass2(typing.Dict[str, int], typing.Dict[str, typing.Union[int, str]])
    assert issubclass2(typing.Dict[str, int | str], typing.Dict[str, typing.Union[int, str]])
