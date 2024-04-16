from pydantic import BaseModel
from typing import Any

# MODELS

class Flight(BaseModel):
    flight_num: str
    capacity: int
    estimated_flight_duration: int

class Airline(BaseModel):
    name: str
    flights: list[Flight]

# REQUESTS

class UpdateFlightRequest(BaseModel):
    capacity: int | None = None
    estimated_flight_duration: int | None = None


# RESPONSE DATA

class FlightData(BaseModel):
     airline_name: str
     flight_num: str
     capacity: int
     estimated_flight_duration: int

# RESPONSES

class FlightResponse(BaseModel):
    data: FlightData

class GetRequestResponse(BaseModel):
    data: Any