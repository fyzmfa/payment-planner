from flask import Flask, render_template, request
import csv
from pathlib import Path

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add-payment", methods=["POST"])
def add_payment():
    data = request.form.to_dict()

    file_exists = Path("payments.csv").exists()
    with open("payments.csv", mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

    return "Payment saved! ✅ <a href='/'>Go back</a>"

import pandas as pd

@app.route("/pivot")
def pivot_table():
    try:
        df = pd.read_csv("payments.csv", parse_dates=["payment_date"])
        df["payment_date"] = pd.to_datetime(df["payment_date"])

        pivot = df.groupby("payment_date")["payment_amount"].sum().reset_index()
        pivot_html = pivot.to_html(index=False, classes="table table-bordered")

        return render_template("pivot.html", table=pivot_html)

    except Exception as e:
        return f"Error reading CSV: {e}"

import plotly.express as px
import plotly.io as pio

@app.route("/calendar")
def calendar_view():
    try:
        df = pd.read_csv("payments.csv", parse_dates=["payment_date"])
        df["payment_date"] = pd.to_datetime(df["payment_date"])
        df["payment_amount"] = pd.to_numeric(df["payment_amount"], errors="coerce")

        daily = df.groupby("payment_date")["payment_amount"].sum().reset_index()

        fig = px.density_heatmap(
            daily,
            x="payment_date",
            y=["Payment Load"] * len(daily),  # fake y-axis to make it 1-row
            z="payment_amount",
            nbinsx=30,
            color_continuous_scale="YlOrRd",
            labels={"payment_amount": "₹ Amount", "payment_date": "Date"}
        )

        fig.update_layout(
            title="📅 Payment Calendar Heatmap",
            yaxis=dict(showticklabels=False),
            xaxis_title="Date",
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )

        graph_html = pio.to_html(fig, full_html=False)

        return render_template("calendar.html", plot=graph_html)

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
