from dash import html, Input, Output, State, dcc, callback, no_update, callback_context
import dash_paperdragon
from settings import gc, osdConfig
import dash_bootstrap_components as dbc
from settings import osdConfig, getId
import dash_bootstrap_components as dbc

import random
import json


def get_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgb({r}, {g}, {b})"


sampleTileSrc = {
    "label": "CDG Example",
    "value": 2,
    "tileSources": [
        {
            "tileSource": "https://candygram.neurology.emory.edu/api/v1/item/65240a2ec1ae16db59f790bb/tiles/dzi.dzi",
            "x": 0,
            "y": 0,
            "opacity": 1,
            "layerIdx": 0,
        }
    ],
}

mxif_osdViewer = dash_paperdragon.DashPaperdragon(
    id="osdMxif_viewer",
    viewerHeight=600,
    config=osdConfig,
    tileSources=sampleTileSrc["tileSources"],
    zoomLevel=0,
    viewportBounds={"x": 0, "y": 0, "width": 0, "height": 0},
    curMousePosition={"x": 0, "y": 0},
    inputToPaper=None,
    outputFromPaper=None,
    viewerWidth=1000,
)


simpleSelector = dbc.Col(
    [
        dbc.Select(
            id="sample_select",
            options=["MedStats", "PosStats"],
            style={"maxWidth": 300},
            value="PosStats",
            className="me-1",
        )
    ],
    width=1,
)


mouseDisplay = dbc.Col(
    dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6("Mouse Position", className="card-title"),
                    html.Div(id="mousePos_disp", className="card-text"),
                ]
            )
        ],
        className="img-control-grid",
        style={"height": "5rem", "margin": "10px"},
    ),
    width=2,
)


# @callback(
#     Output("debugOutputDiv", "children"),
#     Output("rawFeatureData_store", "data"),
#     Input("sample_select", "value"),
# )
# def updateDebugOutputDiv(value):
#     print("CLUSTER THE FARK OUT OF IT!!!")
#     return f"Selected {value}", no_update


genImageCluster = dbc.Col(
    [
        dbc.Button("Generate Image Cluster", id="genImageCluster", color="primary"),
        html.Div(id="debugOutputDiv"),
    ],
    width=2,
)


curObjDisp = dbc.Col([html.Div(id="curObject_disp", className="card-text")], width=4)

mxifViewer_layout = html.Div(
    [
        dbc.Row(
            [mouseDisplay, curObjDisp, genImageCluster, simpleSelector],
            style={"height": "100px"},
        ),
        dbc.Row(mxif_osdViewer),
        dbc.Button(id="redraw-overlay", color="primary"),
    ]
)


@callback(
    Output("curObject_disp", "children"), Input("osdMxif_viewer", "curShapeObject")
)
def update_curShapeObject(curShapeObject):

    print(curShapeObject, "is current shape detected..")
    if curShapeObject:
        return json.dumps(curShapeObject.get("userdata", {}))
    else:
        return no_update


# @callback(Output("debugOutputDiv", "children"),)
# def eventuallyGenerateImageCluster(n_clicks):
#     print("Generating Image Cluster")
#     return f"Clicked {n_clicks} times"

colorPalette = ["red", "green", "blue", "orange", "yellow"]


@callback(
    Output("osdMxif_viewer", "inputToPaper"),
    Input("rawFeatureData_store", "data"),
    Input("redraw-overlay", "n_clicks"),
    Input("genImageCluster", "n_clicks"),
)
def renderCellsonOSDViewer(clusterData, redrawClicked, genImageClusterClicked):
    print(f"cluster data: {clusterData[0]}")

    ctx = callback_context.triggered_id

    shapesToAdd = []
    for idx, s in enumerate(
        clusterData[:10000]
    ):  ### Just do the first 500 rows for now

        color = get_random_color()
        if "genImageCluster" in ctx and genImageClusterClicked is not None:
            # print("You were clickity clackity", genImageClusterClicked)
            color = colorPalette[idx % len(colorPalette)]

        si = get_circle_instructions(
            int(s["Cell_Centroid_X"]),
            int(s["Cell_Centroid_Y"]),
            4,
            color,  ## TO MAKE BASED ON CLASS..
            {"class": "cell", "allDaStuff": s},
        )
        shapesToAdd.append(si)
    print(f"shapes:  {shapesToAdd[0]}")
    return {
        "actions": [
            {"type": "clearItems"},
            {"type": "drawItems", "itemList": shapesToAdd},
        ]
    }


