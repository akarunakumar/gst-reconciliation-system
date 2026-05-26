from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AgentResult:
    success: bool
    data: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def run(self, context: dict) -> AgentResult: ...
