from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Language:
    name: str
    code: str
    active: bool = field(default=True)
    offset: int = field(default=None)
    service_name: str = field(default=None)
    service: object = field(init=False, repr=False)


@dataclass_json
@dataclass
class LanguagesConfig:
    langs: list[Language]
