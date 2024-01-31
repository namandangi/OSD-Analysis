/* These are controls related to pulling or interacting with data and overlays from the backend , basically related to filtering
or selecting tiles or operations to perform on the tiles */
import constants from "../constants.js";
import { osdViewer, overlay } from "../../main.js";
import renderFeatures from "../renderFeatures.js";

export const similarityCutOff = {
  view: "slider",
  id: "similarityCutOff",
  label: "SimCutOff",
  value: 5,
  min: 0,
  max: 25,
  step: 0.5,
  inputWidth: 200,
  labelWidth: 100,
  title: "#value#",
  on: {
    onChange: function (newv, oldv) {
      webix.message("Something slid" + newv);
    },
  },
};

export let currentFeatureSet = {};

/* TO DO: See how to better scope the overlay object, I think maybe I can grab it from the viewer */
function buildImageTileSource(imageInfo) {
  console.log(imageInfo);
  var tileSourceUrl =
    imageInfo.apiURL + "/item/" + imageInfo.imageId + "/tiles/dzi.dzi";

  return { tileSource: tileSourceUrl, width: imageInfo.sizeX };
}

export const imageSelector = {
  view: "richselect",
  label: "Image Selector",
  id: "imageSelectCombo",
  dataFeed: "http://localhost:82/getImageList/",
  options: { body: { template: "#imageName#" } },
  width: 400,
  on: {
    onChange: function (newv, oldv) {
      /* get the imageId for the selected image, and then need to populate the list of available features */
      var selectedImage = $$(this).getPopup().getList().getItem(newv);
      var ts = buildImageTileSource(selectedImage);
      var ftrLookupUrl =
        constants.FEATURE_LIST_URL + "?imageId=" + selectedImage.imageId;
      osdViewer.open(ts);

      $.getJSON(ftrLookupUrl).then(function (featureSetData) {
        $$("featureSetTable").clearAll();
        $$("featureSetTable")
          .parse(featureSetData)
          .then(function () {
            $$("featureSetTable").select($$("featureSetTable").getFirstId());
          });
      });
    },
  },
};

export const opacitySlider = {
  view: "slider",
  label: "gridOpacity",
  value: constants.START_GRID_OPACITY,
  inputWidth: 200,
  labelWidth: 100,
  min: 0,
  step: 0.05,
  max: 1,
  id: "gridOpacity",
  on: {
    onChange: function (newv, oldv) {
      d3.selectAll(".gutmansSquare").style("opacity", newv);
    },
  },
};

var featureColumns = [
  { id: "featureType" },
  { id: "magnification" },
  { id: "imageFeatureSet_id" },
  { id: "ifs_id" },
  { id: "tilesProcessed" },
];

let currentFeatureData = new webix.DataCollection({ id: "currentFeatureData" }); //While I am putting the feature data into the overlay
//I am also keeping a copy in case I need to reprocess things

var featureDataStore = { view: "datastore", id: "featureDataStore" };

export const featureSetSelector = {
  rows: [
    { type: "header", template: "gridSize" },
    {
      view: "datatable",
      columns: featureColumns,
      select: "row",
      id: "featureSetTable",
      on: {
        onAfterSelect: function (id) {
          // webix.message("table was clicked");
          var item = $$(this).getItem(id);
          console.log(item);

          if (item.featureType == "nftFeature") {
            webix.message("Seleceted NP Feature");
            $.getJSON(
              constants.NP_FEATURES_URL +
                "?imageId=" +
                item.imageId +
                "&featureType=" +
                item.featureType +
                "&imageFeatureSet_id=" +
                item.imageFeatureSet_id
            ).then((NPfeatureData) => {
              renderFeatures.renderNFTData(NPfeatureData, overlay);
            });
            // $.getJSON(
            //   constants.TILE_FEATURES_URL +
            //     "?imageId=" +
            //     item.imageId +
            //     "&ftxtract_id=" +
            //     item.ftxtract_id
            // ).then((featureData) => {
            //   // console.table(featureData);
            //   currentFeatureSet = featureData;

            //   currentFeatureData.parse(featureData); //Update local copy so I can run stats
            //   renderFeatures.renderGrid(featureData, overlay);

            //   console.log(currentFeatureSet);
          } else {
            $.getJSON(
              constants.TILE_FEATURES_URL +
                "?imageId=" +
                item.imageId +
                "&ftxtract_id=" +
                item.ftxtract_id +
                "&featureType=" +
                item.featureType
            ).then((featureData) => {
              // console.table(featureData);
              currentFeatureSet = featureData;

              currentFeatureData.parse(featureData); //Update local copy so I can run stats
              renderFeatures.renderGrid(featureData, overlay);

              console.log(currentFeatureSet);
            });
          }
        },
      },
    },
  ],
};
