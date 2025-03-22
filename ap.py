import requests
WEATHER_API_KEY = "97cfde7e6a47301badaf2d7cf0633a4d"
url = f"http://api.openweathermap.org/geo/1.0/direct?q={'London'}&appid={WEATHER_API_KEY}"
response = requests.get(url).json()
data = response
for city in data:
    name = city['name']
    lat = city['lat']
    lon = city['lon']
    print(f"City: {name}, Latitude: {lat}, Longitude: {lon}")
