import datetime
import requests
from google.adk.agents import Agent

# Get weather for any city using OpenWeatherMap
def get_weather(city: str) -> dict:
    api_key = "5339d80f5b7e56ad14873d0d9ccfbafe"  # <-- Put your API key here
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    r = requests.get(url, params=params).json()
    if r.get("cod") != 200:
        return {"status": "error", "error_message": f"No weather for {city}."}
    desc = r["weather"][0]["description"]
    temp = r["main"]["temp"]
    return {"status": "success", "report": f"Weather in {city}: {desc}, {temp}°C."}

# Get time for any city using geopy and timezonefinder
def get_current_time(city: str) -> dict:
    try:
        from timezonefinder import TimezoneFinder
        from geopy.geocoders import Nominatim
        import pytz
    except ImportError:
        return {"status": "error", "error_message": "Install geopy, timezonefinder, pytz."}
    loc = Nominatim(user_agent="city_time").geocode(city)
    if not loc:
        return {"status": "error", "error_message": f"No location for {city}."}
    tz = TimezoneFinder().timezone_at(lng=loc.longitude, lat=loc.latitude)
    if not tz:
        return {"status": "error", "error_message": f"No timezone for {city}."}
    now = datetime.datetime.now(pytz.timezone(tz))
    return {"status": "success", "report": f"Time in {city}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"}

# Agent setup
agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description="Answers weather and time questions for any city.",
    instruction="Answer in simple Shakespearean English.",
    tools=[get_weather, get_current_time],
)

# Simple runner
import sys, asyncio
async def main():
    if len(sys.argv) < 2:
        print("Usage: python test_agent.py 'Your question'"); return
    q = " ".join(sys.argv[1:])
    try:
        async for r in agent.run_live(q):
            print(r)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main()) 