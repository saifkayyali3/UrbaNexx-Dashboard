from flask import Flask, render_template, request, send_file, Response, jsonify 
from datetime import datetime, timezone
import pandas as pd 
import io
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.parse import unquote


df = pd.read_csv("data/cities.csv")
df["City_lower"] = df["City"].str.lower()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def dashboard():
    query = request.args.get("q", "").strip()
    full_view = request.args.get("full_view") == "1"  
    export_error = request.args.get("export_error")

    warning = None
    filtered = pd.DataFrame()

    if export_error == "no-selection-csv":
        warning = "No cities selected for CSV export, select at least one."

    if full_view:
        filtered = df.copy()
    elif query:
        filtered = df[df["City"].str.lower().str.contains(query.lower())]
        if filtered.empty:
            warning = f"No data found for '{query}'."
    elif request.args.get("searched") == "1":
        warning = "Please enter a city name."

    records = filtered.to_dict(orient="records")

    return render_template("dashboard.html",tables=records,warning=warning,query=query,full_view=full_view,searched=request.args.get("searched") == "1")

@app.route("/export_csv", methods=["POST"])
def export_csv():
    selected_cities = request.form.getlist("cities")
    if not selected_cities:
        return jsonify({"error": "Select at least one city to export CSV."}), 400

    filtered = df[df["City"].isin(selected_cities)]
    if filtered.empty:
        return jsonify({"error": "No matching cities found."}), 400

    csv_buffer = io.StringIO()
    filtered.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(io.BytesIO(csv_buffer.getvalue().encode()),mimetype="text/csv",as_attachment=True,download_name="selected_cities.csv")

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}

def get_latest_mod_time():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

@app.route("/city/<path:city_name>")
def city_view(city_name):
    city_name = unquote(city_name).strip().lower()

    city = df[df["City_lower"] == city_name]
    if city.empty:
        return render_template("404.html", message=f"City '{city_name.title()}' not found."), 404

    return render_template("city.html", city=city.iloc[0])

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html",message="The page you are looking for does not exist."), 404

@app.route("/sitemap.xml")
def sitemap():
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    lastmod = get_latest_mod_time()

    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = request.url_root.rstrip("/")
    ET.SubElement(url, "lastmod").text = lastmod

    for city in df["City"]:
        city_slug = quote(city)  
        city_url = ET.SubElement(urlset, "url")
        ET.SubElement(city_url, "loc").text = f"{request.url_root}city/{city_slug}"
        ET.SubElement(city_url, "lastmod").text = lastmod

    xml_str = ET.tostring(urlset, encoding="utf-8", method="xml")
    return Response(xml_str, mimetype="application/xml")

@app.route("/robots.txt")
def robots_txt():
    return """User-agent: *
Allow: /
Sitemap: {}/sitemap.xml
""".format(request.url_root.rstrip("/")), 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    app.run(debug=True)
