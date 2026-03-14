from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar


@dataclass
class ClientRecord:
    """Dataclass representing a Client record."""

    TYPE: ClassVar[str] = "Client"

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
        """Return the record as a dictionary using the canonical schema field names."""
        return {
            "ID": self.id,
            "Type": self.type,
            "Name": self.name,
            "Address Line 1": self.address_line_1,
            "Address Line 2": self.address_line_2,
            "Address Line 3": self.address_line_3,
            "City": self.city,
            "State": self.state,
            "Zip Code": self.zip_code,
            "Country": self.country,
            "Phone Number": self.phone_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClientRecord":
        """Construct a ClientRecord from a canonical schema dictionary."""
        return cls(
            id=data["ID"],
            name=data["Name"],
            address_line_1=data["Address Line 1"],
            address_line_2=data["Address Line 2"],
            address_line_3=data["Address Line 3"],
            city=data["City"],
            state=data["State"],
            zip_code=data["Zip Code"],
            country=data["Country"],
            phone_number=data["Phone Number"],
        )


@dataclass
class AirlineRecord:
    """Dataclass representing an Airline record."""

    TYPE: ClassVar[str] = "Airline"

    id: int
    company_name: str
    type: str = field(init=False)

    def __post_init__(self):
        self.type = self.TYPE

    def to_dict(self) -> dict:
        """Return the record as a dictionary using the canonical schema field names."""
        return {
            "ID": self.id,
            "Type": self.type,
            "Company Name": self.company_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AirlineRecord":
        """Construct an AirlineRecord from a canonical schema dictionary."""
        return cls(
            id=data["ID"],
            company_name=data["Company Name"],
        )


@dataclass
class FlightRecord:
    """Dataclass representing a Flight record."""

    TYPE: ClassVar[str] = "Flight"

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
        """Return the record as a dictionary using the canonical schema field names."""
        return {
            "Type": self.type,
            "Client_ID": self.client_id,
            "Airline_ID": self.airline_id,
            "Date": self.date.isoformat(),
            "Start City": self.start_city,
            "End City": self.end_city,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FlightRecord":
        """Construct a FlightRecord from a canonical schema dictionary."""
        return cls(
            client_id=data["Client_ID"],
            airline_id=data["Airline_ID"],
            date=data["Date"],
            start_city=data["Start City"],
            end_city=data["End City"],
        )
