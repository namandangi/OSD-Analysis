from dash import html, Input, Output, State, dcc, callback, no_update, callback_context
import dash_paperdragon
from settings import gc, osdConfig
import dash_bootstrap_components as dbc
from settings import osdConfig, getId
import dash_bootstrap_components as dbc
import requests

import random
import json

defaultImageID = "65240a2ec1ae16db59f790bb"
defaultImageName = "test"

def get_random_color(seed = None, decay = 1):
    random.seed(seed)
    r = random.randint(0, 255) * decay
    g = random.randint(0, 255) * decay
    b = random.randint(0, 255) * decay
    return f"rgb({r}, {g}, {b})"

def decrease_expo(initial_opacity, decay_factor):
    return initial_opacity * decay_factor

def getTileSource(imageID, imageName):
    tileSrc = {
        "label": imageName,
        "value": 2,
        "tileSources": [
            {
                "tileSource": f"https://candygram.neurology.emory.edu/api/v1/item/{imageID}/tiles/dzi.dzi",
                "x": 0,
                "y": 0,
                "opacity": 1,
                "layerIdx": 0,
            }
        ],
    }
    return tileSrc
    

sampleTileSrc = getTileSource(defaultImageID, defaultImageName)

@callback(
    Output("osdMxif_viewer", "tileSources"),
    Input("image_select", "value"),
    State("metaData_store", "data"),
)
def update_tile_source(selected_image_id, meta_data):
    if not meta_data:
        raise PreventUpdate

    selected_image_data = next((data for data in meta_data if data['imageId'] == selected_image_id), None)

    if selected_image_data:
        tile_source = getTileSource(selected_image_id, selected_image_data['imageName'])
        return tile_source["tileSources"]
    else:
        raise PreventUpdate


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

# drop down selector to chose images and tile sources
imageSelector = dbc.Col(
    [
        dcc.Dropdown(
            id="image_select",
            style={"maxWidth": 300},
        )
    ]
)

@callback(
    Output("image_select", "options"),
    Output("image_select", "value"),
    Input("metaData_store", "data"),
)
def populate_image_selector(metaData):
    if not metaData:
        raise PreventUpdate

    options = [{'label': data['imageName'], 'value': data['imageId']} for data in metaData]
    value = metaData[0]['imageId'] if metaData else None # keep the first iamge as the default image
    return options, value


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


genImageCluster = dbc.Col(
    [
        dbc.Button("Generate Image Cluster", id="genImageCluster", color="primary"),
        html.Div(id="debugOutputDiv"),
    ],
    width=2,
)


curObjDisp = dbc.Col([html.Div(id="curObject_disp", className="card-text")], width=4)


order_by_opts = [{'label': 'Cell Area', 'value': 'Cell_Area'},
                 {'label': 'Nuc_Area', 'value': 'Nuc_Area'},
                 {'label': 'Cyt_Area', 'value': 'Cyt_Area'},
                 {'label': 'Mem Area', 'value': 'Mem_Area'},
                 {'label': 'Percent Stroma', 'value': 'Percent_Stroma'},
                 {'label': 'Percent Epithelium', 'value': 'Percent_Epithelium'},
                 ]

menu_opts = dbc.Col([
    dbc.Row(html.Div([html.Label('Radius: '), dcc.Input(id='radius-input', type='number', value=400, min=0, step=1)])),
    dbc.Row(html.Div([html.Label('Limit: '), dcc.Input(id='limit-input', type='number', value=250, min=1, step=1) ])),
    dbc.Row(html.Div([html.Label('Criteria:'),dcc.Dropdown(id='criteria-dropdown',options=order_by_opts,value='Cell_Area')])),
    dbc.Row(dbc.Button("Find Similar", id="find-similar", color="primary"), style={"left-margin": "1em"}),
    dcc.Store(id='state')
])

mxifViewer_layout = html.Div(
    [
        dbc.Row(
            [mouseDisplay, curObjDisp, menu_opts, genImageCluster, imageSelector],
            style={"height": "150px"},
        ),
        dbc.Row(mxif_osdViewer),
        dbc.Row(dbc.Button("Plot Points", id="redraw-overlay", color="primary"), style={"left-margin": "1em"})
        
    ]
)


@callback(
    Output("curObject_disp", "children"), Input("osdMxif_viewer", "curShapeObject"), Input("state", "data")
)
def update_curShapeObject(curShapeObject, data):

    # print("is current shape detected..", data)
    keys_to_include = ['UniqueID', 'Cell_Centroid_X', 'Cell_Centroid_Y', 'Cell_Area']    
    if curShapeObject:
        data = curShapeObject.get("userdata", {}).get("allDaStuff", {})
        extracted_data = {key: data[key] for key in keys_to_include if key in data}
        return json.dumps(extracted_data)
    else:
        return no_update


