# UrbaNexx: City Data Dashboard

UrbaNexx is an interactive dashboard that provides an overview of cities worldwide, including population, area, and average temperature data. Users can explore cities, visualize population vs. area, and even submit additional information for review.  

---

## Features

- **Searchable City Table**: Quickly find cities using the search bar.
- **Live Population Updates**: Fetches updated population data from the GeoDB API.
- **Data Submission**: Users can submit new information for cities, subject to verification.
- **Interactive Table**: Browse, sort, and view city data easily in table format.

---

## Live Demo:
Check out the live site on: **[UrbaNexx Dashboard](https://urbanexx-dashboard.vercel.app/)!**

---

## Data Sources & Attribution

City & Population Data: Fetched from [GeoDB Cities API](https://rapidapi.com/wirefreethought/api/geodb-cities), as the script  which updates population data is built to run every month insha'Allah

Country Codes: Derived from [Luke’s ISO-3166 Countries with Regional Codes](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/tree/master/all) (`all.csv`), licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). 

Temperature Data: Fetched from [Open-meteo API](https://open-meteo.com/), as the script which updates temperature data is built to run yearly insha'Allah

Proper attribution is required when using or modifying this data.

---

## How to Run Locally:

### 1. Clone this repository:
```bash
   git clone https://github.com/Skayyali3/UrbaNexxDash.git
   cd UrbaNexxDash
```
### 2. Make a virtual environment:
```bash
    python -m venv venv

    source venv/bin/activate # Linux/macOS
    venv\Scripts\activate # Windows
```

### 3. Install dependencies:
```bash
    pip install -r requirements.txt
```

### 4. Run:
```bash 
    python main.py
    # Open your browser at http://127.0.0.1:5000 to view the dashboard.
```

---

## Contributing:

Contributions are welcome!

1. Fork the repository.

2. Make your changes (if it is a new city data submission, please make sure it isn't already present before adding).

3. Submit a pull request for review (if a new city data submission, country-reorder.py must be ran before submitting the pull request to ensure organization of data).

All new city data submissions are fact-checked before being accepted.

---

## LICENSE:

This project is under the MIT License - check the [LICENSE](LICENSE) file for more details.


## Licensing Notice

This project uses third-party datasets licensed under **CC BY-SA 4.0**.
Any redistributed or modified versions of those datasets must remain
under the same license, with proper attribution.

## Author
**Saif Kayyali**
