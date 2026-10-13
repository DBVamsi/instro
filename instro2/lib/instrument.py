import functools
import inspect
import time
from collections.abc import Callable
from typing import Any, TypeVar

from instro.lib.types import Command, Measurement
from instro2.lib.publisher import Publisher
from instro2.lib.transport import Transport

F = TypeVar("F", bound=Callable[..., Any])


def measures(template: str) -> Callable[[F], F]:
    def mark(method: F) -> F:
        setattr(method, "publish_spec", (template, None))
        return method

    return mark


def commands(template: str, value: str) -> Callable[[F], F]:
    def mark(method: F) -> F:
        setattr(method, "publish_spec", (template, value))
        return method

    return mark


def publishing(method: Callable, template: str, value: str | None) -> Callable:
    signature = inspect.signature(method)

    @functools.wraps(method)
    def wrapper(self: "Instrument", *args: Any, **kwargs: Any) -> Any:
        result = method(self, *args, **kwargs)
        arguments = signature.bind(self, *args, **kwargs).arguments
        channel = f"{self.name}.{template.format(**arguments)}"
        if value is None:
            self.publish(Measurement({channel: [result]}, [time.time_ns()]))
        else:
            self.publish(Command({channel: arguments[value]}, time.time_ns()))
        return result

    return wrapper


class Instrument:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for name, method in list(vars(cls).items()):
            for base in cls.__mro__[1:]:
                spec = getattr(vars(base).get(name), "publish_spec", None)
                if spec:
                    setattr(cls, name, publishing(method, *spec))
                    break

    def __init__(
        self,
        name: str,
        transport: Transport,
        publishers: list[Publisher] | None = None,
        tags: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.transport = transport
        self.publishers = publishers or []
        self.tags = tags or {}

    def connect(self) -> None:
        self.transport.connect()

    def disconnect(self) -> None:
        self.transport.disconnect()

    def add_publisher(self, publisher: Publisher) -> None:
        self.publishers.append(publisher)

    def publish(self, data: Measurement | Command) -> None:
        data.tags = {**self.tags, **(data.tags or {})}
        for publisher in self.publishers:
            publisher.publish(data)