colorPalette = ["red", "green", "blue", "orange", "yellow"]

def renderAllCells(ctx, clusterData, genImageClusterClicked):
    shapesToAdd = []
    for idx, s in enumerate(
        clusterData[:15]
    ):  ### Just do the first 500 rows for now

        color = get_random_color()
        if "genImageCluster" in ctx and genImageClusterClicked is not None:
            color = colorPalette[idx % len(colorPalette)]

        si = get_circle_instructions(
            int(s["Cell_Centroid_X"]),
            int(s["Cell_Centroid_Y"]),
            4,
            color,  ## TO MAKE BASED ON CLASS..
            0.5,
            {"class": "cell", "allDaStuff": s},
        )
        shapesToAdd.append(si)
    # print(f"shapes:  {shapesToAdd[0]}")
    return {
        "actions": [
            {"type": "clearItems"},
            {"type": "drawItems", "itemList": shapesToAdd},
        ]
    }
    
@callback(
    Output('state', 'data'),
    Input("radius-input", "value"),
    Input("limit-input", "value"),
    Input("criteria-dropdown", "value"),
    Input("osdMxif_viewer", "curShapeObject"),
    State("state", "data")
)
def updateState(radius, limit, criteria, currObj, state):
    if currObj is None and state is not None:
        currObj = state['currObj'] # keep the currObj as it is --> reset it to last non null obj
    return {
        "radius": radius,
        "limit": limit,
        "criteria": criteria,
        "currObj": currObj
    }
    
@callback(
    Output("osdMxif_viewer", "inputToPaper"),
    Input("rawFeatureData_store", "data"),    
    Input("redraw-overlay", "n_clicks"),
    Input("genImageCluster", "n_clicks"),
)
def renderCellsonOSDViewer(clusterData, redrawClicked, genImageClusterClicked):
    # print(f"cluster data: {clusterData[0]}")

    ctx = callback_context.triggered_id
    result = renderAllCells(ctx, clusterData, genImageCluster)

    return result


@callback(
    Output("osdMxif_viewer", "inputToPaper", allow_duplicate=True),
    Input("find-similar", "n_clicks"),
    State("state", "data"),
    State("metaData_store", "data"),
    prevent_initial_call=True
)
def renderSimilarCells(similarClicked, state, metadata):
    shapesToAdd = [state["currObj"]]
    print("testsssds", state["currObj"])
    payload = {
    'x': state["currObj"]["userdata"]["allDaStuff"]["Cell_Centroid_X"],
    'y': state["currObj"]["userdata"]["allDaStuff"]["Cell_Centroid_Y"],
    'dst': state["radius"],
    'imageID': metadata[0]["imageId"],    
    'lmt': state["limit"],
    'order_list': state["criteria"]
    }
    # container name to allow 2 containers to talk with each other since they are in the same network
    api_url = 'http://osd-analysis-api:85/get-similar-feat'
    
    print(api_url, payload)
    try:
        response = requests.get(api_url, params=payload)
        neighbors = response.json()
        opacity = 1
        color_seed = 123
        color_decay_rate = 1
        radius = 12
        print(len(neighbors))
        for neigh in neighbors:
            radius = decrease_expo(radius, 0.992)
            color_decay_rate = decrease_expo(color_decay_rate, 0.992)
            opacity = decrease_expo(opacity, 0.992)
            si = get_circle_instructions(
                int(neigh["Cell_Centroid_X"]),
                int(neigh["Cell_Centroid_Y"]),
                radius,
                get_random_color(color_seed, color_decay_rate),  ## TO MAKE BASED ON CLASS..
                opacity,
                {"class": "cell", "allDaStuff": neigh},
            )
            
            
            shapesToAdd.append(si)
            
        print(len(shapesToAdd))
    except Exception as e:
        return html.Div(f'Error fetching data: {e}')
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


def get_circle_instructions(x, y, r, color, opacity, userdata={}):
    props = osdConfig.get("defaultStyle") | {
        "center": [x, y],
        "radius": r,
        "fillColor": color,
        "strokeColor": color,
        "fillOpacity": opacity,
    }
    userdata["objectId"] = getId()
    command = {"paperType": "Path.Circle", "args": [props], "userdata": userdata}

    return command

