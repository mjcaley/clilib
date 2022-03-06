from dataclasses import dataclass
from typing import Any


@dataclass
class Context:
    exit_code: int = 0
    obj: Any = None
