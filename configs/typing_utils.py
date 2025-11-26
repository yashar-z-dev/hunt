from dataclasses import dataclass
from typing import List, Callable, Optional

@dataclass
class Command:
    keywords: List[str]
    method: Callable[..., Optional[str]]