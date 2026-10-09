from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name
        self.last_status: str = "Initialized"
        self.last_updated: Optional[str] = None

    @abstractmethod
    def health_check(self) -> bool:
        pass
