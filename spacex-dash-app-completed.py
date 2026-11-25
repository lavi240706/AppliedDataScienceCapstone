"""
Completed IBM SpaceX interactive dashboard lab.
Run: python spacex-dash-app-completed.py
Expected dataset: spacex_launch_dash.csv in this directory.
"""
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

DATA_FILE = "spacex_launch_dash.csv"
spacex_df = pd.read_csv(DATA_FILE)

# Normalize column names only if the dataset uses common alternate names.
rename_map = {}
for col in spacex_df.columns:
    if col.lower().strip() in {"launchsite", "launch_site"}:
        rename_map[col] = "Launch Site"
    elif col.lower().strip() in {"payloadmass", "payload_mass", "payload_mass_kg"}:
        rename_map[col] = "Payload Mass (kg)"
    elif col.lower().strip() == "booster_version_category":
        rename_map[col] = "Booster Version Category"
spacex_df = spacex_df.rename(columns=rename_map)

required = {"Launch Site", "Payload Mass (kg)", "class"}
missing = required - set(spacex_df.columns)
if missing:
    raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
if "Booster Version Category" not in spacex_df.columns:
    spacex_df["Booster Version Category"] = "Unknown"

spacex_df["Payload Mass (kg)"] = pd.to_numeric(spacex_df["Payload Mass (kg)"], errors="coerce")
spacex_df["class"] = pd.to_numeric(spacex_df["class"], errors="coerce")
min_payload = int(spacex_df["Payload Mass (kg)"].min(skipna=True) or 0)
max_payload = int(spacex_df["Payload Mass (kg)"].max(skipna=True) or 10000)
max_payload = max(10000, max_payload)

app = Dash(__name__)
app.title = "SpaceX Launch Dashboard"

sites = sorted(spacex_df["Launch Site"].dropna().unique())
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site, "value": site} for site in sites
]

app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard", style={"textAlign": "center"}),
    html.Label("Select Launch Site:"),
    dcc.Dropdown(
        id="site-dropdown",
        options=site_options,
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True,
    ),
    html.Div([
        html.H2("Launch Success Counts"),
        dcc.Graph(id="success-pie-chart"),
    ]),
    html.Label("Select Payload Range (kg):"),
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload],
    ),
    html.Div([
        html.H2("Payload vs Launch Outcome"),
        dcc.Graph(id="success-payload-scatter-chart"),
    ]),
], style={"maxWidth": "1200px", "margin": "auto", "padding": "20px"})

# TASK 2: Pie chart callback based on selected site
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def get_pie_chart(entered_site):
    filtered = spacex_df if entered_site == "ALL" else spacex_df[spacex_df["Launch Site"] == entered_site]
    counts = filtered["class"].value_counts().sort_index()
    labels = {0: "Failure", 1: "Success"}
    names = [labels.get(int(v), str(v)) for v in counts.index]
    fig = px.pie(values=counts.values, names=names, title="Launch Outcomes")
    return fig

# TASK 4: Scatter chart callback based on selected site and payload interval
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered = spacex_df[spacex_df["Payload Mass (kg)"].between(low, high, inclusive="both")]
    if entered_site != "ALL":
        filtered = filtered[filtered["Launch Site"] == entered_site]
    fig = px.scatter(
        filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title="Payload Mass vs Launch Outcome",
        hover_data=["Launch Site"],
    )
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Failure", "Success"])
    return fig

if __name__ == "__main__":
    app.run(debug=True, port=8050)