## This updates the mouse tracker output
@callback(
    Output("mousePos_disp", "children"), Input("osdMxif_viewer", "curMousePosition")
)
def update_mouseCoords(curMousePosition):
    return (
        f'{int(curMousePosition["x"])},{int(curMousePosition["y"])}'
        if curMousePosition["x"] is not None
        else ""
    )

# @callback(
#     # Output("osdMxif_viewer", "inputToPaper"), 
#     Output("currPoint_disp", "children"),
#     Input("osdMxif_viewer", "curMousePosition"),
#     Input("rawFeatureData_store", "data"),
# )
# def update_curCursor(curMousePosition, clusterData):

#     return (
#         f'{int(curMousePosition["x"])},{int(curMousePosition["y"])}'
#         if curMousePosition["x"] is not None
#         else ""
#     )
#     # return {
#     #     "actions": [
#     #         {"type": "clearItems"},
#     #         {"type": "drawItems", "itemList": shapesToAdd},
#     #     ]
#     # }

# {'label': 1, ']': 1726, 'centroid-0': 214.33545770567787, 'centroid-1': 3238.139049826188, 'intensity_mean_ACTININ': 1377.1819184123483, 'intensity_mean_BCATENIN': 5453.981256890849, 'intensity_mean_CD11B': 70.35170893054024, 'intensity_mean_CD20': 222.2844542447629, 'intensity_mean_CD3D': 2814.541345093716, 'intensity_mean_CD45B': 0, 'intensity_mean_CD45': 122.56339581036384, 'intensity_mean_CD4': 794.1565600882029, 'intensity_mean_CD68': 1089.0738699007718, 'intensity_mean_CD8': 476.13340683572216, 'intensity_mean_CGA': 110.7805953693495, 'intensity_mean_COLLAGEN': 424.9173098125689, 'intensity_mean_COX2': 693.9834619625137, 'intensity_mean_DAPI': 2043.550165380375, 'intensity_mean_ERBB2': 1225.8202866593165, 'intensity_mean_FOXP3': 0, 'intensity_mean_GACTIN': 2672.4189636163173, 'intensity_mean_HLAA': 4471.524807056229, 'intensity_mean_LYSOZYME': 123.78610804851158, 'intensity_mean_MUC2': 1057.851157662624, 'intensity_mean_NAKATPASE': 2098.327453142227, 'intensity_mean_OLFM4': 145.1047409040794, 'intensity_mean_PANCK': 8892.259095920617, 'intensity_mean_PCNA': 272.10363836824695, 'intensity_mean_PDL1': 1.0871003307607496, 'intensity_mean_PEGFR': 1813.5038588754132, 'intensity_mean_PSTAT3': 670.1907386990077, 'intensity_mean_SMA': 37.18853362734289, 'intensity_mean_SNA': 3938.1642778390296, 'intensity_mean_SOX9': 179.20948180815876, 'intensity_mean_VIMENTIN': 0.0209481808158765, 'epithelial': 1, 'slide': 'MAP01938_0000_0E_01', 'region': 1}


### Create a callback to render the points on the image


#   si = get_box_instructions(
#             paperOutput["data"]["point"]["x"],
#             paperOutput["data"]["point"]["y"],
#             paperOutput["data"]["size"]["width"],
#             paperOutput["data"]["size"]["height"],
#             colors[0],
#             {"class": classes[0]},
#         )
#         currentShapeData.append(si)

