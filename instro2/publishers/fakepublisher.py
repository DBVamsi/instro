from instro.lib.types import Command, Measurement


class FakePublisher:
    def __init__(self) -> None:
        self.published: list[Measurement | Command] = []
        self.closed = False

    def publish(self, data: Measurement | Command) -> None:
        print(f"publishing {data}")
        self.published.append(data)

    def close(self) -> None:
        print("closing publisher")
        self.closed = True
