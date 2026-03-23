"""
Data models for the Record Management System

Defines three dataclasses — ClientRecord, AirlineRecord, and
FlightRecord — each providing serialisation helpers (to_dict /
from_dict) for round-tripping with the JSONL storage layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar


@dataclass
class ClientRecord:
    """Represent a single Client record.

    Attributes:
        id:             Unique numeric identifier for the client.
        name:           Full name of the client.
        address_line_1: First line of the postal address.
        address_line_2: Second line of the postal address.
        address_line_3: Third line of the postal address.
        city:           City of residence.
        state:          State or county.
        zip_code:       Postal or ZIP code.
        country:        Country of residence.
        phone_number:   Contact telephone number.
        type:           Record type tag, set automatically to "Client".
    """

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

    def __post_init__(self) -> None:
        """Initialise the ``type`` field to the class-level TYPE constant.

        Called automatically by the dataclass machinery immediately
        after ``__init__`` completes.
        """
        self.type = self.TYPE

    def to_dict(self) -> dict:
        """Return the record as a dict using canonical schema field names.

        Returns:
            A dictionary whose keys match the JSONL storage schema.
        """
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
        """Construct a ClientRecord from a canonical schema dictionary.

        Parameters:
            data: A dictionary whose keys match the JSONL storage schema.

        Returns:
            A fully initialised ClientRecord instance.
        """
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
    """Represent a single Airline record.

    Attributes:
        id:           Unique numeric identifier for the airline.
        company_name: Trading name of the airline company.
        type:         Record type tag, set automatically to "Airline".
    """

    TYPE: ClassVar[str] = "Airline"

    id: int
    company_name: str
    type: str = field(init=False)

    def __post_init__(self) -> None:
        """Initialise the ``type`` field to the class-level TYPE constant.

        Called automatically by the dataclass machinery immediately
        after ``__init__`` completes.
        """
        self.type = self.TYPE

    def to_dict(self) -> dict:
        """Return the record as a dict using canonical schema field names.

        Returns:
            A dictionary whose keys match the JSONL storage schema.
        """
        return {
            "ID": self.id,
            "Type": self.type,
            "Company Name": self.company_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AirlineRecord":
        """Construct an AirlineRecord from a canonical schema dictionary.

        Parameters:
            data: A dictionary whose keys match the JSONL storage schema.

        Returns:
            A fully initialised AirlineRecord instance.
        """
        return cls(
            id=data["ID"],
            company_name=data["Company Name"],
        )


@dataclass
class FlightRecord:
    """Represent a single Flight record.

    Attributes:
        client_id:  ID of the client who booked the flight.
        airline_id: ID of the airline operating the flight.
        date:       Departure date and time.
        start_city: Departure city.
        end_city:   Destination city.
        type:       Record type tag, set automatically to "Flight".
    """

    TYPE: ClassVar[str] = "Flight"

    client_id: int
    airline_id: int
    date: datetime
    start_city: str
    end_city: str
    type: str = field(init=False)

    def __post_init__(self) -> None:
        """Initialise the ``type`` field and coerce ``date`` to datetime.

        Sets ``type`` to the class-level TYPE constant. If ``date``
        was supplied as an ISO-8601 string, it is parsed into a
        ``datetime`` object so that downstream code can rely on a
        consistent type.
        """
        self.type = self.TYPE
        # Coerce a raw ISO-8601 string to a datetime instance if necessary
        if isinstance(self.date, str):
            self.date = datetime.fromisoformat(self.date)

    def to_dict(self) -> dict:
        """Return the record as a dict using canonical schema field names.

        Returns:
            A dictionary whose keys match the JSONL storage schema.
        """
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
        """Construct a FlightRecord from a canonical schema dictionary.

        Parameters:
            data: A dictionary whose keys match the JSONL storage schema.

        Returns:
            A fully initialised FlightRecord instance.
        """
        return cls(
            client_id=data["Client_ID"],
            airline_id=data["Airline_ID"],
            date=data["Date"],
            start_city=data["Start City"],
            end_city=data["End City"],
        )
