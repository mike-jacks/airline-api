"""
Have these endpoints:

GET / -> list[airline_name]
GET /:airline_name -> list[flight_num]
GET /:airline_name/:flight_num -> Flight

POST /:airline
PUT /:airline/:flight_num
DELETE /:airline/:flight_num

"""

import json
from fastapi import FastAPI, HTTPException, status

from models import Airline, Flight, UpdateFlightRequest, FlightResponse, FlightData, GetRequestResponse

with open("airlines.json", "r") as file:
    airlines_json: dict = json.load(file)

airlines: dict[str, Airline] = {}

for name, flights in airlines_json.items():
    flights = [Flight(flight_num=flight["flight_num"],
                      capacity=flight["capacity"],
                      estimated_flight_duration=flight["estimated_flight_duration"]
                      ) for flight in flights]
    airlines[name] = Airline(name=name, flights=flights)

app = FastAPI()

@app.get("/", response_model=list[str], status_code=status.HTTP_200_OK)
async def get_airline_names() -> list[str]:
    data = list(airlines.keys())
    return data

@app.get("/{airline_name}", response_model=list[str], status_code=status.HTTP_200_OK)
async def get_airline_flight_numbers(airline_name: str) -> list[str]:
    airline: list[Airline]= [airline for name, airline in airlines.items() if name == airline_name]
    if not airline:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{airline_name} not found.")
    else:
        airline: Airline = airline[0]
    data = [flight.flight_num for flight in airline.flights]
    return data

@app.get("/{airline_name}/{flight_num}", response_model=Flight)
async def get_airline_flight(airline_name: str, flight_num: str) -> Flight:
    airline: list[Flight] = [airline for name, airline in airlines.items() if name == airline_name]
    if not airline:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{airline_name} not found.")
    else:
        airline: Airline = airline.pop()
    flight: list[Flight] = [flight for flight in airline.flights if flight.flight_num == flight_num]
    if not flight:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{flight_num} not found.")
    else:
        flight: Flight = flight.pop()
    data = flight
    return data

@app.post("/{airline_name}", response_model=FlightResponse)
async def add_flight(airline_name: str, flight: Flight):
    if airline_name not in airlines:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{airline_name} airline not found.")
    if flight.flight_num in [flight.flight_num for flight in airlines[airline_name].flights]:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Flight {flight.flight_num} already exists for {airline_name} airline.")
    airlines[airline_name].flights.append(flight)
    flight_data = FlightData(**flight.model_dump(), airline_name=airline_name)
    return FlightResponse(data=flight_data)

@app.put("/{airline_name}/{flight_num}", response_model=FlightResponse)
async def update_flight(airline_name: str, flight_num: str, update_flight_request: UpdateFlightRequest) -> FlightResponse:
    for i, flight in enumerate(airlines[airline_name].flights):
        if flight.flight_num == flight_num:
            for attr, value in update_flight_request.model_dump().items():
                if value != None:
                    setattr(flight, attr, value)
            airlines[airline_name].flights[i] = flight
            update_flight_data = FlightData(**flight.model_dump(), airline_name=airline_name)
            return FlightResponse(data=update_flight_data)

@app.delete("/{airline_name}/{flight_num}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(airline_name: str, flight_num: str):
    for i, flight in enumerate(airlines[airline_name].flights):
        if flight.flight_num == flight_num:
            airlines[airline_name].flights.pop(i)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Flight {flight_num} not found.")
    