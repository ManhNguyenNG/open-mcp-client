#!/usr/bin/env python3
"""
MCP Server for Scientific Calculations
Provides tools for advanced mathematical and scientific operations.
"""

from mcp.server.fastmcp import FastMCP
import math
import random

mcp = FastMCP("Scientific")

@mcp.tool()
def square_root(number: float) -> float:
    """Calculate the square root of a number"""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(number)

@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Calculate base raised to the power of exponent"""
    return math.pow(base, exponent)

@mcp.tool()
def factorial(n: int) -> int:
    """Calculate the factorial of a number"""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return math.factorial(n)

@mcp.tool()
def logarithm(number: float, base: float = 10) -> float:
    """Calculate logarithm of a number with specified base (default: 10)"""
    if number <= 0 or base <= 0:
        raise ValueError("Logarithm is not defined for non-positive numbers")
    return math.log(number, base)

@mcp.tool()
def natural_logarithm(number: float) -> float:
    """Calculate natural logarithm (ln) of a number"""
    if number <= 0:
        raise ValueError("Natural logarithm is not defined for non-positive numbers")
    return math.log(number)

@mcp.tool()
def sine(angle_degrees: float) -> float:
    """Calculate sine of an angle in degrees"""
    return math.sin(math.radians(angle_degrees))

@mcp.tool()
def cosine(angle_degrees: float) -> float:
    """Calculate cosine of an angle in degrees"""
    return math.cos(math.radians(angle_degrees))

@mcp.tool()
def tangent(angle_degrees: float) -> float:
    """Calculate tangent of an angle in degrees"""
    return math.tan(math.radians(angle_degrees))

@mcp.tool()
def arcsin(value: float) -> float:
    """Calculate arcsine (inverse sine) in degrees"""
    if value < -1 or value > 1:
        raise ValueError("Arcsine is only defined for values between -1 and 1")
    return math.degrees(math.asin(value))

@mcp.tool()
def arccos(value: float) -> float:
    """Calculate arccosine (inverse cosine) in degrees"""
    if value < -1 or value > 1:
        raise ValueError("Arccosine is only defined for values between -1 and 1")
    return math.degrees(math.acos(value))

@mcp.tool()
def arctan(value: float) -> float:
    """Calculate arctangent (inverse tangent) in degrees"""
    return math.degrees(math.atan(value))

@mcp.tool()
def absolute_value(number: float) -> float:
    """Calculate the absolute value of a number"""
    return abs(number)

@mcp.tool()
def round_number(number: float, decimals: int = 0) -> float:
    """Round a number to specified number of decimal places"""
    return round(number, decimals)

@mcp.tool()
def floor(number: float) -> int:
    """Calculate the floor (greatest integer less than or equal to) of a number"""
    return math.floor(number)

@mcp.tool()
def ceiling(number: float) -> int:
    """Calculate the ceiling (smallest integer greater than or equal to) of a number"""
    return math.ceil(number)

@mcp.tool()
def random_number(min_value: float, max_value: float) -> float:
    """Generate a random number between min_value and max_value"""
    return random.uniform(min_value, max_value)

@mcp.tool()
def random_integer(min_value: int, max_value: int) -> int:
    """Generate a random integer between min_value and max_value (inclusive)"""
    return random.randint(min_value, max_value)

@mcp.tool()
def calculate_percentage(part: float, total: float) -> float:
    """Calculate what percentage part is of total"""
    if total == 0:
        raise ValueError("Total cannot be zero")
    return (part / total) * 100

@mcp.tool()
def percentage_of(percentage: float, total: float) -> float:
    """Calculate what amount is percentage% of total"""
    return (percentage / 100) * total

@mcp.tool()
def compound_interest(principal: float, rate: float, time: float, compounds_per_year: int = 1) -> float:
    """Calculate compound interest: A = P(1 + r/n)^(nt)"""
    if rate < 0 or time < 0 or compounds_per_year <= 0:
        raise ValueError("Rate, time, and compounds_per_year must be positive")
    return principal * math.pow(1 + rate / compounds_per_year, compounds_per_year * time)

@mcp.tool()
def simple_interest(principal: float, rate: float, time: float) -> float:
    """Calculate simple interest: I = P * r * t"""
    if rate < 0 or time < 0:
        raise ValueError("Rate and time must be positive")
    return principal * rate * time

@mcp.tool()
def calculate_area_circle(radius: float) -> float:
    """Calculate the area of a circle: A = πr²"""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius * radius

@mcp.tool()
def calculate_circumference_circle(radius: float) -> float:
    """Calculate the circumference of a circle: C = 2πr"""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return 2 * math.pi * radius

@mcp.tool()
def calculate_volume_sphere(radius: float) -> float:
    """Calculate the volume of a sphere: V = (4/3)πr³"""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return (4/3) * math.pi * math.pow(radius, 3)

@mcp.tool()
def calculate_surface_area_sphere(radius: float) -> float:
    """Calculate the surface area of a sphere: A = 4πr²"""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return 4 * math.pi * radius * radius

@mcp.tool()
def solve_quadratic_equation(a: float, b: float, c: float) -> str:
    """Solve quadratic equation ax² + bx + c = 0"""
    if a == 0:
        return "This is not a quadratic equation (a = 0)"
    
    discriminant = b*b - 4*a*c
    
    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        return f"Two real solutions: x₁ = {x1:.3f}, x₂ = {x2:.3f}"
    elif discriminant == 0:
        x = -b / (2*a)
        return f"One real solution: x = {x:.3f}"
    else:
        real_part = -b / (2*a)
        imaginary_part = math.sqrt(-discriminant) / (2*a)
        return f"Two complex solutions: x₁ = {real_part:.3f} + {imaginary_part:.3f}i, x₂ = {real_part:.3f} - {imaginary_part:.3f}i"

if __name__ == "__main__":
    mcp.run(transport="stdio")
