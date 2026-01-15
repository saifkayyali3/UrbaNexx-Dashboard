# Updates Happen Monthly

import pandas as pd
import requests
import os
import shutil
from datetime import datetime
import glob
import subprocess

# Setup paths
BASE_DIR = r"C:\Users\USER\OneDrive\Desktop\UrbaNexxDash"
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
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
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
    headers = {
        "X-RapidAPI-Key": GEODB_KEY,
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }
    params = {"namePrefix": city, "countryIds": code, "limit": 1}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        data = r.json()
        if data["data"]:
            return data["data"][0].get("population")
    except Exception as e:
        logging.warning(f"Failed to fetch population for {city}, {country}: {e}")
        return None

def update_populations(row):
    if pd.notna(row.get("Population")):
        return row["Population"]
    return fetch_population(row["City"], row["Country"])

# Update population & density
df["Population"] = df.apply(update_populations, axis=1)
df["PopulationDensity"] = df.apply(
    lambda r: round(r["Population"] / r["Area_km2"], 2)
    if pd.notna(r["Population"]) and pd.notna(r["Area_km2"]) and r["Area_km2"] > 0
    else None,
    axis=1
)

# Clean & reorder columns
df = df.drop(columns=[col for col in ["Latitude", "Longitude"] if col in df.columns])
columns_order = ["City", "Country", "Population", "Area_km2", "PopulationDensity", "Average_Temp_C"]
df = df[columns_order]

# Save updated CSV
df.to_csv(CSV_PATH, index=False)
logging.info("Population & density updated, unnecessary columns removed, and density column moved correctly.")

# Git commit & push
def run_git(cmd):
    return subprocess.run(
        cmd,
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )

try:
    run_git(["git", "add", "-A"])

    status = run_git(["git", "status", "--porcelain"])

    if not status.stdout.strip():
        logging.info("No changes detected. Skipping git commit.")
    else:
        run_git(["git", "commit", "-m", f"Monthly population update {timestamp}"])
        run_git(["git", "push", "origin", "main"])
        logging.info("Changes committed and pushed to git.")

except subprocess.CalledProcessError as e:
    logging.error("Git stdout:\n" + e.stdout)
    logging.error("Git stderr:\n" + e.stderr)
    logging.warning(f"Git operation failed: {e}")


print("Update complete. See log for details:", LOG_PATH)