def get_box_instructions(x, y, w, h, color, userdata={}):
    props = osdConfig.get("defaultStyle") | {
        "point": {"x": x, "y": y},
        "size": {"width": w, "height": h},
        "fillColor": color,
        "strokeColor": color,
    }
    userdata["objectId"] = getId()
    command = {"paperType": "Path.Rectangle", "args": [props], "userdata": userdata}

    return command


def get_circle_instructions(x, y, r, color, userdata={}):
    props = osdConfig.get("defaultStyle") | {
        "center": [x, y],
        "radius": r,
        "fillColor": color,
        "strokeColor": color,
        "fillOpacity": 0.01,
    }
    userdata["objectId"] = getId()
    command = {"paperType": "Path.Circle", "args": [props], "userdata": userdata}

    return command


# # def generateMultiVizGraph(imageName):
# #     imageMetadata = {}

# #     #  html.P(f"ScaleFactor X:{image_info['scaleX']}")
# #     # print("Received", imageName)
# #     if imageName == "demo":
# #         img = Image.open("sample_image_for_pointdata.png")
# #         width, height = img.size
# #         ## TO DO IS CHANGE THIS IMAGE

# #         tileMetadata = gc.get(f"item/{imgId}/tiles")

# #         tileMetadata["scaleX"] = tileMetadata["sizeX"] / width
# #         tileMetadata["scaleY"] = tileMetadata["sizeY"] / height

# #         img_array = np.array(img)

# #         fig = make_subplots(
# #             rows=1, cols=1, subplot_titles=("Image with Cluster Points",)
# #         )
# #         fig.add_trace(go.Image(z=img_array), 1, 1)
# #         # fig = px.imshow(img_array)
# #         fig.update_layout(
# #             margin=dict(t=2, r=2, b=2, l=2)
# #         )  ## removed width=800, height=600,

# #         # Display image

# #         fig.update_layout(
# #             margin=dict(t=6, b=5, l=2, r=2),  # Adjust these values as needed
# #             dragmode="drawrect",
# #             shapes=[],
# #             # dragmode="select",
# #         )
# #         fig.update_xaxes(range=[0, width])
# #         fig.update_yaxes(range=[0, height], scaleanchor="x")

# #         return fig, tileMetadata

# #     return None, None
# # mcHoverDataGraph = dcc.Graph(
# #     id="activeObject-chart",
# #     style={
# #         "width": "25%",
# #         "display": "inline-block",
# #         "vertical-align": "top",
# #         "margin": "0px",
# #         "padding": "0px",
# #     },
# # )


# import dash_bootstrap_components as dbc
# import pandas as pd
# from PIL import Image
# import json, pickle, dash, time
# from ..utils.helpers import load_dataset, generate_generic_DataTable

# # from diskcache import Cache
# # import time
# # import plotly.subplots as sp
# import numpy as np
# import plotly.express as px
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# import girder_client

# ## Adding locla cache here
# from diskcache import FanoutCache

# ## Create cacheing here, may want to add a button to clear cache at some point
# ## Currently I just delete it from the disk
# cache_directory = ".localDashDiskCache"
# cache = FanoutCache(directory=cache_directory, shards=4)

# sampleCSVFile = "PosStats_MAP01938_0000_0E_01_region_001_labelled.csv"


# # @cache.memoize()
# # def loadSegmentResults(csvFileName):
# #     data_df = pd.read_csv(csvFileName)
# #     ## May do some of the type casting here as well...
# #     print(data_df.head())
# #     return data_df


# # st = time.time()
# # et = time.time()

# # # get the execution time
# # elapsed_time = et - st
# # print("Execution time:", elapsed_time, "seconds")

# # data_df = loadSegmentResults(sampleCSVFile)

# ### Helper functions to pull and visualize multichannel images from the DSA

# mcGraph = dcc.Graph(
#     id="multiChannel-graph",
#     style={
#         "width": "100%",
#         "margin": "0px",
#         "padding": "0px",
#         "display": "inline-block",
#         "vertical-align": "top",
#     },
#     config={
#         "staticPlot": False,
#         "displayModeBar": False,
#         "modeBarButtonsToAdd": ["drawrect"],
#     },
# )

