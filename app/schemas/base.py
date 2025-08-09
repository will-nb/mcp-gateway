import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer


def to_camel(s: str) -> str:
    return re.sub(r"_([a-z])", lambda m: m.group(1).upper(), s)


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @field_serializer("*")
    def serialize_datetime(self, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class BaseSchema(CamelModel):
    pass
