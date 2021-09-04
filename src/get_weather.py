import yaml
import requests
import json
from datetime import datetime, timedelta
import os

city_name = "Zurich, Switzerland"
url = "http://dataservice.accuweather.com"
cache_folder = "./cache"


def getJSONfromUrl(url):
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data


def retrieve_api_key():
    with open('./password.yml') as stream:
        config = yaml.safe_load(stream)
        api_key = config['accuweather']['api_key']
        return api_key


def get_cache(filename):
    # Load json from file if exist
    folder_path = os.path.abspath(cache_folder)
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        with open(file_path) as stream:
            cache = json.load(stream)
        return cache
    else:
        print("Cache file does not exist: %s" % (file_path))
        return None


def save_cache(filename, cache):
    # Create folder if it doesn exist
    folder_path = os.path.abspath(cache_folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Write json to file
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'w') as stream:
        json.dump(cache, stream, indent=2)
    print("Cache saved to %s" % (file_path))


def retrieve_location_key(api_key):
    """Location key is how Accuweather reference a location."""
    cache_filename = "location_key.json"
    cache_expiry = timedelta(days = 2)

    cache = get_cache(cache_filename)
    if cache is None or datetime.fromisoformat(cache['retrival_time']) - datetime.now() > cache_expiry:
        # Retrive new location key
        request = "/locations/v1/cities/search?apikey=" + api_key + "&q=" + city_name
        json_data = getJSONfromUrl(url + request)
        key = json_data[0]['Key']

        cache = {
            'key': key,
            'retrival_time': datetime.now().isoformat(),
        }
        save_cache(cache_filename, cache)
        return key
    else:
        print("Location Key loaded from cache: %s" % cache_filename)
        key = cache['key']
        return key


def retrieve_weather_12h_forecast(api_key, location_key):
    cache_filename = "weather_12h_forecast.json"
    cache_expiry = timedelta(minutes=57)

    cache = get_cache(cache_filename)
    if cache is None or datetime.fromisoformat(cache['retrival_time']) - datetime.now() > cache_expiry:
        # Retrive new weather
        request = "/forecasts/v1/hourly/12hour/" + location_key + "?apikey=" + api_key + "&metric=true"
        weather = getJSONfromUrl(url + request)
        print("New weather_12h_forecast retrived")

        # Weather is encapsulated in a dictionary and saved
        cache = {
            'weather': weather,
            'retrival_time': datetime.now().isoformat(),
        }
        save_cache(cache_filename, cache)
        return weather
    else:
        print("Loaded from cache: %s" % cache_filename)
        weather = cache['weather']
        return weather


def retrieve_weather_5d_forecast(api_key, location_key):
    cache_filename = "weather_5d_forecast.json"
    cache_expiry = timedelta(hours=5, minutes=57)

    cache = get_cache(cache_filename)
    if cache is None or datetime.fromisoformat(cache['retrival_time']) - datetime.now() > cache_expiry:
        # Retrive new weather
        request = "/forecasts/v1/daily/5day/" + location_key + "?apikey=" + api_key + "&details=true&metric=true"
        weather = getJSONfromUrl(url + request)
        print("New weather_5d_forecast retrived")

        # Weather is encapsulated in a dictionary and saved
        cache = {
            'weather': weather,
            'retrival_time': datetime.now().isoformat(),
        }
        save_cache(cache_filename, cache)
        return weather
    else:
        print("Loaded from cache: %s" % cache_filename)
        weather = cache['weather']
        return weather


def retrieve_weather_24h_history(api_key, location_key):
    cache_filename = "weather_24h_history.json"
    cache_expiry = timedelta(minutes=57)

    cache = get_cache(cache_filename)
    if cache is None or datetime.fromisoformat(cache['retrival_time']) - datetime.now() > cache_expiry:
        # Retrive new weather
        request = "/currentconditions/v1/" + location_key + "/historical/24?apikey=" + api_key + "&details=true"
        weather = getJSONfromUrl(url + request)
        print("New weather_24h_history retrived")

        # Weather is encapsulated in a dictionary and saved
        cache = {
            'weather': weather,
            'retrival_time': datetime.now().isoformat(),
        }
        save_cache(cache_filename, cache)
        return weather
    else:
        print("Loaded from cache: %s" % cache_filename)
        weather = cache['weather']
        return weather


api_key = retrieve_api_key()
location_key = retrieve_location_key(api_key)
weather_24h_history = retrieve_weather_24h_history(api_key, location_key)
weather_5d_forecast = retrieve_weather_5d_forecast(api_key, location_key)
weather_12h_forecast = retrieve_weather_12h_forecast(api_key, location_key)


for hour_forcast in weather_12h_forecast:
    d = datetime.fromtimestamp(hour_forcast['EpochDateTime'])

    print("%s : %s%s" % (
        d.strftime("%H:%M"),
        hour_forcast['Temperature']['Value'],
        hour_forcast['Temperature']['Unit'])
    )
