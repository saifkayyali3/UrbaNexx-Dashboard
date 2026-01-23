from flask import Flask, render_template, request, send_file, Response, jsonify 
from datetime import datetime, timezone
import pandas as pd 
import io
import xml.etree.ElementTree as ET
from urllib.parse import quote
import plotly.express as px 
import plotly.io as pio 
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
    elif export_error == "no-selection-plot":
        warning = "No cities found for plot export, select at least one in database."

    if full_view:
        filtered = df.copy()
    elif query:
        filtered = df[df["City"].str.lower().str.contains(query.lower())]
        if filtered.empty:
            warning = f"No data found for '{query}'."
    elif request.args.get("searched") == "1":
        warning = "Please enter a city name."

    plot = None
    if not filtered.empty:
        plot = population_area_plot(filtered)

    records = filtered.to_dict(orient="records")

    # Respond to AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"warning": warning,"plot": plot,"tables": records})

    return render_template("dashboard.html",tables=records,warning=warning,query=query,plot=plot,full_view=full_view,searched=request.args.get("searched") == "1")


def population_area_plot(data):
    plot_data = data.dropna(subset=["Population", "Area_km2"])
    if plot_data.empty:
        return None

    fig = px.scatter(plot_data,x="Area_km2",y="Population",color="City",hover_name="City",labels={"Area_km2":"Area (km²)","Population":"Population"},title="Population vs Area",color_discrete_sequence=px.colors.qualitative.Alphabet)
    fig.update_traces(marker=dict(size=8, opacity=0.8))
    fig.update_layout(autosize=True,margin=dict(l=40, r=20, t=50, b=40),legend=dict(font=dict(size=10),orientation="h",yanchor="bottom",y=-0.3))
    plot_html = pio.to_html(fig,full_html=False,include_plotlyjs="cdn",config={"responsive": True})

    return plot_html



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

@app.route("/export_plot", methods=["POST"])
def export_plot():
    selected_cities = request.form.getlist("cities")
    if not selected_cities:
        return jsonify({"error": "Select at least one city to export plot."}), 400

    filtered = df[df["City"].isin(selected_cities)]
    if filtered.empty:
        return jsonify({"error": "No valid city data to plot."}), 400

    # Plotly scatter for export
    fig = px.scatter(filtered,x="Area_km2",y="Population",color="City",hover_name="City",labels={"Area_km2": "Area (km²)", "Population": "Population"},color_discrete_sequence=px.colors.qualitative.Alphabet,width=1200,height=800,title="Population vs Area")
    fig.update_traces(marker=dict(size=8, opacity=0.8))

    buf = io.BytesIO()
    fig.write_image(buf, format="png", engine="kaleido")
    buf.seek(0)

    return send_file(buf,mimetype="image/png",as_attachment=True,download_name="population_area_plot.png")

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
