import girder_client, os
from os.path import join, dirname
from dotenv import load_dotenv
from joblib import Memory
import pandas as pd


## Create a cache object to cache the results of function calls
memory = Memory(".npCacheDir", verbose=0)

# Assuming that this file, settings.py, is in the same directory as the .env file.
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path, override=True)

## Load the DSA Keys from the environment
DSAKEY = os.getenv("DSAKEY")
DSA_BASE_URL = os.getenv("DSA_BASE_URL", "https://candygram.neurology.emory.edu/api/v1")
## Use candygram as default if .env not set

SAMPLE_CELLDATA_FILE = "MAP01938_0000_0E_01_region_001_quantification.csv"
SAMPLE_IMGID = "649b7993fbfabbf55f16fba4"

## CONNECT TO GIRDER
gc = girder_client.GirderClient(apiUrl=DSA_BASE_URL)
## AUTHENTICATE IF THE DSAKEY IS SET


# For now these are global variables; can be redis if multiple windows can interact with the same server
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
classes = ["a", "b", "c", "d", "e", "f"]

globalId = 0


def getId():
    global globalId
    globalId = globalId + 1
    return globalId


osdConfig = {
    "eventBindings": [
        {"event": "keyDown", "key": "c", "action": "cycleProp", "property": "class"},
        {
            "event": "keyDown",
            "key": "x",
            "action": "cyclePropReverse",
            "property": "class",
        },
        {"event": "keyDown", "key": "d", "action": "deleteItem"},
        {"event": "keyDown", "key": "n", "action": "newItem", "tool": "rectangle"},
        {"event": "mouseEnter", "action": "dashCallback", "callback": "mouseEnter"},
        {"event": "mouseLeave", "action": "dashCallback", "callback": "mouseLeave"},
    ],
    "callbacks": [
        {"eventName": "item-created", "callback": "createItem"},
        {"eventName": "property-changed", "callback": "propertyChanged"},
        {"eventName": "item-deleted", "callback": "itemDeleted"},
    ],
    "properties": {"class": classes},
    "defaultStyle": {
        "fillColor": colors[0],
        "strokeColor": colors[0],
        "rescale": {
            "strokeWidth": 1,
        },
        "fillOpacity": 0.2,
    },
    "styles": {
        "class": {
            k: {"fillColor": c, "strokeColor": c} for (k, c) in zip(classes, colors)
        }
    },
}