# mcROIgraph = dcc.Graph(
#     id="multiChannel-ROI-graph",
#     style={
#         "width": "100%",
#         "margin": "0px",
#         "padding": "0px",
#         "display": "inline-block",
#         "vertical-align": "top",
#     },
#     config={
#         "staticPlot": False,
#         "displayModeBar": False,
#         # "modeBarButtonsToAdd": ["drawrect"],
#     },
# )


# imageView_layout = html.Div(
#     [
#         dbc.Row(
#             [
#                 dbc.Select(
#                     id="imageFeatureSet_select",
#                     options=["MedStats", "PosStats"],
#                     style={"maxWidth": 300},
#                     value="PosStats",
#                     className="me-1",
#                 ),
#                 dbc.Select(
#                     id="imageToRender_select",
#                     options=["anotherdemo"],
#                     style={"maxWidth": 300},
#                     value="anotherdemo",
#                 ),
#                 dbc.Select(
#                     id="viewportSize_select",
#                     options=[256, 512, 768, 1024],
#                     value=256,
#                     style={"display": "inline-block", "maxWidth": 200},
#                     className="me-1",
#                 ),
#                 dbc.Container(
#                     [
#                         dbc.Select(
#                             options=[],
#                             id="frame_select",
#                             value=0,
#                             className="me-1",
#                         ),
#                     ],
#                     style={"display": "inline-block", "maxWidth": 300},
#                 ),
#             ],
#         ),
#         dbc.Row(
#             [
#                 dbc.Col(html.Div(id="mouseTracker"), width=6),
#                 dbc.Col(html.Div(id="curROI_disp"), width=6),
#             ]
#         ),  ### Mouse tracker should be on its own line..
#         dbc.Row(
#             [
#                 dbc.Col(mcGraph, width=4),
#                 dbc.Col(
#                     [html.Div(id="graph-metadata"), html.Div(id="roiDispArea")],
#                     width=8,
#                 ),
#             ]
#         ),
#         dbc.Row(
#             dbc.Collapse(
#                 [html.Div(id="displayedPoints_table")],
#                 is_open=True,
#             ),
#             style={"maxHeight": 200},
#         ),
#         dbc.Row(
#             [
#                 html.Div(id="scalingProperties"),
#                 dcc.Store("curImageProps_store"),
#                 dcc.Store("curROI_store", data={}),
#                 dcc.Store("clusterData_store", data=[]),  ## Load the initial file
#             ]
#         ),
#     ]
# )


# ### FYI... THIS IS THE PART THAT TAKES LONG... PUSHING ALL THE DATA TO THE LOCAL DATASTORE
# ## I can probably refactor this significantly...


# ## TO DO: ADD error handling if file doesn't exist
# @callback(Output("clusterData_store", "data"), Input("imageFeatureSet_select", "value"))
# # @cache.memoize()
# def updateClusterDataStore(statsType):
#     statsFileName = f"{statsType}_MAP01938_0000_0E_01_region_001_labelled.csv"

#     data = pd.read_csv(statsFileName)
#     try:
#         data.Cell_Centroid_X = data.Cell_Centroid_X.astype(int)
#         data.Cell_Centroid_Y = data.Cell_Centroid_Y.astype(int)
#     except:
#         print("Input file is missing centroid params..")

#     ## So the delay is happening here... loading all those points for whatever reason takes an oddly long time
#     return data.to_dict()


# ### This will generate a table of the points being displayed
# @callback(
#     Output("displayedPoints_table", "children"), Input("clusterData_store", "data")
# )
# # @cache.memoize()
# def generateClusterDataTable(cluster_data):
#     ## irritatingly I think I need to comnvert this back to a dataframe for the table..
#     ## maybe i need to determine the file typei n the function to make it simpler
#     return generate_generic_DataTable(
#         pd.DataFrame(cluster_data)[0:100], "clusterDataTable_table"
#     )


# ### Now let's listen for click events, and for now we will NOT draw an ROI on the image as it
# ## is taking a weird amount of time, but we will actually generate the zoomed in image and display that


