"""Backend de preferencias en memoria para pruebas sin escrituras al perfil."""


class MemorySettings:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def value(self, key: str, default=None):
        return self.values.get(key, default)

    def setValue(self, key: str, value) -> None:
        self.values[key] = value

    def sync(self) -> None:
        pass
