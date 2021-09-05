import yaml
import requests
import json
from datetime import datetime, timedelta
import os

city_name = "Zurich, Switzerland"
url = "http://dataservice.accuweather.com"
cache_folder = "../cache"
api_key_filename = '../password.yml'
# ##################################################################
# The retrieve_* functions in this file have implemented file
# cacheing. The retrived json data are stored in the cache folders.
# get_cache() and save_cache() function assisted this.
# ##################################################################


def getJSONfromUrl(url):
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data


def retrieve_api_key():
    here = os.path.realpath(__file__)
    path = os.path.realpath(os.path.join(os.path.dirname(here), api_key_filename))
    with open(path) as stream:
        config = yaml.safe_load(stream)
        api_key = config['accuweather']['api_key']
        return api_key


def get_cache(filename):
    # Load json from file if exist
    here = os.path.realpath(__file__)
    folder_path = os.path.realpath(os.path.join(os.path.dirname(here), cache_folder))
    # folder_path = os.path.abspath(cache_folder)
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
    here = os.path.realpath(__file__)
    folder_path = os.path.realpath(os.path.join(os.path.dirname(here), cache_folder))

    # folder_path = os.path.abspath(cache_folder)
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
    cache_expiry = timedelta(days=2)

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
    if cache is None or datetime.now() - datetime.fromisoformat(cache['retrival_time']) > cache_expiry:
        # Retrive new weather
        request = "/forecasts/v1/hourly/12hour/" + location_key + "?apikey=" + api_key + "&details=true&metric=true"
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
    if cache is None or datetime.now() - datetime.fromisoformat(cache['retrival_time']) > cache_expiry:
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
    cache_expiry = timedelta(hours=1, minutes=57)

    cache = get_cache(cache_filename)
    if cache is None or datetime.now() - datetime.fromisoformat(cache['retrival_time']) > cache_expiry:
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


def retrieve_all_weather(state):
    """
    Manages all call to AccuWeather

    Free Trial 50 calls/day
    -----------------------

    - retrieve_location_key : Update freq every 2 days (1 time a day max)
    - weather_24h_history : Update freq every 2 hours (12 times a day)
    - weather_5d_forecast : Update freq every 6 hours (4 times a day)
    - weather_12h_forecast : Update freq every 1 hours (24 times a day)
    Total: ~ 41 Calls
    """
    api_key = retrieve_api_key()
    location_key = retrieve_location_key(api_key)

    weather_24h_history = retrieve_weather_24h_history(api_key, location_key)
    weather_5d_forecast = retrieve_weather_5d_forecast(api_key, location_key)
    weather_12h_forecast = retrieve_weather_12h_forecast(api_key, location_key)
    daily_temp_plot = build_daily_temp_plot(weather_24h_history, weather_12h_forecast)
    all_weather = {
        'weather_24h_history': weather_24h_history,
        'weather_5d_forecast': weather_5d_forecast,
        'weather_12h_forecast': weather_12h_forecast,
        'daily_temp_plot': daily_temp_plot
    }
    state.update(all_weather)
    return all_weather


def build_daily_temp_plot(weather_24h_history, weather_12h_forecast):
    now = datetime.now()
    compile_date_string = now.strftime('%Y-%m-%d')
    cache_filename = "plot_daily_temp_%s.json" % compile_date_string
    cache = get_cache(cache_filename)
    # Create a empty storage dictionary structure
    if cache is None:
        cache = {}
        for i in range(24):
            cache[str(i)] = {'historic': None, 'forecast': None}
    # Date for the current plot

    cache['compile_date'] = compile_date_string
    cache['compile_epoch'] = int(now.timestamp())

    # Updating cells in the cache
    for observation in weather_24h_history:
        d = datetime.fromtimestamp(observation['EpochTime'])
        if (d + timedelta(minutes=5)).date() != now.date():
            continue
        rounded_hour = (d + timedelta(minutes=30)).hour
        cache[str(rounded_hour)]['historic'] = observation['Temperature']['Metric']['Value']
    for observation in weather_12h_forecast:
        d = datetime.fromtimestamp(observation['EpochDateTime'])
        if (d - timedelta(minutes=5)).date() != now.date():
            continue
        rounded_hour = (d + timedelta(minutes=30)).hour
        cache[str(rounded_hour)]['forecast'] = observation['Temperature']['Value']

    save_cache(cache_filename, cache)
    return cache


def print_weather_summary():
    weather = retrieve_all_weather({})

    # Printing Historial Data
    print("Hourly Historic: ")
    for observation in weather['weather_24h_history']:
        d = datetime.fromtimestamp(observation['EpochTime'])
        print("%s : %s%s prec: %s%s" % (
            d.strftime("%a %H:%M"),
            observation['Temperature']['Metric']['Value'],
            observation['Temperature']['Metric']['Unit'],
            observation['Precip1hr']['Metric']['Value'],
            observation['Precip1hr']['Metric']['Unit'],
        ))

    # Printing Hourly Forecast
    print("Hourly Forecast: ")
    for observation in weather['weather_12h_forecast']:
        d = datetime.fromtimestamp(observation['EpochDateTime'])
        print("%s : %s%s prec: %s%s (%s%%)" % (
            d.strftime("%a %H:%M"),
            observation['Temperature']['Value'],
            observation['Temperature']['Unit'],
            observation['TotalLiquid']['Value'],
            observation['TotalLiquid']['Unit'],
            observation['PrecipitationProbability'],
        ))

    # 5 Day Forecast
    print("Daily Forecast: ")
    for observation in weather['weather_5d_forecast']['DailyForecasts']:
        d = datetime.fromtimestamp(observation['EpochDate'])
        print("%s : %s%s to %s%s" % (
            d.strftime("%a %H:%M"),
            observation['Temperature']['Minimum']['Value'],
            observation['Temperature']['Minimum']['Unit'],
            observation['Temperature']['Maximum']['Value'],
            observation['Temperature']['Maximum']['Unit'],
        ))


if __name__ == "__main__":
    print_weather_summary()