# # @cache.memoize()
# def getImageROI_fromGirder(imageId, startX, startY, roiSize, frameNum=0):
#     """Returns a numpy array of an image at base resolution at coordinates
#     startX, startY of width/height=roiSize"""
#     imageUrl = f"item/{imageId}/tiles/region?left={startX}&top={startY}&regionWidth={roiSize}&regionHeight={roiSize}&frame={frameNum}&encoding=pickle"

#     try:
#         imageData = gc.get(
#             imageUrl,
#             jsonResp=False,
#         )
#     except:
#         print("Image Data Query failed... DOH")

#     imageNP_array = pickle.loads(imageData.content)

#     return imageNP_array


# ## This stores the coordinates of the ROI that was just selected/clicked on the left Image
# @callback(Output("curROI_disp", "children"), Input("curROI_store", "data"))
# def updateCurrentROIinfo(curRoiInfo):
#     return html.Div(json.dumps(curRoiInfo))


# # ## TO BE DEBUGGED
# @callback(
#     Output("roiDispArea", "children"),
#     Output("curROI_store", "data"),
#     Input("multiChannel-graph", "clickData"),
#     Input("curImageProps_store", "data"),
#     Input("viewportSize_select", "value"),
#     Input("clusterData_store", "data"),
# )
# def renderROI_image(clickData, imageProps, viewportSize, clusterData):
#     if clickData:
#         x = clickData["points"][0]["x"]
#         y = clickData["points"][0]["y"]

#         startX = x * float(imageProps["scaleFactor"])
#         startY = y * float(imageProps["scaleFactor"])
#         region_np = getImageROI_fromGirder(
#             imageProps["imageId"], startX, startY, viewportSize
#         )
#         image_squeezed = np.squeeze(region_np)
#         fig = px.imshow(image_squeezed)
#         fig = go.Figure(fig)

#         data_df = pd.DataFrame(clusterData)

#         data_df["x_centroid"] = data_df["Cell_Centroid_X"].astype(int)
#         data_df["y_centroid"] = data_df["Cell_Centroid_Y"].astype(int)
#         print(data_df.head())
#         filtefet__data = data_df[
#             (
#                 (data_df["x_centroid"] >= startX)
#                 & (data_df["x_centroid"] <= (startX + int(viewportSize)))
#             )
#             & (
#                 (data_df["y_centroid"] >= startY)
#                 & (data_df["y_centroid"] <= (startY + int(viewportSize)))
#             )
#         ]
#         cluster_labels = filtered_data["cluster_labels"].tolist()
#         # print(data_df.head())

#         x_values = filtered_data["x_centroid"].tolist()
#         y_values = filtered_data["y_centroid"].tolist()

#         x_values_rescaled = [(x - startX) for x in x_values]
#         y_values_rescaled = [(y - startY) for y in y_values]

#         ids = [chr(ord("A") + i) for i in range(len(x_values))]

#         valid_colors = ["red", "yellow", "green"]
#         marker_colors = [
#             valid_colors[label % len(valid_colors)] for label in cluster_labels
#         ]
#         marker_text = [f"Cluster: {label}" for label in cluster_labels]

#         # marker_text = [f"Cluster: {label}" for label in cluster_labels]

#         points = pd.DataFrame(
#             {
#                 "x": x_values_rescaled,
#                 "y": y_values_rescaled,
#                 "id": ids,
#                 "text": marker_text,
#                 "color": marker_colors,
#             }
#         )

#         # Add the scatter plot
#         fig.add_trace(
#             go.Scatter(
#                 x=points["x"],
#                 y=points["y"],
#                 text=points["text"],
#                 mode="markers",
#                 marker=dict(size=6, color=marker_colors),
#             )
#         )

#         fig_dict = fig.to_dict()
#         return dcc.Graph(
#             figure=fig,
#             style={
#                 "width": "100%",
#                 "margin": "0px",
#                 "padding": "0px",
#                 "display": "inline-block",
#                 "vertical-align": "top",
#             },
#             config={
#                 "staticPlot": False,
#                 "displayModeBar": False,
#                 # "modeBarButtonsToAdd": ["drawrect"],
#             },
#         ), {"startX": startX, "startY": startY, "viewportSize": viewportSize}
#     # generate_generic_DataTable(filtered_data, "filtered_points")
#     else:
#         return None, None


