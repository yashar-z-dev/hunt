from dataclasses import dataclass
from typing import List, Optional, Protocol

class CommandMethod(Protocol):
    def __call__(self, id: int, chat_id: int, timestamp: str, flags: str, text: str) -> Optional[str]: ...

@dataclass
class Command:
    keywords: List[str]
    method: CommandMethod