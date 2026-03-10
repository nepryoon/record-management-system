from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import ClassVar


@dataclass
class ClientRecord:
    TYPE: ClassVar[str] = "client"

    id: int
    name: str
    address_line_1: str
    address_line_2: str
    address_line_3: str
    city: str
    state: str
    zip_code: str
    country: str
    phone_number: str
    type: str = field(init=False)

    def __post_init__(self):
        self.type = self.TYPE

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ClientRecord":
        d = {k: v for k, v in data.items() if k != "type"}
        return cls(**d)


@dataclass
class AirlineRecord:
    TYPE: ClassVar[str] = "airline"

    id: int
    company_name: str
    type: str = field(init=False)

    def __post_init__(self):
        self.type = self.TYPE

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AirlineRecord":
        d = {k: v for k, v in data.items() if k != "type"}
        return cls(**d)


@dataclass
class FlightRecord:
    TYPE: ClassVar[str] = "flight"

    client_id: int
    airline_id: int
    date: datetime
    start_city: str
    end_city: str
    type: str = field(init=False)

    def __post_init__(self):
        self.type = self.TYPE
        if isinstance(self.date, str):
            self.date = datetime.fromisoformat(self.date)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["date"] = self.date.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "FlightRecord":
        d = {k: v for k, v in data.items() if k != "type"}
        return cls(**d)
