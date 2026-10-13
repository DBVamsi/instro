from instro2.lib.transport import MessageTransport


class FakeTransport(MessageTransport):
    def __init__(self, address: str) -> None:
        self.address = address

    def connect(self) -> None:
        print(f"connecting to {self.address}")

    def disconnect(self) -> None:
        print(f"disconnecting from {self.address}")

    def read(self) -> str:
        print(f"read something from {self.address}")
        return "0.0"

    def write(self, payload: str) -> None:
        print(f"writing {payload}")

    def query(self, payload: str) -> str:
        self.write(payload)
        return self.read()
