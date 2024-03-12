from dash import html, Input, Output, State, dcc, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import seaborn as sns
from ..utils.helpers import load_dataset, generate_generic_DataTable
from dash import dcc
from sklearn.preprocessing import StandardScaler
import scipy.cluster.hierarchy as shc
import plotly.figure_factory as ff
import plotly.graph_objs as go

sampleCSVFile = "MAP01938_0000_0E_01_region_001_quantification.csv"
df = load_dataset(sampleCSVFile)


dendogram_layout = html.Div([
    html.H1("Dendogram"),
    dcc.Store(id="rawFeatureDataSet", data=df.to_dict("records")),
    dbc.Row(id="dendogram-graph")
]
)
@callback(Output("dendogram-graph","children"),
        Input("rawFeatureDataSet","data")
)
def update_dendrogram(clusterData):
    df = pd.DataFrame(clusterData)
    all_columns = df.columns
    filtered_columns = [col for col in all_columns if col.startswith('intensity')]
    data = df[filtered_columns]
    scaler = StandardScaler()
    data[filtered_columns] = scaler.fit_transform(data[filtered_columns])
    columns_to_drop = ['intensity_mean_CD11B', 'intensity_mean_CD45B', 'intensity_mean_FOXP3', 'intensity_mean_PDL1']
    data = data.drop(columns=columns_to_drop, axis=1)
    subset_data = data.iloc[0:2000]
    dendrogram_fig = ff.create_dendrogram(subset_data, labels=None)
    fig = go.Figure(data=dendrogram_fig)
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(width=800, height=600)
    return dcc.Graph(figure=fig)
