<img src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2Foriginals%2Fe6%2Fff%2F86%2Fe6ff86db1ad224c37d328579786e13f3.jpg&f=1&nofb=1&ipt=448de94a888dd920ca7383f804f09f69d49ad4d226d9bee06115bbc9b188e1d2&ipo=images" alt="drawing" style="width:400px;display: block;  margin-left: auto;margin-right: auto;"/>
By: CenturyBoys

# Witch-doctor

A simple dependency injection for python

## Register 

Witch Doctor provides a method to register interfaces, implementation, injection type, instance args and container name. 

- The interface and implementation inheritance will be checked and will raise a TypeError if was some issue.
- The injection type will be checked and will raise a TypeError if was some issue. There are two types the singleton and factory types, the singleton will return the same instance for all injection and the factory will return a new instance for each injection.
- If no values was giving will not pass the args to the class constructor.
- The container name will segregate the injections by scopes.

```python
class WitchDoctor:
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
        :param injection_type: The injection type that must be used for this register. Allowed Factory or Singleton
        :param args: List of args tha will be used to instantiate the class object
        :param container: Container name where the reference will be saved.
        """
        pass
```

## Container

You can register your injections using containers. The method `contianer` will provide a container register with the same signature as teh register without the container param. To use the created container you need to load it using `load_container`.
The base work load will set all registers in the DEFAULT group

```python
from abc import ABC, abstractmethod

from witch_doctor import WitchDoctor, InjectionType

class IStubFromABCClass(ABC):
    @abstractmethod
    def sum(self, a: int, b: int):
        pass
    
class StubFromABCClass(IStubFromABCClass):
    def sum(self, a: int, b: int):
        return a + b

container = WitchDoctor.container("prod")
WitchDoctor.register(IStubFromABCClass, StubFromABCClass, InjectionType.SINGLETON)   
WitchDoctor.load_container("prod")

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

from witch_doctor import WitchDoctor, InjectionType

class IStubFromABCClass(ABC):
    @abstractmethod
    def sum(self, a: int, b: int):
        pass
    
class StubFromABCClass(IStubFromABCClass):
    def __init__(self, a: int):
        self.a = a

    def sum(self, a: int, b: int):
        return a + b + self.a
    
container = WitchDoctor.container("prod")
container(IStubFromABCClass, StubFromABCClass, InjectionType.SINGLETON, args=[20])
container = WitchDoctor.container()
container(IStubFromABCClass, StubFromABCClass, InjectionType.FACTORY, args=[10])


@WitchDoctor.injection
def func_t(a: int, b: int, c: IStubFromABCClass):
    return c.sum(a, b), c

result_a1 = func_t(a=1, b=2)
result_a2 = func_t(a=2, b=2)

assert result_a1 == 13
assert result_a2 == 14

WitchDoctor.load_container("prod")

result_a1 = func_t(a=1, b=2)
result_a2 = func_t(a=2, b=2)

assert result_a1 == 23
assert result_a2 == 24
```