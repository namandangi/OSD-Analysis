### This will generate a basic dash datatable we can use to look at whatever data set we are loading..
## Can add pretty formatting later for bonus points

import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State
from helpers import load_dataset, generate_generic_DataTable
from dash import dcc
import plotly.express as px
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
import dash_ag_grid
from settings import memory
import plotly.graph_objects as go
import requests

# sampleCSVFile = "data/PosStats_MAP01938_0000_0E_01_region_001_labelled.csv"
sampleCSVFile = "data/PosStats_MAP01938_0000_0E_01_region_001.csv"


global_df = None


featureGraphs_row = dbc.Row(
    [
        dbc.Col(
            [html.Div(id="left-col-stats"), html.Div(id="class-info-graph")], width=4
        ),
        dbc.Col(
            dbc.Row(
                [
                    dcc.Slider(
                        0,
                        50000,
                        100,
                        value=10000,
                        id="area-slider",
                        marks=None,
                    ),
                    html.Div(id="middle-col-graph"),
                ]
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Row(
                [
                    dbc.Select(
                        id="featureList_selector",
                        style={"maxWidth": 300},
                    ),
                    html.Div(id="right-col-graph"),
                ]
            ),
            width=4,
        ),
    ]
)

@memory.cache
def get_feature_list(selected_image):    
    feature_list = []
    try:
        api_url = f'http://osd-analysis-api:85/get-features-by-image/{selected_image}?lmt={10000}'
        response = requests.get(api_url).json()
        feature_list = response['features']
        print(feature_list[0]["localFeatureId"])
    except Exception as e:
        print(f'Error fetching data: {e}')
    return feature_list


@memory.cache
def computeClusterSets(data, setSize=2000, n_clusters=9):
    df = pd.DataFrame(data)
    all_columns = df.columns.tolist()
    filtered_columns = [
        col
        for col in all_columns
        if col.startswith("Mean_") or col.startswith("Median_")
    ]

    # Save the other columns for later
    other_columns = df.drop(columns=filtered_columns)

    # Scale the filtered data
    scaler = StandardScaler()

    df[filtered_columns] = df[filtered_columns].fillna(df[filtered_columns].mean())

    cluster_data = scaler.fit_transform(df[filtered_columns])

    # Perform clustering
    cluster = AgglomerativeClustering(
        n_clusters=n_clusters, affinity="euclidean", linkage="ward"
    )
    labels = cluster.fit_predict(cluster_data[:1000])

    # Convert cluster_data back to a DataFrame and add the cluster labels
    cluster_data = pd.DataFrame(cluster_data, columns=filtered_columns, index=df.index)
    cluster_data["cluster_labels"] = labels

    # Concatenate the other columns back to the DataFrame
    # df = pd.concat([cluster_data, other_columns], axis=1)
    return pd.DataFrame()
    print(df.head())
    return df

# function to load metaDataTable_layout
@callback(Output("metaData_store", "data"), Input("initMetaDataDiv", "children"))
def loadMetaDataTable(_):
    api_url = 'http://osd-analysis-api:85/get-image-list'
    image_list = []
    try:
        response = requests.get(api_url)
        image_list = response.json()
        # print(f"image_list: {image_list}")
    except Exception as e:
        return html.Div(f'Error fetching data: {e}')
    return image_list




### This will likely change in the future, but this will load the current feature set using a hidden div as a trigger
@callback(Output("rawFeatureData_store", "data"), Input("initFeatureDiv", "children"), Input("image_select", "value"))
def loadFeatureData(_, selected_image):
    global df
       
    feature_list = get_feature_list(selected_image)
    df = pd.DataFrame(feature_list)
    
    dataStoreCols = [
        "localFeatureId",
        "Cell_Centroid_X",
        "Cell_Centroid_Y",
        "Cell_Area",
    ]
    
    filtered_df = df[dataStoreCols]
    df['cluster_labels'] = None
    
    print(filtered_df.head())
    return filtered_df.to_dict("records")


@callback(
    Output("featureList_selector", "options"),
    Output("featureList_selector", "value"),
    Input("rawFeatureData_store", "data"),
)
def updateFeatureList(clusterData):
    ## access the dataframe global variable and get those columns.
    all_columns = df.columns
    filtered_columns = [
        col
        for col in all_columns
        if col.startswith("Mean_" or col.startswith("Median_"))
    ]
    columnList = [{"label": col, "value": col} for col in filtered_columns]
    if(len(columnList) == 0):
        return [], []
    return columnList, columnList[0]["value"]


featureDataTable_layout = html.Div(
    [
        dcc.Store(id="rawFeatureData_store"),
        html.Div(id="initFeatureDiv", style={"display": "none"}),
        dcc.Store(id="metaData_store"),
        html.Div(id="initMetaDataDiv", style={"display": "none"}),
        featureGraphs_row,
    ]
)


@callback(Output("left-col-stats", "children"), Input("rawFeatureData_store", "data"))
def featureSetStabs_update(clusterData):
    numCellsInDataSet = len(clusterData)
    return html.H3(f"There are {numCellsInDataSet} objects in the current dataset")


@callback(
    Output("middle-col-graph", "children"),
    Input("rawFeatureData_store", "data"),
    Input("area-slider", "value"),
)
def generateObjectAreaGraph(clusterData, maxAreaValue):
    ## TO DO... add in some logic that sets the maximum X and or doesn't plot
    ## extreme outliers..
    global df

    fig = px.histogram(df[df.Cell_Area < maxAreaValue], x="Cell_Area")
    return dcc.Graph(figure=fig)


@callback(
    Output("class-info-graph", "children"),
    Input("rawFeatureData_store", "data"),
)
def generateClassDistroGraph(clusterData):
    ## TO DO... add in some logic that sets the maximum X and or doesn't plot
    ## extreme outliers..
    global df

    fig = go.Figure(data=[go.Pie(labels=df["cluster_labels"])])

    # fig = px.pie(df, x="cluster_labels")
    return dcc.Graph(figure=fig)

