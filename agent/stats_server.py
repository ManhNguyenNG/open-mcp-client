#!/usr/bin/env python3
"""
MCP Server for Statistical Calculations
Provides tools for basic and advanced statistical operations.
"""

from mcp.server.fastmcp import FastMCP
import statistics
import math

mcp = FastMCP("Statistics")

@mcp.tool()
def mean(numbers: list) -> float:
    """Calculate the arithmetic mean (average) of a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate mean of empty list")
    return statistics.mean(numbers)

@mcp.tool()
def median(numbers: list) -> float:
    """Calculate the median of a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate median of empty list")
    return statistics.median(numbers)

@mcp.tool()
def mode(numbers: list) -> list:
    """Calculate the mode(s) of a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate mode of empty list")
    return statistics.multimode(numbers)

@mcp.tool()
def standard_deviation(numbers: list) -> float:
    """Calculate the standard deviation of a list of numbers"""
    if len(numbers) < 2:
        raise ValueError("Need at least 2 numbers to calculate standard deviation")
    return statistics.stdev(numbers)

@mcp.tool()
def variance(numbers: list) -> float:
    """Calculate the variance of a list of numbers"""
    if len(numbers) < 2:
        raise ValueError("Need at least 2 numbers to calculate variance")
    return statistics.variance(numbers)

@mcp.tool()
def population_standard_deviation(numbers: list) -> float:
    """Calculate the population standard deviation of a list of numbers"""
    if len(numbers) < 2:
        raise ValueError("Need at least 2 numbers to calculate population standard deviation")
    return statistics.pstdev(numbers)

@mcp.tool()
def population_variance(numbers: list) -> float:
    """Calculate the population variance of a list of numbers"""
    if len(numbers) < 2:
        raise ValueError("Need at least 2 numbers to calculate population variance")
    return statistics.pvariance(numbers)

@mcp.tool()
def minimum(numbers: list) -> float:
    """Find the minimum value in a list of numbers"""
    if not numbers:
        raise ValueError("Cannot find minimum of empty list")
    return min(numbers)

@mcp.tool()
def maximum(numbers: list) -> float:
    """Find the maximum value in a list of numbers"""
    if not numbers:
        raise ValueError("Cannot find maximum of empty list")
    return max(numbers)

@mcp.tool()
def range_calculation(numbers: list) -> float:
    """Calculate the range (max - min) of a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate range of empty list")
    return max(numbers) - min(numbers)

@mcp.tool()
def sum_numbers(numbers: list) -> float:
    """Calculate the sum of a list of numbers"""
    return sum(numbers)

@mcp.tool()
def count_numbers(numbers: list) -> int:
    """Count the number of items in a list"""
    return len(numbers)

@mcp.tool()
def quartiles(numbers: list) -> dict:
    """Calculate the quartiles (Q1, Q2, Q3) of a list of numbers"""
    if len(numbers) < 4:
        raise ValueError("Need at least 4 numbers to calculate quartiles")
    
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    
    # Q1 (25th percentile)
    q1_index = (n - 1) * 0.25
    q1 = sorted_numbers[int(q1_index)] + (sorted_numbers[int(q1_index) + 1] - sorted_numbers[int(q1_index)]) * (q1_index - int(q1_index))
    
    # Q2 (median, 50th percentile)
    q2 = statistics.median(sorted_numbers)
    
    # Q3 (75th percentile)
    q3_index = (n - 1) * 0.75
    q3 = sorted_numbers[int(q3_index)] + (sorted_numbers[int(q3_index) + 1] - sorted_numbers[int(q3_index)]) * (q3_index - int(q3_index))
    
    return {
        "Q1": round(q1, 3),
        "Q2": round(q2, 3),
        "Q3": round(q3, 3),
        "IQR": round(q3 - q1, 3)  # Interquartile Range
    }

@mcp.tool()
def correlation_coefficient(x_values: list, y_values: list) -> float:
    """Calculate the Pearson correlation coefficient between two lists of numbers"""
    if len(x_values) != len(y_values):
        raise ValueError("Lists must have the same length")
    if len(x_values) < 2:
        raise ValueError("Need at least 2 data points to calculate correlation")
    
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    sum_y2 = sum(y * y for y in y_values)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
    
    if denominator == 0:
        return 0
    
    return numerator / denominator

@mcp.tool()
def linear_regression(x_values: list, y_values: list) -> dict:
    """Calculate linear regression (y = mx + b) for two lists of numbers"""
    if len(x_values) != len(y_values):
        raise ValueError("Lists must have the same length")
    if len(x_values) < 2:
        raise ValueError("Need at least 2 data points for linear regression")
    
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    
    # Calculate slope (m)
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    
    # Calculate y-intercept (b)
    y_intercept = (sum_y - slope * sum_x) / n
    
    return {
        "slope": round(slope, 4),
        "y_intercept": round(y_intercept, 4),
        "equation": f"y = {slope:.4f}x + {y_intercept:.4f}"
    }

@mcp.tool()
def z_score(value: float, mean: float, standard_deviation: float) -> float:
    """Calculate the z-score of a value given mean and standard deviation"""
    if standard_deviation == 0:
        raise ValueError("Standard deviation cannot be zero")
    return (value - mean) / standard_deviation

@mcp.tool()
def percentile_rank(value: float, numbers: list) -> float:
    """Calculate the percentile rank of a value in a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate percentile rank of empty list")
    
    sorted_numbers = sorted(numbers)
    count_below = sum(1 for x in sorted_numbers if x < value)
    count_equal = sum(1 for x in sorted_numbers if x == value)
    
    return (count_below + 0.5 * count_equal) / len(sorted_numbers) * 100

@mcp.tool()
def descriptive_statistics(numbers: list) -> dict:
    """Calculate comprehensive descriptive statistics for a list of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate statistics of empty list")
    
    stats = {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "mode": statistics.multimode(numbers),
        "minimum": min(numbers),
        "maximum": max(numbers),
        "range": max(numbers) - min(numbers)
    }
    
    if len(numbers) >= 2:
        stats.update({
            "variance": statistics.variance(numbers),
            "standard_deviation": statistics.stdev(numbers),
            "population_variance": statistics.pvariance(numbers),
            "population_standard_deviation": statistics.pstdev(numbers)
        })
    
    if len(numbers) >= 4:
        stats["quartiles"] = quartiles(numbers)
    
    # Round numeric values
    for key, value in stats.items():
        if isinstance(value, (int, float)) and key != "count":
            stats[key] = round(value, 4)
    
    return stats

if __name__ == "__main__":
    mcp.run(transport="stdio")
