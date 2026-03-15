"""
Record sub-package for the Record Management System.

Re-exports the public CRUD functions for Client, Airline, and Flight
records so that callers can import them directly from ``src.record``
without referencing the individual sub-modules.
"""

from .client_record import (
    create_client,
    delete_client,
    update_client,
    search_clients,
)
from .airline_record import (
    create_airline,
    delete_airline,
    update_airline,
    search_airlines,
)
from .flight_record import (
    create_flight,
    delete_flight,
    update_flight,
    search_flights,
)

__all__ = [
    "create_client",
    "delete_client",
    "update_client",
    "search_clients",
    "create_airline",
    "delete_airline",
    "update_airline",
    "search_airlines",
    "create_flight",
    "delete_flight",
    "update_flight",
    "search_flights",
]
