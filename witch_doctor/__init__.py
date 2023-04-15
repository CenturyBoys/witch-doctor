"""
Witch Doctor a simple dependencies injection
"""

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
    FACTORY = 2


T = TypeVar("T")


class WitchDoctor:
    """
    WitchDoctor provides a register to sign interfaces em types and a
    decorator to inject the dependencies
    """

    __injection_map = {"current": {}}
    __singletons = {}

    @classmethod
    def container(cls, name: str = DEFAULT):
        """
        This method will provide a container register
        :param name: Container name
        :return: Wrapper for register func
        """

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
    def load_container(cls, name: str = DEFAULT) -> None:
        """
        Will set the current container by the container name
        :param name:
        :return:
        """
        cls.__injection_map["current"].update(cls.__injection_map[name])

    @classmethod
    def injection(cls, function: T) -> T:
        """
        WitchDoctor.injection is a function decorator that will match the
        function params signature and inject the  dependencies.\n
        :type function: Callable
        """

        def medicine(*args, **kwargs):
            signature = inspect.signature(function).parameters
            for param, signature in signature.items():
                if param in kwargs:
                    continue
                param_type = signature.annotation
                if class_metadata := cls.__injection_map["current"].get(param_type):
                    class_ref = class_metadata["cls"]
                    class_args = class_metadata["args"]
                    injection_type = class_metadata["injection_type"]
                    instance = cls.__resolve_instance(
                        class_ref, class_args, injection_type
                    )
                    kwargs.update({param: instance})
            return function(*args, **kwargs)

        medicine.__wrapped__ = function
        return medicine

    @classmethod
    def __resolve_instance(
        cls, class_ref: T, args: list, injection_type: InjectionType
    ) -> Type[T]:
        if injection_type == InjectionType.SINGLETON:
            if cls.__singletons.get(class_ref) is None:
                cls.__singletons.update({class_ref: class_ref(*args)})
            return cls.__singletons.get(class_ref)
        if injection_type == InjectionType.FACTORY:
            return class_ref(*args)
        return None

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
        if cls.__injection_map.get(container) is None:
            cls.__injection_map.update({container: {}})
        cls.__injection_map[container].update(
            {
                interface: {
                    "cls": class_ref,
                    "args": args,
                    "injection_type": injection_type,
                }
            }
        )
        if container == DEFAULT:
            cls.__injection_map["current"].update(
                {
                    interface: {
                        "cls": class_ref,
                        "args": args,
                        "injection_type": injection_type,
                    }
                }
            )
        return cls
