from dataclasses import dataclass
from typing import Optional

@dataclass
class DBResult:
    success: bool
    error_message: Optional[str] = None
    data: Optional[list[dict]] = None
    row_count: Optional[int] = 0
