import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

from witch_doctor import WitchDoctor, InjectionType


class ICounter(ABC):
    @abstractmethod
    def get_value(self) -> int:
        pass


class Counter(ICounter):
    _instance_count = 0
    _lock = threading.Lock()

    def __init__(self):
        with Counter._lock:
            Counter._instance_count += 1
            self._value = Counter._instance_count

    def get_value(self) -> int:
        return self._value

    @classmethod
    def reset_count(cls):
        with cls._lock:
            cls._instance_count = 0


class TestConcurrentRegistration:
    def test_concurrent_container_creation(self):
        num_threads = 10

        def create_container(idx):
            container = WitchDoctor.container(f"container_{idx}")
            container(ICounter, Counter, InjectionType.FACTORY)
            return f"container_{idx}"

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_container, i) for i in range(num_threads)]
            results = [f.result() for f in as_completed(futures)]

        assert len(results) == num_threads
        for i in range(num_threads):
            assert f"container_{i}" in WitchDoctor._injection_map

    def test_concurrent_registration_same_container(self):
        class IService1(ABC):
            @abstractmethod
            def execute(self):
                pass

        class IService2(ABC):
            @abstractmethod
            def execute(self):
                pass

        class IService3(ABC):
            @abstractmethod
            def execute(self):
                pass

        class Service1(IService1):
            def execute(self):
                return 1

        class Service2(IService2):
            def execute(self):
                return 2

        class Service3(IService3):
            def execute(self):
                return 3

        interfaces = [
            (IService1, Service1),
            (IService2, Service2),
            (IService3, Service3),
        ]

        def register_service(pair):
            interface, impl = pair
            WitchDoctor.register(interface, impl, InjectionType.FACTORY)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(register_service, pair) for pair in interfaces]
            for f in as_completed(futures):
                f.result()

        WitchDoctor.load_container()
        assert WitchDoctor.resolve(IService1).execute() == 1
        assert WitchDoctor.resolve(IService2).execute() == 2
        assert WitchDoctor.resolve(IService3).execute() == 3


class TestConcurrentResolution:
    def test_concurrent_factory_resolution(self):
        Counter.reset_count()
        WitchDoctor.register(ICounter, Counter, InjectionType.FACTORY)
        WitchDoctor.load_container()

        num_threads = 50
        instances = []
        lock = threading.Lock()

        def resolve_counter():
            instance = WitchDoctor.resolve(ICounter)
            with lock:
                instances.append(instance)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(resolve_counter) for _ in range(num_threads)]
            for f in as_completed(futures):
                f.result()

        assert len(instances) == num_threads
        ids = [id(inst) for inst in instances]
        assert len(set(ids)) == num_threads

    def test_concurrent_singleton_resolution(self):
        Counter.reset_count()
        WitchDoctor.register(ICounter, Counter, InjectionType.SINGLETON)
        WitchDoctor.load_container()

        num_threads = 50
        instances = []
        lock = threading.Lock()

        def resolve_counter():
            instance = WitchDoctor.resolve(ICounter)
            with lock:
                instances.append(instance)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(resolve_counter) for _ in range(num_threads)]
            for f in as_completed(futures):
                f.result()

        assert len(instances) == num_threads
        ids = [id(inst) for inst in instances]
        assert len(set(ids)) == 1


class TestConcurrentInjection:
    def test_concurrent_injection(self):
        Counter.reset_count()
        WitchDoctor.register(ICounter, Counter, InjectionType.SINGLETON)
        WitchDoctor.load_container()

        @WitchDoctor.injection
        def get_counter_value(counter: ICounter) -> int:
            return counter.get_value()

        num_threads = 50
        results = []
        lock = threading.Lock()

        def call_injected():
            value = get_counter_value()
            with lock:
                results.append(value)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(call_injected) for _ in range(num_threads)]
            for f in as_completed(futures):
                f.result()

        assert len(results) == num_threads
        assert all(v == results[0] for v in results)


class TestConcurrentContainerSwitch:
    def test_container_switch_isolation(self):
        class ServiceA(ICounter):
            def get_value(self) -> int:
                return 1

        class ServiceB(ICounter):
            def get_value(self) -> int:
                return 2

        container_a = WitchDoctor.container("thread_container_a")
        container_a(ICounter, ServiceA, InjectionType.FACTORY)

        container_b = WitchDoctor.container("thread_container_b")
        container_b(ICounter, ServiceB, InjectionType.FACTORY)

        results_a = []
        results_b = []
        lock = threading.Lock()

        def use_container_a():
            WitchDoctor.load_container("thread_container_a")
            value = WitchDoctor.resolve(ICounter).get_value()
            with lock:
                results_a.append(value)

        def use_container_b():
            WitchDoctor.load_container("thread_container_b")
            value = WitchDoctor.resolve(ICounter).get_value()
            with lock:
                results_b.append(value)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(20):
                if i % 2 == 0:
                    futures.append(executor.submit(use_container_a))
                else:
                    futures.append(executor.submit(use_container_b))
            for f in as_completed(futures):
                f.result()

        assert len(results_a) == 10
        assert len(results_b) == 10


class TestSingletonThreadSafety:
    def test_singleton_constructed_exactly_once_under_concurrency(self):
        """Constructor must run exactly once even when many threads race to create it."""
        construction_count = 0
        count_lock = threading.Lock()

        class IExpensive(ABC):
            @abstractmethod
            def get_id(self) -> int:
                pass

        class ExpensiveService(IExpensive):
            def __init__(self):
                nonlocal construction_count
                time.sleep(0.05)  # slow constructor — forces thread overlap
                with count_lock:
                    construction_count += 1
                self._id = construction_count

            def get_id(self) -> int:
                return self._id

        WitchDoctor.register(IExpensive, ExpensiveService, InjectionType.SINGLETON)
        WitchDoctor.load_container()

        num_threads = 20
        instances = []
        lock = threading.Lock()

        def resolve():
            instance = WitchDoctor.resolve(IExpensive)
            with lock:
                instances.append(instance)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(resolve) for _ in range(num_threads)]
            for f in as_completed(futures):
                f.result()

        assert construction_count == 1
        assert len(set(id(i) for i in instances)) == 1
