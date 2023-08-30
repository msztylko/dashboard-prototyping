import datetime

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import requests
from dash import Input, Output, dcc, html
from dash.dependencies import Input, Output

available_values = ("open", "high", "low", "close", "adj_close", "volume")


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.Hr(),
        html.P("Ticker 1"),
        dcc.Input(
            id="ticker1",
            type="text",
            value="AAPL",
            placeholder="",
            debounce=True,
        ),
        html.Hr(),
        html.P("Ticker 2"),
        dcc.Input(
            id="ticker2",
            type="text",
            value="AAPL",
            placeholder="",
            debounce=True,
        ),
        html.Hr(),
        html.P("Start Date"),
        dcc.DatePickerSingle(
            id="start",
            min_date_allowed=datetime.date(2020, 8, 5),
            max_date_allowed=datetime.date(2023, 8, 19),
            initial_visible_month=datetime.date(2020, 8, 5),
            date=datetime.date(2020, 8, 5),
        ),
        html.Hr(),
        html.P("End Date"),
        dcc.DatePickerSingle(
            id="end",
            min_date_allowed=datetime.date(2020, 8, 5),
            max_date_allowed=datetime.date(2023, 8, 19),
            initial_visible_month=datetime.date(2023, 8, 19),
            date=datetime.date(2023, 8, 19),
        ),
        html.Hr(),
        html.P("Value to plot"),
        dcc.Dropdown(
            id="value-dropdown",
            options=[{"label": v, "value": v} for v in available_values],
            value="close",
        ),
    ],
    style=SIDEBAR_STYLE,
)

# content = html.Div(id="page-content", style=CONTENT_STYLE)
graph = html.Div(
    [
        html.H1("Stock Prices", style={"textAlign": "center"}),
        dcc.Graph(id="price-chart"),
    ],
    style=CONTENT_STYLE,
)


app.layout = html.Div(
    [
        sidebar,
        graph,
    ]
)


def date_to_datetime(dt):
    return datetime.datetime.combine(dt, datetime.datetime.min.time())


def get_data(ticker, start_date, end_date):
    start_date = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.fromisoformat(end_date)
    end_date = date_to_datetime(end_date).isoformat()
    start_date = date_to_datetime(start_date).isoformat()
    data = requests.get(
        f"http://localhost:5000/prices/{ticker}/{start_date}/{end_date}"
    )
    df = pd.DataFrame(dict(price) for price in data.json())
    df["date"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("date")
    return df


@app.callback(
    Output("price-chart", "figure"),
    [
        Input("ticker1", "value"),
        Input("ticker2", "value"),
        Input("start", "date"),
        Input("end", "date"),
        Input("value-dropdown", "value"),
    ],
)
def update_graph(ticker1, ticker2, start, end, value):
    fig = go.Figure()
    data1 = get_data(ticker1, start, end)
    fig.add_scatter(x=data1.index, y=data1[value], name=ticker1)
    data2 = get_data(ticker2, start, end)
    fig.add_scatter(x=data2.index, y=data2[value], name=ticker2)
    fig.update_layout(
        title_text=f"{ticker1} and {ticker2}  {value}",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title=value,
    )

    return fig


if __name__ == "__main__":
    app.run_server()