# # # ### This won't do anything yet other than load the only Image I have locally saved...
# @callback(
#     Output("mouseTracker", "children"),
#     Input("multiChannel-graph", "hoverData"),
#     Input("curImageProps_store", "data"),
# )
# def trackMousePositionOnMCGraph(hoverData, imageProps):
#     # print(relayoutData)

#     if hoverData:
#         scaleFactor = imageProps["scaleFactor"]

#         x = hoverData["points"][0]["x"]  # * scaleFactor
#         y = hoverData["points"][0]["y"]  # * scaleFactor

#         # roiImage_np = getImageROI_fromGirder(sampleImageId, x, y, 512)
#         return html.Div(
#             f"localX: {x} localY: {y} globalX: {x*scaleFactor:.4f} globalY: {y*scaleFactor:.4f}"
#         )


# @callback(
#     Output("multiChannel-graph", "figure"),
#     Output("curImageProps_store", "data"),
#     Output("frame_select", "options"),
#     Input("imageToRender_select", "value"),
#     Input("frame_select", "value"),
# )
# # @cache.memoize()
# def loadBaseMultiChannelImage(imageName, frameNum):
#     ## This actually only loads a single image, because I don't have more than one local image to use for this..
#     imageProps = {}
#     if imageName == "anotherdemo":
#         imageId = "649b78f3fbfabbf55f16fb0f"
#         tileData = gc.get(f"item/{imageId}/tiles")
#         imageProps = tileData
#         imageProps["imageId"] = imageId
#         thumbnailWidth = 768
#         imageProps["thumbnailWidth"] = thumbnailWidth

#         imageProps["scaleFactor"] = imageProps["sizeX"] / thumbnailWidth

#         ## Retrieve the currently selected image as a numpy array... or an image.. to be determined
#         imageThumbnail_data = gc.get(
#             f"item/{imageId}/tiles/thumbnail?width={thumbnailWidth}&frame={frameNum}&encoding=pickle",
#             jsonResp=False,
#         )
#         thumb_np = pickle.loads(imageThumbnail_data.content)

#         image_squeezed = np.squeeze(thumb_np)

#         fig = px.imshow(image_squeezed)
#         # Convert the figure to a dictionary
#         fig_dict = fig.to_dict()
#         # print(imageProps["channelmap"])
#         frameOptions = [
#             {"label": k, "value": v} for k, v in imageProps["channelmap"].items()
#         ]

#         return (fig_dict, imageProps, frameOptions)
#     return dash.no_update, dash.no_update, dash.no_update


# ## Bind/display the imageProps dictionary .. for now we can keep it ugly
# # @callback(Output("scalingProperties", "children"), Input("curImageProps_store", "data"))
# # def updateCurImageProps(data):
# #     ## We need to format this and make it prettier, for now I am just dumpign the contents..
# #     return html.Div(json.dumps(data))


# # encoded_style_value = "%7B%22bands%22:%20%5B%7B%22frame%22:%200,%20%22palette%22:%20%5B%22#000000%22,%20%22#0000ff%22%5D,%20%22min%22:%20%22auto%22,%20%22max%22:%20%22auto%22%7D,%20%7B%22frame%22:%201,%20%22palette%22:%20%5B%22#000000%22,%20%22#00ff00%22%5D,%20%22max%22:%20%22auto%22%7D,%20%7B%22frame%22:%202,%20%22palette%22:%20%5B%22#000000%22,%20%22#ff0000%22%5D,%20%22max%22:%20%22auto%22%7D%5D%7D"

# # # Decode the style parameter value
# # decoded_style_value = urllib.parse.unquote(encoded_style_value)


