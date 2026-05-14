#!/usr/bin/env python3
"""
Weather Data Automation Script
Fetches weather and AQI data from APIs and stores to database
"""

import requests
import os
import sys
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Add Assets to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Assets'))
from Assets.Cities import CITIES_DICT

# Load environment variables
load_dotenv()

# API Keys
api_key1 = os.getenv("OPENWEATHER_API_KEY")
api_key2 = os.getenv("WAQIP_API_KEY")
database_url = os.getenv("DATABASE_URL")

# File paths
base_dir = os.path.dirname(__file__)
json_dir = os.path.join(base_dir, 'Json_data')

path1 = os.path.join(json_dir, 'City.json')
path2 = os.path.join(json_dir, 'Weather_records.json')
path3 = os.path.join(json_dir, 'Aqi_stations.json')
path4 = os.path.join(json_dir, 'Aqi_records.json')
path5 = os.path.join(json_dir, 'Forecast_records.json')

temp1 = os.path.join(json_dir, 'Temp_City.json')
temp2 = os.path.join(json_dir, 'Temp_Weather_records.json')
temp3 = os.path.join(json_dir, 'Temp_Aqi_stations.json')
temp4 = os.path.join(json_dir, 'Temp_Aqi_records.json')
temp5 = os.path.join(json_dir, 'Temp_Forecast_records.json')

# Date
date = datetime.now().strftime("%Y-%m-%d")
forecast_day = datetime.now().day


