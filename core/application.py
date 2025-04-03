from abc import ABC, abstractmethod
from typing import Any
class Application(ABC):

    @abstractmethod
    def start(self) -> Any:
        """Starts the application and return native app object."""
        pass

