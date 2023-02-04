<img src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2Fe6%2Fff%2F86%2Fe6ff86db1ad224c37d328579786e13f3.jpg&f=1&nofb=1&ipt=448de94a888dd920ca7383f804f09f69d49ad4d226d9bee06115bbc9b188e1d2&ipo=images" alt="drawing" style="width:400px;display: block;  margin-left: auto;margin-right: auto;"/>
By: CenturyBoys

# Witch-doctor

A simple dependency injection for python

## Register 

Witch Doctor provides a method to register interfaces and his implementation. The interface and implementation inheritance will be check and will raise a TypeError if was some error.

```python
class WitchDoctor:
    @classmethod
    def register(cls, interface: Type[ABC], class_ref: Any):
        """
        WitchDoctor.register will check inherit of the interface and class_ref.
        Will raise a TypeError on validation error\n
        :param interface: Interface that inherits from ABC
        :param class_ref: A implementation of the interface
        """
        pass
```

## Injection 

Witch Doctor must be used as decorator. The function signature will ber check and if some values was not provide Witch Doctor will search on the registered interfaces to inject the dependencies.

```python
class WitchDoctor:
    @classmethod
    def injection(cls, function: Callable):
        """
        WitchDoctor.injection is a function decorator that will match the
        function params signature and inject the  dependencies.
        Will raise AttributeError is some args was pass throw\n

        :type function: Callable
        """
        pass
```

## Usage example

```python
from abc import ABC, abstractmethod

from witch_doctor import WitchDoctor

class IStubFromABCClass(ABC):
    @abstractmethod
    def sum(self, a: int, b: int):
        pass
    
class StubFromABCClass(IStubFromABCClass):
    def sum(self, a: int, b: int):
        return a + b
    
WitchDoctor.register(IStubFromABCClass, StubFromABCClass)

@WitchDoctor.injection
def func_t(a: int, b: int, c: IStubFromABCClass):
    return c.sum(a, b), c

result_a1, reference_a1 = func_t(a=1, b=2)
result_a2, reference_a2 = func_t(a=2, b=2)

assert result_a1 == 3
assert result_a2 == 4
assert reference_a1 == reference_a2
```