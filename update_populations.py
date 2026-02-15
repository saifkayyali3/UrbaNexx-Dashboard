# Updates Happen Monthly Automatically
# Need a GEODB_API_KEY to be able to run, add to environment variables for safety

import pandas as pd
import requests
import os
import shutil
from datetime import datetime
import time
import glob
import sys

""" Setup paths """

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d")
CSV_PATH = os.path.join(DATA_DIR, "cities.csv")
BACKUP_PATH = os.path.join(BACKUP_DIR, f"cities_backup_{timestamp}.csv")
LOG_PATH = os.path.join(LOGS_DIR, f"update_{timestamp}.log")

# Logging setup
import logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Starting monthly population update script.")

# Backup with rolling limit of 5
backup_files = sorted(glob.glob(os.path.join(BACKUP_DIR, "cities_backup_*.csv")))
if len(backup_files) >= 5:
    oldest = backup_files[0]
    os.remove(oldest)
    logging.info(f"Deleted oldest backup: {oldest}")

if os.path.exists(CSV_PATH):
    shutil.copy(CSV_PATH, BACKUP_PATH)
    logging.info(f"Backup created at {BACKUP_PATH}")

# Load data
df = pd.read_csv(CSV_PATH)
iso_df = pd.read_csv(os.path.join(DATA_DIR, "all.csv"))

country_to_alpha2 = dict(zip(iso_df['name'], iso_df['alpha-2']))

country_to_alpha2.update({
    "UK": "GB", "USA": "US", "Palestine": "PS", "Russia": "RU", "Iran": "IR",
    "Viet Nam": "VN", "Korea, South": "KR", "Korea, North": "KP", "Syria": "SY",
    "Tanzania": "TZ", "Moldova": "MD", "Bolivia": "BO", "DRC": "CD",
    "Czechia": "CZ", "Laos": "LA", "Brunei": "BN", "Cabo Verde": "CV",
    "Eswatini": "SZ", "Micronesia": "FM", "Saint Kitts and Nevis": "KN",
    "Saint Lucia": "LC", "Saint Vincent and the Grenadines": "VC",
    "Sao Tome and Principe": "ST", "Timor-Leste": "TL", "Ivory Coast": "CI",
    "North Macedonia": "MK", "Burma": "MM", "Congo": "CG", "Swaziland": "SZ",
    "Cape Verde": "CV", "East Timor": "TL", "Vatican City": "VA",
    "Palestinian Territories": "PS", "Occupied Palestine": "PS",
    "Republic of the Congo": "CG", "Democratic Republic of the Congo": "CD",
    "The Gambia": "GM", "Bahamas": "BS", "Gambia": "GM",
    "Congo-Brazzaville": "CG", "Congo-Kinshasa": "CD",
    "Syrian Arab Republic": "SY", "Venezuela, RB": "VE",
    "Yemen, Rep.": "YE", "Iran, Islamic Rep.": "IR",
    "Korea, Dem. People's Rep.": "KP", "Korea, Rep.": "KR",
    "Lao PDR": "LA", "Russian Federation": "RU",
    "Tanzania, United Rep.": "TZ", "United Kingdom": "GB",
    "United States": "US", "PRC": "CN", "Deutschland": "DE", "España": "ES",
    "Italia": "IT", "Nippon": "JP", "Brasil": "BR", "México": "MX",
    "Türkiye": "TR", "Ελλάδα": "GR", "Sverige": "SE", "Suomi": "FI",
    "Nederland": "NL", "Polska": "PL", "Česká republika": "CZ",
    "Magyarország": "HU", "Österreich": "AT", "Schweiz": "CH",
    "Schweizerische Eidgenossenschaft": "CH", "Suisse": "CH", "Danmark": "DK",
    "Norge": "NO", "Ísland": "IS", "Ελλάδα": "GR", "ประเทศไทย": "TH",
    "المملكة العربية السعودية": "SA", "الإمارات العربية المتحدة": "AE",
    "대한민국": "KR", "中华人民共和国": "CN", "Российская Федерация": "RU",
    "الأردن": "JO", "لبنان": "LB", "مصر": "EG", "اليمن": "YE",
    "العراق": "IQ", "سوريا": "SY", "فلسطين": "PS","تونس": "TN", "المغرب": "MA",
    "الجزائر": "DZ", "ليبيا": "LY", "السودان": "SD", "Somaliland": "SO", "جمهورية السودان": "SD","جمهورية مصر العربية": "EG",
    "جمهورية العراق": "IQ", "جمهورية تونس": "TN", "المملكة المغربية": "MA", "جمهورية الجزائر": "DZ", "دولة ليبيا": "LY",
    "جمهورية الصومال": "SO","جمهورية اليمن": "YE","دولة الإمارات العربية المتحدة": "AE","المملكة العربية السعودية": "SA","دولة الكويت": "KW",
    "دولة قطر": "QA","سلطنة عمان": "OM","دولة البحرين": "BH","جمهورية لبنان": "LB","المملكة الأردنية الهاشمية": "JO",
    "دولة فلسطين": "PS","المملكة الأردنية ": "JO", 
})

# API Key
GEODB_KEY = os.getenv("GEODB_API_KEY")

def fetch_population(city, country):
    code = country_to_alpha2.get(country)
    if not code:
        return None
    url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
    headers = {"X-RapidAPI-Key": GEODB_KEY, "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"}
    params = {"namePrefix": city, "countryIds": code, "limit": 1}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            logging.warning(f"API Error {r.status_code} for {city}")
            return None
            
        data = r.json()
        if isinstance(data, dict) and "data" in data and data["data"]:
            return data["data"][0].get("population")
    except Exception as e:
        logging.warning(f"Failed to fetch population for {city}, {country}: {e}")
        return None

def update_populations(row):
    new_pop = fetch_population(row["City"], row["Country"])
    
    if new_pop is not None:
        return new_pop
    
    return row.get("Population")

def update_logic(row, index, total):
    print(f"[{index+1}/{total}] Processing {row['City']}, {row['Country']}...", flush=True)
    
    new_pop = fetch_population(row["City"], row["Country"])
    time.sleep(1.2) 
    
    if new_pop is not None:
        return new_pop
    return row.get("Population")

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    total_rows = len(df)

    new_populations = []
    for i, row in df.iterrows():
        new_populations.append(update_logic(row, i, total_rows))
    
    df["Population"] = new_populations

    df["PopulationDensity"] = df.apply(lambda r: round(r["Population"] / r["Area_km2"], 2) if pd.notna(r["Population"]) and r["Area_km2"] > 0 else None, axis=1)

    df.to_csv(CSV_PATH, index=False)
    logging.info("Population & density updated.")

logging.info("Monthly Population Update Complete.")
sys.exit(0)