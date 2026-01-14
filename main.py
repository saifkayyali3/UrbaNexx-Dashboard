from flask import Flask, render_template, request
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

    warning = None
    filtered = pd.DataFrame()

    if query:
        filtered = df[df["City"].str.lower().str.contains(query.lower())]
        if filtered.empty:
            warning = f"No data found for '{query}'."
    elif request.args.get("searched") == "1":
        warning = "Please enter a city name."
    plot = None
    if not filtered.empty:
        plot = population_area_plot(filtered)

    records = filtered.to_dict(orient="records")

    return render_template("dashboard.html",tables=records,warning=warning,query=query,plot=plot)

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



@app.route("/city/<city_name>")
def city_view(city_name):
    city = df[df["City"].str.lower() == city_name.lower()]
    if city.empty:
        return "City not found", 404

    return render_template("city.html", city=city.iloc[0])


if __name__ == "__main__":
    app.run(debug=True)
