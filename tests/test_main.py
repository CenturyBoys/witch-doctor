from abc import ABC, abstractmethod

from witch_doctor import WitchDoctor, InjectionType

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


class Stub4FromABCClass(IStubFromABCClass):
    def __init__(self, a: int):
        self.a = a

    def sum(self, a: int, b: int):
        return a + b + self.a


def test_register_invalid_interface():
    with pytest.raises(TypeError) as error:
        WitchDoctor.register(IStubClass, Stub1FromABCClass, InjectionType.SINGLETON)
    assert error.value.args == ("Interface does not inherit from ABC",)


def test_register_invalid_class_reference():
    with pytest.raises(TypeError) as error:
        WitchDoctor.register(
            IStubFromABCClass, Stub2FromABCClass, InjectionType.FACTORY
        )
    assert error.value.args == ("Class reference not implements IStubFromABCClass",)


def test_register_invalid_injection_type():
    with pytest.raises(TypeError) as error:
        WitchDoctor.register(IStubFromABCClass, Stub1FromABCClass, 3)
    assert error.value.args == ("Invalid injection_type, must be one of InjectionType",)


def test_load_not_created_container():
    with pytest.raises(ValueError) as error:
        WitchDoctor.load_container("lallaa")
    assert error.value.args == ("Container lallaa not created. Go back and fix it!",)


def test_injection_without_register():
    with pytest.raises(TypeError) as error:

        @WitchDoctor.injection
        def func_t(a, b: str, c: bool):
            return f"{a}{b}"

        func_t(a=1, b="")

    assert error.value.args == (
        "test_injection_without_register.<locals>.func_t() missing 1 required positional argument: 'c'",
    )


def test_validate_single__injection_map():
    container_name = "t1"
    assert container_name not in WitchDoctor._injection_map
    container = WitchDoctor.container(container_name)
    container(IStubFromABCClass, Stub1FromABCClass, InjectionType.FACTORY)
    assert WitchDoctor._injection_map[container_name]
    WitchDoctor.container(container_name)
    assert WitchDoctor._injection_map[container_name]


def test_injection():
    container = WitchDoctor.container("t1")
    container(IStubFromABCClass, Stub1FromABCClass, InjectionType.FACTORY)

    WitchDoctor.register(IStubFromABCClass, Stub1FromABCClass, InjectionType.FACTORY)

    @WitchDoctor.injection
    def func_t(a: int, b: int, c: IStubFromABCClass):
        return c.sum(a, b)

    WitchDoctor.load_container()

    result_a1 = func_t(a=1, b=2)
    result_a2 = func_t(a=2, b=2)

    assert result_a1 == 3
    assert result_a2 == 4

    WitchDoctor.load_container("t1")

    result_a1 = func_t(a=1, b=2)
    result_a2 = func_t(a=2, b=2)

    assert result_a1 == 3
    assert result_a2 == 4


def test_inject_overwrite():
    WitchDoctor.register(IStubFromABCClass, Stub1FromABCClass, InjectionType.FACTORY)

    class Stub5FromABCClass(IStubFromABCClass):
        def sum(self, a: int, b: int):
            return a + b + 10

    @WitchDoctor.injection
    def func_t(a: int, b: int, c: IStubFromABCClass):
        return c.sum(a, b)

    result_a1 = func_t(a=1, b=2, c=Stub5FromABCClass())

    assert result_a1 == 13


def test_injection_on_class_method():
    WitchDoctor.register(IStubFromABCClass, Stub1FromABCClass, InjectionType.FACTORY)

    stub_c = Stub3FromABCClass(a=1, b=2)
    result = stub_c.perform_sum()
    assert result == 3


def test_container_injection():
    container = WitchDoctor.container("t1")
    container(IStubFromABCClass, Stub4FromABCClass, InjectionType.SINGLETON, args=[20])
    container = WitchDoctor.container()
    container(IStubFromABCClass, Stub4FromABCClass, InjectionType.FACTORY, args=[10])

    WitchDoctor.load_container()

    @WitchDoctor.injection
    def func_t(a: int, b: int, c: IStubFromABCClass):
        return c.sum(a, b)

    result_a1 = func_t(a=1, b=2)
    result_a2 = func_t(a=2, b=2)

    assert result_a1 == 13
    assert result_a2 == 14

    WitchDoctor.load_container("t1")

    result_a1 = func_t(a=1, b=2)
    result_a2 = func_t(a=2, b=2)

    assert result_a1 == 23
    assert result_a2 == 24


def test_injection_type():
    WitchDoctor.register(
        IStubFromABCClass, Stub4FromABCClass, InjectionType.SINGLETON, args=[10]
    )
    WitchDoctor.load_container()

    @WitchDoctor.injection
    def func_t(c: IStubFromABCClass):
        return c

    instance_a1 = func_t()
    instance_a2 = func_t()

    assert id(instance_a2) == id(instance_a1)

    WitchDoctor.register(
        IStubFromABCClass, Stub4FromABCClass, InjectionType.FACTORY, args=[10]
    )
    WitchDoctor.load_container()

    instance_a3 = func_t()
    instance_a4 = func_t()

    assert id(instance_a4) != id(instance_a3)
