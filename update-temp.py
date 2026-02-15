import pandas as pd
import requests
import os
import shutil
from datetime import datetime
import time
import glob
import sys
import logging

""" Setup paths """
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups-temp")
LOGS_DIR = os.path.join(BASE_DIR, "logs-temp")

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d")
last_year = datetime.now().year - 1
start_date = f"{last_year}-01-01"
end_date = f"{last_year}-12-31"

CSV_PATH = os.path.join(DATA_DIR, "cities.csv")
BACKUP_PATH = os.path.join(BACKUP_DIR, f"backup_{timestamp}.csv")
LOG_PATH = os.path.join(LOGS_DIR, f"update_{timestamp}.log")

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info(f"Starting yearly temperature update for {last_year}.")

backup_files = sorted(glob.glob(os.path.join(BACKUP_DIR, "backup_*.csv")))
while len(backup_files) >= 5:
    os.remove(backup_files.pop(0))

if os.path.exists(CSV_PATH):
    shutil.copy(CSV_PATH, BACKUP_PATH)

def get_yearly_avg_celsius(city, country):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city},{country}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=10).json()
        
        if 'results' not in geo_res:
            logging.warning(f"Skipping {city}: Not found.")
            return None
        
        lat = geo_res['results'][0]['latitude']
        lon = geo_res['results'][0]['longitude']

        archive_url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}"
            f"&daily=temperature_2m_mean&timezone=auto"
        )

        response = requests.get(archive_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'daily' in data and 'temperature_2m_mean' in data['daily']:
            daily_temps = data['daily']['temperature_2m_mean']
            valid_temps = [t for t in daily_temps if t is not None]
            
            if valid_temps:
                return int(round(sum(valid_temps) / len(valid_temps)))
        return None
    except requests.exceptions.Timeout:
        logging.error(f"Timeout reached for {city}. Skipping.")
        return None
    except Exception as e:
        logging.error(f"Error for {city}: {e}")
        return None

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    total=len(df)
    for index, row in df.iterrows():
        print(f"[{index+1}/{total}] Processing {row['City']}, {row['Country']}...", flush=True)

        logging.info(f"Processing {row['City']}...")
        new_val = get_yearly_avg_celsius(row['City'], row['Country'])
        if new_val is not None:
            df.at[index, 'Average_Temp_C'] = new_val
        time.sleep(1)

    df.to_csv(CSV_PATH, index=False)
    logging.info("CSV updated.")

logging.info("Yearly Temperature update completed.")