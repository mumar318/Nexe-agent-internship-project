# tools.py

import math

# In-session memory store
_memory_store: dict = {"value": None}


# ➤ Tool 1: Add
def add(a: float, b: float) -> float:
    return a + b


# ➤ Tool 2: Subtract
def subtract(a: float, b: float) -> float:
    return a - b


# ➤ Tool 3: Multiply
def multiply(a: float, b: float) -> float:
    return a * b


# ➤ Tool 4: Divide
def divide(a: float, b: float):
    if b == 0:
        return "❌ Error: Division by zero is not allowed."
    return a / b


# ➤ Tool 5: Power
def power(base: float, exponent: float) -> float:
    return math.pow(base, exponent)


# ➤ Tool 6: Square Root
def square_root(a: float):
    if a < 0:
        return "❌ Error: Cannot take square root of a negative number."
    return math.sqrt(a)


# ➤ Tool 7: Store result in memory
def store_memory(value: float) -> str:
    _memory_store["value"] = value
    return f"✅ Value {value} saved to memory."


# ➤ Tool 8: Recall result from memory
def recall_memory() -> str:
    if _memory_store["value"] is None:
        return "⚠️ No value stored in memory yet."
    return _memory_store["value"]