# def generateImageMetadataPanel(imageMetadata):
#     ### Given a dictionary, should generate a formatted panel with the relevant info
#     if imageMetadata:
#         info_content = html.Div(
#             [
#                 html.H5("Image Information"),
#                 # html.P(f"Levels: {image_info['levels']}"),
#                 html.P(f"Size X: {imageMetadata.get('sizeX',{})}"),
#                 html.P(f"Size Y: {imageMetadata.get('sizeY',{})}"),
#                 # html.P(f"Tile Height: {image_info['tileHeight']}"),
#                 # html.P(f"Tile Width: {image_info['tileWidth']}"),
#                 html.P(f"ScaleFactor X:{imageMetadata['scaleX']:.4f}"),
#                 html.P(f"ScaleFactor Y:{imageMetadata['scaleY']:.4f}"),
#             ],
#             style={"margin": "10px"},
#         )
#         return info_content


# # # Convert the image to a numpy array
# # img_array = np.array(img)


# # def getImageData(imageName):
# #     print("Getting image data for imageName??")

# #     if imageName == "demo":
# #         # Load the image using PIL
# #         # Sample points

# #         num_points = len(points)
# #         random_colors = [
# #             "#%02x%02x%02x" % (int(r), int(g), int(b))
# #             for r, g, b in np.random.randint(0, 255, size=(num_points, 3))
# #         ]
# #         points["color"] = random_colors

# #     return imageName


# # import dash
# # from dash import html, Input, Output, State, dcc, callback
# # import dash_bootstrap_components as dbc
# # from src.utils.multiChannelHelpers import (
# #     generateMultiVizGraph,
# #     generateImageMetadataPanel,
# # )
# # import pandas as pd
# # import random

# # ## This is the button set to control the graph , this is just a placeholder until I add more
# # ## Functionality
# # viz_control_layout = html.Div(
# #     [
# #         dbc.Button(
# #             "Graph Random PtSet",
# #             id="btn-graph-ptSet",
# #             className="me-1",
# #             color="success",
# #             style={"display": "inline-block"},
# #         ),
# #         dbc.Button(
# #             "Get New PtSet",
# #             id="btn-add-random-points",
# #             className="me-1",
# #             style={"display": "inline-block"},
# #         ),
# #         dbc.Button(
# #             "PlotClusterPts",
# #             id="btn-plot-clusterPoints",
# #             className="me-1",
# #             style={"display": "inline-block"},
# #         ),
# #     ]
# # )


# # mcv_layout = html.Div(
# #     [
# #         dcc.Store("imageInfo_store"),
# #         dcc.Store("graph-data-store"),
# #         dcc.Store("activePointList_store"),
# #         dbc.Row(viz_control_layout),
# #         dbc.Row(
# #             [
# #                 dbc.Col(id="imageInfo_panel", width=2),
# #                 dbc.Col([mcGraph], id="graph_panel", width=8),
# #             ]
# #         ),
# #     ]
# # )


# # ### Currently using the output from btn-graph-ptSet to initialize the graph


# # @callback(Output("imageInfo_panel", "children"), Input("imageInfo_store", "data"))
# # def updateImageMetadataPanel(imageMetadata):
# #     return generateImageMetadataPanel(imageMetadata)


# # @callback(
# #     Output("activePointList_store", "data"), Input("btn-plot-clusterPoints", "n_clicks")
# # )
# # def plotClusterPoints(n_clicks):
# #     print("YO")


# # # @callback(
# # #     [Output("graph-data-store", "data"), Output("imageInfo_store", "data")],
# # #     Input("btn-graph-ptSet", "n_clicks"),
# # # )
# # # def initMainGraph(n_clicks):
# # #     graph_layout, imageMetadata = generateMultiVizGraph("demo")
# # #     print("Received", imageMetadata)
# # #     return graph_layout, imageMetadata


# # # @callback(
# # #     Output("graph-data-store", "data"),
# # #     [Input("btn-add-random-points", "n_clicks")],
# # #     [State("graph-data-store", "data")],
# # # )
# # # def add_random_points(n_clicks, current_figure):
# # #     if not n_clicks:
# # #         return dash.no_update