def load_existing_data(file_path):
    """Load existing JSON data from file"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []


def save_data(file_path, data):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def build_existing_keys(data):
    """Build set of existing (city_id, date) keys"""
    keys = set()
    for record in data:
        city_id = record.get("City_id")
        record_date = record.get("Date")
        if city_id and record_date:
            keys.add((city_id, record_date))
    return keys


def Weather_error(city_name):
    """Fetch weather data from OpenWeather API with error handling"""
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city_name}&appid={api_key1}&units=metric"
    )
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"✗ Weather city not found: {city_name}")
        elif response.status_code == 401:
            print("✗ Invalid weather API key")
        else:
            print(f"✗ Weather API error: {response.status_code}")
        
        return None
    
    except requests.exceptions.Timeout:
        print(f"✗ Weather timeout: {city_name}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Weather network error: {e}")
        return None


def waqi_error(city_name):
    """Fetch AQI data from WAQI API with error handling"""
    url = f"https://api.waqi.info/feed/{city_name}/?token={api_key2}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"✗ AQI city not found: {city_name}")
        elif response.status_code == 401:
            print("✗ Invalid AQI API key")
        else:
            print(f"✗ AQI API error: {response.status_code}")
        
        return None
    
    except requests.exceptions.Timeout:
        print(f"✗ AQI timeout: {city_name}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"✗ AQI network error: {e}")
        return None


def fetch_data():
    """Fetch weather and AQI data for all cities"""
    print("\nLoading existing files...")
    
    city_data_existing = load_existing_data(path1)
    weather_existing = load_existing_data(path2)
    aqi_station_existing = load_existing_data(path3)
    aqi_record_existing = load_existing_data(path4)
    forecast_existing = load_existing_data(path5)
    
    city_keys = build_existing_keys(city_data_existing)
    weather_keys = build_existing_keys(weather_existing)
    aqi_station_keys = build_existing_keys(aqi_station_existing)
    aqi_record_keys = build_existing_keys(aqi_record_existing)
    forecast_keys = build_existing_keys(forecast_existing)
    
    print("\nFetching API data once per city...\n")
    
    weather_cache = {}
    aqi_cache = {}
    
    for city_id, city_name in CITIES_DICT.items():
        print(f"Fetching: {city_id}: {city_name}")
        weather_cache[city_id] = Weather_error(city_name)
        aqi_cache[city_id] = waqi_error(city_name)
    
    # Process city records
    new_city_records = []
    for city_id, city_name in CITIES_DICT.items():
        weather = weather_cache.get(city_id)
        if (city_id, date) not in city_keys and weather:
            city_record = {
                'City_id': city_id,
                'Open_Weather_City_id': weather['id'],
                'City': city_name,
                'Country': weather['sys']['country'],
                'Latitude': weather['coord']['lat'],
                'Longitude': weather['coord']['lon'],
                'Timezone_offset': weather['timezone'],
                'Date': date
            }
            new_city_records.append(city_record)
    
    # Process weather records
    new_weather_records = []
    for city_id, city_name in CITIES_DICT.items():
        weather = weather_cache.get(city_id)
        if (city_id, date) not in weather_keys and weather:
            weather_record = {
                "City_id": city_id,
                "Date": date,
                "Temperature": weather['main']['temp'],
                "Feels_like": weather['main']['feels_like'],
                "Temp_min": weather['main']['temp_min'],
                "Temp_max": weather['main']['temp_max'],
                "Pressure": weather['main']['pressure'],
                "Humidity": weather['main']['humidity'],
                "Sea_level": weather['main'].get('sea_level'),
                "Ground_level": weather['main'].get('grnd_level'),
                "Visibility": weather.get('visibility'),
                "Wind_speed": weather['wind'].get('speed'),
                "Wind_degree": weather['wind'].get('deg'),
                "Cloudiness": weather['clouds'].get('all'),
                "Weather_main": weather['weather'][0]['main'],
                "Weather_description": weather['weather'][0]['description'],
                "Weather_icon": weather['weather'][0]['icon'],
                "Sunrise": weather['sys']['sunrise'],
                "Sunset": weather['sys']['sunset']
            }
            new_weather_records.append(weather_record)
    
    # Process AQI stations
    new_aqi_stations = []
    for city_id, city_name in CITIES_DICT.items():
        waqi = aqi_cache.get(city_id)
        if ((city_id, date) not in aqi_station_keys and waqi and waqi.get("status") == "ok"):
            aqi_station = {
                "Station_id": waqi['data']['idx'],
                "City_id": city_id,
                "Date": date,
                "Station_name": waqi['data']['city']['name'],
                "Latitude": waqi['data']['city']['geo'][0],
                "Longitude": waqi['data']['city']['geo'][1],
                "Station_url": waqi['data']['city']['url'],
                "Is_active": True
            }
            new_aqi_stations.append(aqi_station)
    
    # Process AQI records
    new_aqi_records = []
    for city_id, city_name in CITIES_DICT.items():
        waqi = aqi_cache.get(city_id)
        if ((city_id, date) not in aqi_record_keys and waqi and waqi.get("status") == "ok"):
            iaqi = waqi['data'].get('iaqi', {})
            aqi_record = {
                "City_id": city_id,
                "Date": date,
                "Aqi": waqi['data']['aqi'],
                "Station_id": waqi['data']['idx'],
                "Dominant_pollutant": waqi['data']['dominentpol'],
                "pm25": iaqi.get('pm25', {}).get('v'),
                "pm10": iaqi.get('pm10', {}).get('v'),
                "o3": iaqi.get('o3', {}).get('v'),
                "no2": iaqi.get('no2', {}).get('v'),
                "so2": iaqi.get('so2', {}).get('v'),
                "co": iaqi.get('co', {}).get('v'),
                "Temperature": iaqi.get('t', {}).get('v'),
                "Humidity": iaqi.get('h', {}).get('v'),
                "Pressure": iaqi.get('p', {}).get('v'),
                "Wind_speed": iaqi.get('w', {}).get('v'),
                "Wind_direction": iaqi.get('wd', {}).get('v'),
                "Wind_gust": iaqi.get('wg', {}).get('v'),
                "Dew_point": iaqi.get('dew', {}).get('v')
            }
            new_aqi_records.append(aqi_record)
    
    # Process forecast records
    new_forecasts = []
    for city_id, city_name in CITIES_DICT.items():
        waqi = aqi_cache.get(city_id)
        if ((city_id, date) not in forecast_keys and waqi and waqi.get("status") == "ok"):
            try:
                pm25_forecast = waqi['data']['forecast']['daily']['pm25'][0]
                forecast_record = {
                    "City_id": city_id,
                    "Date": date,
                    "Station_id": waqi['data']['idx'],
                    "Forecast_day": forecast_day,
                    "Metric_type": "pm25",
                    "Avg_value": pm25_forecast.get('avg'),
                    "Max_value": pm25_forecast.get('max'),
                    "Min_value": pm25_forecast.get('min')
                }
                new_forecasts.append(forecast_record)
            except Exception:
                print(f"✗ Forecast missing for {city_name}")
    
    # Merge with existing data
    city_data_existing.extend(new_city_records)
    weather_existing.extend(new_weather_records)
    aqi_station_existing.extend(new_aqi_stations)
    aqi_record_existing.extend(new_aqi_records)
    forecast_existing.extend(new_forecasts)
    
    # Save to JSON files
    save_data(path1, city_data_existing)
    save_data(path2, weather_existing)
    save_data(path3, aqi_station_existing)
    save_data(path4, aqi_record_existing)
    save_data(path5, forecast_existing)
    
    # Save temp files
    save_data(temp1, new_city_records)
    save_data(temp2, new_weather_records)
    save_data(temp3, new_aqi_stations)
    save_data(temp4, new_aqi_records)
    save_data(temp5, new_forecasts)
    
    print("\n====================================")
    print("✓ DATA COLLECTION COMPLETE")
    print("====================================")
    print(f"Cities Added: {len(new_city_records)}")
    print(f"Weather Added: {len(new_weather_records)}")
    print(f"AQI Stations Added: {len(new_aqi_stations)}")
    print(f"AQI Records Added: {len(new_aqi_records)}")
    print(f"Forecast Added: {len(new_forecasts)}")
    
    return new_city_records, new_weather_records, new_aqi_stations, new_aqi_records, new_forecasts


def store_to_database():
    """Store JSON data to PostgreSQL database"""
    print("\nStoring data to database...")
    
    # Load temp files
    city = pd.read_json(temp1)
    weather = pd.read_json(temp2)
    aqi_stations = pd.read_json(temp3)
    aqi_records = pd.read_json(temp4)
    forecast_records = pd.read_json(temp5)
    
    # Convert to DataFrames
    City = pd.DataFrame(city)
    Weather_records = pd.DataFrame(weather)
    Aqi_stations = pd.DataFrame(aqi_stations)
    Aqi_records = pd.DataFrame(aqi_records)
    Forecast_records = pd.DataFrame(forecast_records)
    
    # Create database engine
    engine = create_engine(database_url)
    
    # Store to database
    if not City.empty:
        City.to_sql('city', engine, if_exists='append', index=False)
        print(f"✓ City records: {len(City)}")
    
    if not Weather_records.empty:
        Weather_records.to_sql('weather_records', engine, if_exists='append', index=False)
        print(f"✓ Weather records: {len(Weather_records)}")
    
    if not Aqi_stations.empty:
        Aqi_stations.to_sql('aqi_stations', engine, if_exists='append', index=False)
        print(f"✓ AQI stations: {len(Aqi_stations)}")
    
    if not Aqi_records.empty:
        Aqi_records.to_sql('aqi_records', engine, if_exists='append', index=False)
        print(f"✓ AQI records: {len(Aqi_records)}")
    
    if not Forecast_records.empty:
        Forecast_records.to_sql('forecast_records', engine, if_exists='append', index=False)
        print(f"✓ Forecast records: {len(Forecast_records)}")
    
    print("✓ Database update complete")


def main():
    """Main execution function"""
    print("====================================")
    print("WEATHER DATA AUTOMATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("====================================")
    
    # Check API keys
    if not api_key1 or not api_key2:
        print("✗ Error: API keys not found in .env file")
        return
    
    if not database_url:
        print("✗ Error: DATABASE_URL not found in .env file")
        return
    
    print(f"✓ Weather API Loaded: {api_key1[:5]}...")
    print(f"✓ WAQI API Loaded: {api_key2[:5]}...")
    print(f"✓ Database URL configured")
    
    # Fetch data
    fetch_data()
    
    # Store to database
    store_to_database()
    
    print(f"\n✓ Automation complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
