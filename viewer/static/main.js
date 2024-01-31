import constants from "./js/constants.js";
import renderFeatures from "./js/renderFeatures.js";
import similarityCompute from "./js/similarityCompute.js";
import {
  similarityCutOff,
  opacitySlider,
  imageSelector,
  featureSetSelector,
} from "./js/views/mainPanelDataControls.js";

import { featureHistogram } from "./js/views/featureHistogram.js";

// import ajaxActions from "./services/ajaxActions";

/* Basic initialization for all webix components */
export var osdViewer = OpenSeadragon({
  id: "osdViewer1",
  prefixUrl: "/node_modules/openseadragon/build/openseadragon/images/",
  tileSources: [{ tileSource: constants.TEST_TILE_SRC }],
});

function viewerOpened() {
  //This needs to clear any prexisting annotations
  d3.selectAll(".gutmansSquare").remove();
}

osdViewer.addHandler("open", viewerOpened);
export var overlay = osdViewer.svgOverlay();

var dsaSpxHeader = {
  view: "label",
  type: "header",
  css: "osdGisHeader",
  label: "DSA OSD PostGis Viewer",
  align: "center",
  height: 20,
};

var mouseInfoBox = {
  view: "label",
  id: "mouseTrackerBox",
  label: "Active ROI",
  value: "1",
  inputWidth: 150,
};

var main_layout = {
  rows: [
    dsaSpxHeader,
    {
      cols: [imageSelector, mouseInfoBox, opacitySlider, similarityCutOff],
    },
    {
      cols: [
        featureSetSelector,
        {
          content: "osdContainer",
          gravity: 2,
        },
        featureHistogram,
      ],
    },
  ],
};

// webix.debug({ events: true });
webix.ui(main_layout);

const imageListCollection = new webix.DataCollection({
  url: constants.IMAGE_LIST_URL,
});

$.getJSON(constants.IMAGE_LIST_URL).then((imageListData) => {
  var imgList = $$("imageSelectCombo").getPopup().getList();
  imgList.parse(imageListData);
  $$("imageSelectCombo").setValue(imageListData[0].id);
});

webix.ready(function () {
  //Kick start the process, this will load the list of available images
  webix
    .$$("imageSelectCombo")
    .getPopup()
    .getList()
    .data.attachEvent("onParse", function () {
      const imgList = $$("imageSelectCombo").getPopup().getList();
      console.log(imgList.getFirstId());
      // this.setValue(this.getFirstId());
    });
  /* This will pull the list of images that have been loaded into the local database */
});
