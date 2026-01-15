from flask import Flask, render_template, request, send_file, url_for, redirect
import pandas as pd
import io
import base64
import matplotlib as mpl
mpl.rcParams['axes.formatter.use_mathtext'] = True
mpl.use("Agg")
import matplotlib.pyplot as plt


df = pd.read_csv("data/cities.csv")

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

    return render_template("dashboard.html",tables=records,warning=warning,query=query,plot=plot,full_view=full_view)


def population_area_plot(data):
    plot_data = data.dropna(subset=["Population", "Area_km2"])
    if plot_data.empty:
        return None

    plt.figure(figsize=(6, 4))

    colors = plt.cm.tab20.colors
    for i, (_, row) in enumerate(plot_data.iterrows()):
        plt.scatter(
            row["Area_km2"],
            row["Population"],
            label=row["City"],
            color=colors[i % len(colors)],
            alpha=0.8
        )

    plt.xlabel("Area (km²)")
    plt.ylabel("Population")
    plt.grid(True, which="both", ls="--", lw=0.5)
    plt.title("Population vs Area")
    plt.legend(
        fontsize="small",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=min(len(plot_data), 4),  # wraps into multiple columns if many cities
        frameon=False
    )


    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight") 
    plt.close()
    img.seek(0)

    return base64.b64encode(img.read()).decode("utf-8")


@app.route("/export_csv", methods=["POST"])
def export_csv():
    selected_cities = request.form.getlist("cities")
    if not selected_cities:
        return redirect(url_for("dashboard", export_error="no-selection-csv"))

    filtered = df[df["City"].isin(selected_cities)]

    csv_buffer = io.StringIO()
    filtered.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(io.BytesIO(csv_buffer.getvalue().encode()), mimetype="text/csv", as_attachment=True, download_name="selected_cities.csv")

@app.route("/export_plot", methods=["POST"])
def export_plot():
    selected_cities = request.form.getlist("cities")
    if not selected_cities:
        return redirect(url_for("dashboard", export_error="no-selection-plot"))

    filtered = df[df["City"].isin(selected_cities)]
    if filtered.empty:
        return redirect(url_for("dashboard", export_error="no-selection-plot"))

    fig, ax = plt.subplots(figsize=(8,6))
    colors = plt.cm.tab20.colors
    for i, (_, row) in enumerate(filtered.iterrows()):
        if pd.notna(row["Population"]) and pd.notna(row["Area_km2"]):
            ax.scatter(
                row["Area_km2"],
                row["Population"],
                label=row["City"],
                color=colors[i % len(colors)],
                alpha=0.8
            )

    ax.set_xlabel("Area (km²)")
    ax.set_ylabel("Population")
    ax.set_title("Population vs Area")
    ax.grid(True, which="both", ls="--", lw=0.5)
    ax.legend(fontsize="small", loc="best")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return send_file(buf,mimetype="image/png",as_attachment=True,download_name="population_area_plot.png")

from datetime import datetime

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}


@app.route("/city/<city_name>")
def city_view(city_name):
    city = df[df["City"].str.lower() == city_name.lower()]
    if city.empty:
        return "City not found", 404

    return render_template("city.html", city=city.iloc[0])


if __name__ == "__main__":
    app.run(debug=True)
