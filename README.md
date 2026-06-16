<img src="https://github.com/CenturyBoys/witch-doctor/blob/main/doc/logo.png" alt="drawing" style="width:400px;display: block;  margin-left: auto;margin-right: auto;"/>
By: CenturyBoys

# Witch-doctor

**A simple dependency injection library for Python**

## Register 

**Witch Doctor** provides a structured method to register interfaces, implementations, injection types, constructor arguments, and container scopes.

* It validates the inheritance relationship between the interface and implementation. If there’s a mismatch, a `TypeError` is raised.
* The injection type is also validated and must be either `"singleton"` or `"factory"`.

  * `"singleton"` returns the same instance on every injection.
  * `"factory"` creates a new instance for each injection.
    An invalid type will raise a `TypeError`.
* If no arguments are provided, the constructor will be called without parameters.
* The `container_name` allows you to isolate dependency registrations by scope, enabling multi-context injection.


```python
class WitchDoctor:
    @classmethod
    def register(
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

You can register your injections using containers. The method `container` will provide a container register with the same signature as the register without the container param. To use the created container you need to load it using `load_container`.
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
container(IStubFromABCClass, StubFromABCClass, InjectionType.SINGLETON)
WitchDoctor.load_container("prod")

```
## Injection 

Witch Doctor can be used as a decorator. The function signature will be checked and if some values were not provided, Witch Doctor will search the registered interfaces to inject the dependencies.

```python
class WitchDoctor:
    @classmethod
    def injection(cls, function: Callable):
        """
        WitchDoctor.injection is a function decorator that will match the
        function params signature and inject the  dependencies.
        Will raise AttributeError if some args were passed through\n

        :type function: Callable
        """
        pass
```

## Usage example

```python
from abc import ABC, abstractmethod

from witch_doctor import WitchDoctor, InjectionType


# Abstract class
class IStubFromABCClass(ABC):
    @abstractmethod
    def sum(self, a: int, b: int):
        pass

    
# Implementation
class StubFromABCClass(IStubFromABCClass):
    def __init__(self, a: int):
        self.a = a

    def sum(self, a: int, b: int):
        return a + b + self.a

# Usage
@WitchDoctor.injection
def func_t(a: int, b: int, c: IStubFromABCClass):
    return c.sum(a, b)

# Containers
container = WitchDoctor.container()
container(IStubFromABCClass, StubFromABCClass, InjectionType.FACTORY, args=[10])

container = WitchDoctor.container("prod")
container(IStubFromABCClass, StubFromABCClass, InjectionType.SINGLETON, args=[20])

# Loading and using
WitchDoctor.load_container()

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


## Resolve 

The `resolve` method is used to retrieve an instance of a class registered in Witch Doctor.
It validates the class signature and searches for the matching implementation based on the registered interfaces. Dependencies are automatically injected.

```python
class WitchDoctor:
    @classmethod
    def resolve(cls, interface: T, container_name: str = CURRENT) -> Type[T]:
        """
        WitchDoctor.resolve will return an instance of the registered class_ref interface.
        Will raise a TypeError if interface is not registered\n
        :param interface: A implementation of the interface
        :param container_name: You can specify the container name to be used by the resolve method
        """
        pass
```

## Usage example

```python
from abc import ABC, abstractmethod

from witch_doctor import WitchDoctor, InjectionType


# Abstract class
class IStubFromABCClass(ABC):
    @abstractmethod
    def sum(self, a: int, b: int):
        pass

    
# Implementation
class StubFromABCClass(IStubFromABCClass):
    def __init__(self, a: int):
        self.a = a

    def sum(self, a: int, b: int):
        return a + b + self.a

# Usage
@WitchDoctor.injection
def func_t(a: int, b: int, c: IStubFromABCClass):
    return c.sum(a, b)

# Containers
container = WitchDoctor.container()
container(IStubFromABCClass, StubFromABCClass, InjectionType.FACTORY, args=[10])

# Loading and using
WitchDoctor.load_container()

result_a1 = WitchDoctor.resolve(IStubFromABCClass)
result_a2 = WitchDoctor.resolve(IStubFromABCClass)


```