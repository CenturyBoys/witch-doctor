"""
Witch Doctor a simple dependencies injection
"""
import functools
import inspect
from abc import ABC
from enum import IntEnum
from typing import Any, Type, TypeVar, List


DEFAULT = "default"


class InjectionType(IntEnum):
    """
    Available injections types
    """

    SINGLETON = 1
    FACTORY = 0


T = TypeVar("T")


class WitchDoctor:
    """
    WitchDoctor provides a register to sign interfaces em types and a
    decorator to inject the dependencies
    """

    _injection_map = {"current": {}, "default": {}}
    _singletons = {}
    _signatures = {}

    @classmethod
    def container(cls, name: str = DEFAULT):
        """
        This method will provide a container register
        :param name: Container name
        :return: Wrapper for register func
        """
        if cls._injection_map.get(name) is None:
            cls._injection_map.update({name: {}})

        def drugstore(
            interface: Type[ABC],
            class_ref: Any,
            injection_type: InjectionType,
            args: List[any] = None,
        ):
            cls.register(
                interface=interface,
                class_ref=class_ref,
                injection_type=injection_type,
                args=args,
                container=name,
            )

        return drugstore

    @classmethod
    def load_container(cls, name: str = DEFAULT):
        """
        Will set the current container by the container name
        :param name:
        :return:
        """
        if name not in cls._injection_map:
            raise ValueError(f"Container {name} not created. Go back and fix it!")
        cls._injection_map["current"].update(cls._injection_map[name])

    @classmethod
    def injection(cls, function: T) -> T:
        """
        WitchDoctor.injection is a function decorator that will match the
        function params signature and inject the  dependencies.\n
        :type function: Callable
        """

        params_signature = []
        for param_name, signature in inspect.signature(function).parameters.items():
            params_signature.append((param_name, signature.annotation))
        cls._signatures[function] = tuple(params_signature)

        @functools.wraps(function)
        def medicine(*args, **kwargs):
            for param, param_type in cls._signatures[function]:
                if param in kwargs:
                    continue
                if class_metadata := cls._injection_map["current"].get(param_type):
                    instance = cls.__resolve_instance(
                        class_ref=class_metadata["cls"],
                        args=class_metadata["args"],
                        injection_type=class_metadata["injection_type"],
                    )
                    kwargs.update({param: instance})
            return function(*args, **kwargs)

        return medicine

    @classmethod
    def __resolve_instance(
        cls, class_ref: T, args: list, injection_type: InjectionType
    ) -> Type[T]:
        if injection_type:
            if cls._singletons.get(class_ref) is None:
                cls._singletons.update({class_ref: class_ref(*args)})
            return cls._singletons.get(class_ref)
        return class_ref(*args)

    @classmethod
    def register(  # pylint: disable=R0913
        cls,
        interface: Type[ABC],
        class_ref: Any,
        injection_type: InjectionType,
        args: List[any] = None,
        container: str = DEFAULT,
    ):
        """
        WitchDoctor.register will check inherit of the interface and class_ref.
        Will raise a TypeError on validation error\n
        :param interface: Interface that inherits from ABC
        :param class_ref: A implementation of the interface
        :param injection_type: The injection type that must be used for this register.
        Allowed Factory or Singleton
        :param args: List of args tha will be used to instantiate the class object
        :param container: Container name where the reference will be saved.
        """
        if not issubclass(interface, ABC):
            raise TypeError("Interface does not inherit from ABC")
        if not issubclass(class_ref, interface):
            raise TypeError(f"Class reference not implements {interface.__name__}")
        if not isinstance(injection_type, InjectionType):
            raise TypeError("Invalid injection_type, must be one of InjectionType")
        if args is None:
            args = []
        cls._injection_map[container].update(
            {
                interface: {
                    "cls": class_ref,
                    "args": args,
                    "injection_type": injection_type,
                }
            }
        )
        return cls
