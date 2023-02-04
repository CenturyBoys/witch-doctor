from abc import ABC, abstractmethod

from witch_doctor import WitchDoctor

import pytest


class IStubFromABCClass(ABC):
    @abstractmethod
    def sum(self, a: int, b: int):
        pass


class IStubClass:
    pass


class Stub1FromABCClass(IStubFromABCClass):
    def sum(self, a: int, b: int):
        return a + b


class Stub2FromABCClass:
    pass


class Stub3FromABCClass:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    @WitchDoctor.injection
    def perform_sum(self, c: IStubFromABCClass):
        return c.sum(self.a, self.b)


def test_register_invalid_interface():
    with pytest.raises(TypeError) as error:
        WitchDoctor.register(IStubClass, Stub1FromABCClass)
    assert error.value.args == ("Interface does not inherit from ABC",)


def test_register_invalid_class_reference():
    with pytest.raises(TypeError) as error:
        WitchDoctor.register(IStubFromABCClass, Stub2FromABCClass)
    assert error.value.args == ("Class reference not implements IStubFromABCClass",)


def test_injection_without_register():
    with pytest.raises(TypeError) as error:

        @WitchDoctor.injection
        def func_t(a, b: str, c: bool):
            return f"{a}{b}"

        func_t(a=1, b="")

    assert error.value.args == (
        "test_injection_without_register.<locals>.func_t() missing 1 required positional argument: 'c'",
    )


def test_injection():
    WitchDoctor.register(IStubFromABCClass, Stub1FromABCClass)

    @WitchDoctor.injection
    def func_t(a: int, b: int, c: IStubFromABCClass):
        return c.sum(a, b)

    result_a1 = func_t(a=1, b=2)
    result_a2 = func_t(a=2, b=2)

    assert result_a1 == 3
    assert result_a2 == 4


def test_injection_on_class_method():
    WitchDoctor.register(IStubFromABCClass, Stub1FromABCClass)

    stub_c = Stub3FromABCClass(a=1, b=2)
    result = stub_c.perform_sum()
    assert result == 3
