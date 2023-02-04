"""
Witch Doctor a simple dependencies injection
"""

import inspect
from abc import ABC
from typing import Any, Type, Callable


class WitchDoctor:
    """
    WitchDoctor provides a register to sign interfaces em types and a
    decorator to inject the dependencies
    """

    __injection_map = {}

    @classmethod
    def injection(cls, function: Callable):
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
                if class_ref := cls.__injection_map.get(param_type):
                    kwargs.update({param: class_ref()})
            return function(*args, **kwargs)

        return medicine

    @classmethod
    def register(cls, interface: Type[ABC], class_ref: Any):
        """
        WitchDoctor.register will check inherit of the interface and class_ref.
        Will raise a TypeError on validation error\n
        :param interface: Interface that inherits from ABC
        :param class_ref: A implementation of the interface
        """
        if not issubclass(interface, ABC):
            raise TypeError("Interface does not inherit from ABC")
        if not issubclass(class_ref, interface):
            raise TypeError("Class reference not implements IStubFromABCClass")
        cls.__injection_map.update({interface: class_ref})
