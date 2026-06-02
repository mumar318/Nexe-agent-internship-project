# tools.py

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ➤ Tool 1: Add numbers
def add(a: float, b: float):
    return a + b

# ➤ Tool 2: Multiply numbers
def multiply(a: float, b: float):
    return a * b

# ➤ Tool 3: Real weather API
def get_weather(city: str):
    city = city.title()   # 👈 IMPORTANT FIX (Lahore not lahore)

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return f"❌ Error: {response.get('message', 'City not found')}"

    temp = response["main"]["temp"]
    desc = response["weather"][0]["description"]
    feels_like = response["main"]["feels_like"]
    humidity = response["main"]["humidity"]
    
    return f"🌤️ Weather in {city}:\n🌡️ Temperature: {temp}°C (feels like {feels_like}°C)\n☁️ Condition: {desc.capitalize()}\n💧 Humidity: {humidity}%"