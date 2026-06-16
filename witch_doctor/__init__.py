"""
Witch Doctor a simple dependency injection library
"""

import functools
import inspect
import threading
from abc import ABC
from enum import IntEnum
from typing import Any, List, Type, TypeVar

DEFAULT = "_default"
CURRENT = "_current"


class InjectionType(IntEnum):
    """
    Available injections types
    """

    SINGLETON = 1
    FACTORY = 0


T = TypeVar("T")


class WitchDoctor:
    """
    WitchDoctor provides a register to sign interfaces and types and a
    decorator to inject the dependencies
    """

    _injection_map = {CURRENT: {}, DEFAULT: {}}
    _singletons = {}
    _signatures = {}
    _singleton_lock = threading.Lock()

    @classmethod
    def _reset(cls):
        """Reset all internal state for test isolation."""
        cls._injection_map = {CURRENT: {}, DEFAULT: {}}
        cls._singletons = {}

    @classmethod
    def container(cls, name: str = DEFAULT):
        """
        Returns a wrapper function to register dependencies in a specific container scope.

        If the container does not exist, it will be created automatically. The returned
        function can be used to register an interface, its implementation, injection type,
        and optional constructor arguments.

        :param name: The name of the container scope. Defaults to the global DEFAULT container.
        :return: A function that registers an interface with its implementation and injection settings.
        """
        if cls._injection_map.get(name) is None:
            cls._injection_map.update({name: {}})

        def drugstore(
            interface: type[ABC],
            class_ref: Any,
            injection_type: InjectionType,
            args: list[Any] = None,
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
        Loads a previously defined container scope into the current context.

        This method sets the current container by copying the contents of the specified
        container into the `CURRENT` container. It allows dynamic switching between
        different dependency scopes.

        Raises a ValueError if the specified container has not been created.

        :param name: The name of the container to load into the current scope.
                     Defaults to the global DEFAULT container.
        :return: None
        """
        if name not in cls._injection_map:
            raise ValueError(f"Container {name} not created. Go back and fix it!")
        cls._injection_map[CURRENT].update(cls._injection_map[name])

    @classmethod
    def injection(cls, function: T) -> T:
        """
        Decorator that automatically injects dependencies based on the function's parameter annotations.

        WitchDoctor will inspect the function signature, match parameter types with registered
        dependencies in the current container, and inject the appropriate instances at runtime.

        Parameters already passed in the call (via args or kwargs) will not be overwritten.

        :param function: The target function to decorate. Parameters must use type annotations.
        :return: The wrapped function with automatic dependency injection.
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
                if class_metadata := cls._injection_map[CURRENT].get(param_type):
                    instance = cls.__resolve_instance(
                        class_ref=class_metadata["cls"],
                        args=class_metadata["args"],
                        injection_type=class_metadata["injection_type"],
                        container_name=CURRENT,
                    )
                    kwargs.update({param: instance})
            return function(*args, **kwargs)

        return medicine

    @classmethod
    def resolve(cls, interface: T, container_name: str = CURRENT) -> type[T]:
        """
        Returns an instance of the class registered for the given interface.
        Raises a TypeError if the interface is not registered.

        :param interface: The interface to resolve an implementation for.
        :param container_name: (Optional) The name of the container scope to use.
                               Defaults to the current active container.
        :return: An instance of the implementation bound to the given interface.
        """
        if container_name not in cls._injection_map:
            raise TypeError("Container not registered")
        if class_metadata := cls._injection_map[container_name].get(interface):
            return cls.__resolve_instance(
                class_ref=class_metadata["cls"],
                args=class_metadata["args"],
                injection_type=class_metadata["injection_type"],
                container_name=container_name,
            )
        raise TypeError(f"Interface was not registered on {container_name} container")

    @classmethod
    def __resolve_instance(
        cls,
        class_ref: T,
        args: list,
        injection_type: InjectionType,
        container_name: str,
    ) -> type[T]:
        if injection_type:
            key = (container_name, class_ref)
            if cls._singletons.get(key) is None:
                with cls._singleton_lock:
                    if cls._singletons.get(key) is None:
                        cls._singletons[key] = class_ref(*args)
            return cls._singletons[key]
        return class_ref(*args)

    @classmethod
    def register(  # pylint: disable=R0913
        cls,
        interface: type[ABC],
        class_ref: Any,
        injection_type: InjectionType,
        args: list[Any] = None,
        container: str = DEFAULT,
    ):
        """
        Registers a class implementation for a given interface in the specified container.

        This method validates that the provided interface inherits from `ABC` and that
        the implementation class (`class_ref`) properly inherits from the interface.
        It also checks that the `injection_type` is valid (either Factory or Singleton).
        If validation fails, a `TypeError` is raised.

        :param interface: An abstract base class (must inherit from `ABC`).
        :param class_ref: The concrete class that implements the given interface.
        :param injection_type: The injection behavior to use. Must be one of `InjectionType.FACTORY` or `InjectionType.SINGLETON`.
        :param args: Optional list of arguments to pass to the class constructor during instantiation.
        :param container: The name of the container scope where the implementation will be registered. Defaults to the global container.
        :return: The WitchDoctor class itself, to allow chaining.
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

    @classmethod
    def clear_container(cls, name: str):
        """
        Clears all singleton instances for a specific container.
        Useful for multi-tenant scenarios where you need to unload a tenant.

        :param name: The name of the container to clear singletons for.
        """
        keys_to_remove = [key for key in cls._singletons if key[0] == name]
        for key in keys_to_remove:
            del cls._singletons[key]
