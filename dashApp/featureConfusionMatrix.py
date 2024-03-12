from dash import html, Input, Output, State, dcc, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import seaborn as sns
from ..utils.helpers import load_dataset, generate_generic_DataTable
from dash import dcc

sampleCSVFile = "MAP01938_0000_0E_01_region_001_quantification.csv"
df = load_dataset(sampleCSVFile)


featureConfusionMatrix_layout = html.Div([
    html.H1("Correlation Heatmap"),
    dcc.Store(id="rawFeatureData", data=df.to_dict("records")),
    dbc.Row(id="heatmap-graph")
]
)

@callback(
    Output("heatmap-graph","children"),
    Input("rawFeatureData", "data")
)
# def update_heatmap(clusterData):
#     df = pd.DataFrame(clusterData)
#     all_columns = df.columns
#     filtered_columns = [col for col in all_columns if col.startswith('intensity')]
#     data = df[filtered_columns]
#     correlation_matrix = data.corr()
#     fig = px.imshow(correlation_matrix, x=correlation_matrix.columns, y=correlation_matrix.columns, color_continuous_scale='Viridis', zmin=-1, zmax=1)
#     fig.update_layout(title="Correlation Heatmap")
#     return dcc.Graph(figure=fig)
def update_heatmap(clusterData):
    df = pd.DataFrame(clusterData)
    all_columns = df.columns
    filtered_columns = [col for col in all_columns if col.startswith('intensity')]
    data = df[filtered_columns]
    correlation_matrix = data.corr()

    fig = px.imshow(
        correlation_matrix,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        color_continuous_scale='Viridis',
        zmin=-1,
        zmax=1
    )

    fig.update_layout(
        title="Correlation Heatmap",
        width=600,  
        height=600,  
        xaxis=dict(tickfont=dict(size=8)),  
        yaxis=dict(tickfont=dict(size=8))   
    )

    return dcc.Graph(figure=fig)
