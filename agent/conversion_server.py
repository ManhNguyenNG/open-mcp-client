#!/usr/bin/env python3
"""
MCP Server for Unit Conversions
Provides tools for temperature, currency, and other unit conversions.
"""

from mcp.server.fastmcp import FastMCP
import math

mcp = FastMCP("Conversion")

@mcp.tool()
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

@mcp.tool()
def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius"""
    return (fahrenheit - 32) * 5/9

@mcp.tool()
def celsius_to_kelvin(celsius: float) -> float:
    """Convert Celsius to Kelvin"""
    return celsius + 273.15

@mcp.tool()
def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin to Celsius"""
    return kelvin - 273.15

@mcp.tool()
def meters_to_feet(meters: float) -> float:
    """Convert meters to feet"""
    return meters * 3.28084

@mcp.tool()
def feet_to_meters(feet: float) -> float:
    """Convert feet to meters"""
    return feet / 3.28084

@mcp.tool()
def kilometers_to_miles(kilometers: float) -> float:
    """Convert kilometers to miles"""
    return kilometers * 0.621371

@mcp.tool()
def miles_to_kilometers(miles: float) -> float:
    """Convert miles to kilometers"""
    return miles / 0.621371

@mcp.tool()
def kilograms_to_pounds(kilograms: float) -> float:
    """Convert kilograms to pounds"""
    return kilograms * 2.20462

@mcp.tool()
def pounds_to_kilograms(pounds: float) -> float:
    """Convert pounds to kilograms"""
    return pounds / 2.20462

@mcp.tool()
def liters_to_gallons(liters: float) -> float:
    """Convert liters to US gallons"""
    return liters * 0.264172

@mcp.tool()
def gallons_to_liters(gallons: float) -> float:
    """Convert US gallons to liters"""
    return gallons / 0.264172

@mcp.tool()
def euros_to_dollars(euros: float) -> float:
    """Convert Euros to US Dollars (approximate rate: 1 EUR = 1.08 USD)"""
    return euros * 1.08

@mcp.tool()
def dollars_to_euros(dollars: float) -> float:
    """Convert US Dollars to Euros (approximate rate: 1 USD = 0.93 EUR)"""
    return dollars * 0.93

@mcp.tool()
def celsius_to_fahrenheit_with_description(celsius: float) -> str:
    """Convert Celsius to Fahrenheit with a descriptive response"""
    fahrenheit = (celsius * 9/5) + 32
    return f"{celsius}°C = {fahrenheit:.1f}°F"

@mcp.tool()
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between different units (Celsius, Fahrenheit, Kelvin)"""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # First convert to Celsius
    if from_unit in ['c', 'celsius', '°c']:
        celsius = value
    elif from_unit in ['f', 'fahrenheit', '°f']:
        celsius = (value - 32) * 5/9
    elif from_unit in ['k', 'kelvin', '°k']:
        celsius = value - 273.15
    else:
        return f"Unknown temperature unit: {from_unit}"
    
    # Then convert from Celsius to target unit
    if to_unit in ['c', 'celsius', '°c']:
        result = celsius
        unit = "°C"
    elif to_unit in ['f', 'fahrenheit', '°f']:
        result = (celsius * 9/5) + 32
        unit = "°F"
    elif to_unit in ['k', 'kelvin', '°k']:
        result = celsius + 273.15
        unit = "K"
    else:
        return f"Unknown temperature unit: {to_unit}"
    
    return f"{value} {from_unit} = {result:.1f} {unit}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