# # #     # Generate random points (you can modify this as needed)
# # #     points = pd.DataFrame(
# # #         {
# # #             "x": [50, 100, 150, 200, 250],
# # #             "y": [50, 100, 150, 200, 600],
# # #             "id": ["A", "B", "C", "D", "E"],
# # #         }
# # #     )

# # #     # Add a scatter trace with the random points
# # #     new_trace = {
# # #         "type": "scatter",
# # #         "mode": "markers",
# # #         "x": points["x"],
# # #         "y": points["y"],
# # #         "text": points["id"],
# # #         "marker": {"size": 10, "color": "red"},
# # #     }

# # #     # Append the new trace to the current data
# # #     if "data" in current_figure:
# # #         current_figure["data"].append(new_trace)
# # #     else:
# # #         current_figure["data"] = [new_trace]

# # #     return current_figure


# # # https://github.com/plotly/dash-world-cell-towers
# # # @callback(
# # #     Output("multiChannel-graph", "figure"),
# # #     [Input("graph-data-store", "data")],
# # # )
# # # def update_graph(data):
# # #     return data
# # def getPointsToGraph(ptName, minX=100, maxX=500, minY=150, maxY=660, num_points=5):
# #     x_values = [random.randint(minX, maxX) for _ in range(num_points)]
# #     y_values = [random.randint(minY, maxY) for _ in range(num_points)]
# #     ids = ["Pt_" + str(i) for i in range(num_points)]

# #     new_points = pd.DataFrame(
# #         {
# #             "x": x_values,
# #             "y": y_values,
# #             "id": ids,
# #         }
# #     )

# #     return new_points


# # # def getPointsToGraph(ptName, minX=100, maxX=500, minY=150, maxY=660):
# # #     new_points = pd.DataFrame(
# # #         {
# # #             "x": [50, 100, 150, 200, 250],
# # #             "y": [50, 100, 150, 200, 600],
# # #             "id": ["A", "B", "C", "D", "E"],
# # #         }
# # #     )


# # @callback(
# #     [Output("multiChannel-graph", "figure"), Output("imageInfo_store", "data")],
# #     [Input("btn-graph-ptSet", "n_clicks"), Input("btn-add-random-points", "n_clicks")],
# #     [State("multiChannel-graph", "figure")],
# # )
# # def update_graph(btn1, btn2, current_figure):
# #     ctx = dash.callback_context
# #     if not ctx.triggered:
# #         ## Need this to fire on init so there's something graphed, this will eventually
# #         ## get smarted and look for an image as well
# #         graph_layout, imageMetadata = generateMultiVizGraph("demo")
# #         return graph_layout, imageMetadata
# #     else:
# #         button_id = ctx.triggered[0]["prop_id"].split(".")[0]

# #     if button_id == "btn-graph-ptSet":
# #         graph_layout, imageMetadata = generateMultiVizGraph("demo")
# #         return graph_layout, imageMetadata

# #     elif button_id == "btn-add-random-points":
# #         # Generate new points
# #         current_figure["data"] = [
# #             trace
# #             for trace in current_figure["data"]
# #             if trace.get("legendgroup") != "random_points"
# #         ]

# #         new_points = getPointsToGraph("demo")
# #         for index, row in new_points.iterrows():
# #             current_figure["data"].append(
# #                 dict(
# #                     x=[row["x"]],
# #                     y=[row["y"]],
# #                     mode="markers",
# #                     marker=dict(color="red", size=10),
# #                     hoverinfo="text",
# #                     showlegend=False,
# #                     legendgroup="random_points"
# #                     # text=row["id"],
# #                     # name=row["id"],
# #                 )
# #             )
# #         return current_figure, dash.no_update

# #     else:
# #         return dash.no_update, dash.no_update


# # html.Hr(),
# # html.H6("Frames:"),
# # # html.Ul(
# # #     [
# # #         html.Li(f"Frame: {frame['Frame']}, Index: {frame['Index']}")
# # #         for frame in image_info["frames"]
# # #     ]
# # # ),
