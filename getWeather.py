import json
import requests

def getWeather():
    with open(".weatherStationData.json") as dataFile:
        stationData = json.load(dataFile)
        
    stationCurrentWeather = requests.get(stationData["dataRequestEndPoint"])
    stationCurrentWeatherJson = stationCurrentWeather.json()["obs"][0]
    # print(json.dumps(stationCurrentWeatherJson, indent=4))
    
    currentWeatherJson = {}
    currentWeatherJson["windDirection"] =  degrees2cardinal(stationCurrentWeatherJson["wind_direction"])
    currentWeatherJson["windSpeed"] = round(stationCurrentWeatherJson["wind_avg"] * 2.23694, 1)
    currentWeatherJson["temperature"] =  round((stationCurrentWeatherJson["air_temperature"] * 9/5) + 32, 0)
    currentWeatherJson["precToday"] = round(stationCurrentWeatherJson["precip_accum_local_day"] / 25.4, 1)
    currentWeatherJson["uv"] = round(stationCurrentWeatherJson["uv"], 1)
    currentWeatherJson["feelsLike"] =  round((stationCurrentWeatherJson["feels_like"] * 9/5) + 32, 0)
    return(currentWeatherJson)

def degrees2cardinal(degrees):
    """
    Converts wind direction in degrees to cardinal direction.
    Assumes 0 degrees is North and increases clockwise.
    """
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    
    # Calculate the size of each sector
    sector_size = 360 / len(directions)
    
    # Adjust degrees to center sectors around their cardinal direction
    # and handle values > 360
    adjusted_degrees = (degrees + sector_size / 2) % 360
    
    # Calculate the index for the directions list
    index = int(adjusted_degrees / sector_size)
    
    return directions[index]



if __name__ == "__main__":
    weatherReport = getWeather()
    print(json.dumps(weatherReport, indent=4))
