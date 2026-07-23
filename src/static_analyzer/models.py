

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Severity(str, Enum):


    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Finding:


    rule_id: str
    message: str
    file_path: str
    line_number: int
    severity: Severity = Severity.WARNING
    column_number: int | None = None

    def to_dict(self) -> dict[str, Any]:


        data = asdict(self)
        data["severity"] = self.severity.value
        return data
