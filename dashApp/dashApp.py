from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# https://gitlab.com/abtawfik/docker-celery-dash-redis-template/-/blob/master/docker-compose.yml?ref_type=heads

from components.featureDatatable import featureDataTable_layout
from components.imageViewer import mxifViewer_layout

from celery import Celery
from dash.long_callback import CeleryLongCallbackManager

## Add celery bindings
# Celery callback manager.
celery_app = Celery(
    __name__,
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="redis://redis:6379/0",
)
long_callback_manager = CeleryLongCallbackManager(celery_app)


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    long_callback_manager=long_callback_manager,
)


tab_layout = dcc.Tabs(
    children=[
        dcc.Tab(
            label="Feature Data",
            value="featureData",
            children=[featureDataTable_layout],
        ),
        dcc.Tab(
            label="Feature Graphs", value="mxifViewer", children=[mxifViewer_layout]
        ),
    ],
    value="mxifViewer",
)


app.layout = html.Div([tab_layout])

server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
