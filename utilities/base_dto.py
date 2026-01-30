from abc import ABC, abstractmethod
from typing import Any


class BaseDto(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseDto":
        pass
