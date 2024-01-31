/*This will deal with overlays to render features we pull from the database */
import constants from "./constants.js";
import { currentFeatureSet } from "./views/mainPanelDataControls.js";

function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function rgb2lab(rgb) {
  var r = rgb[0] / 255,
    g = rgb[1] / 255,
    b = rgb[2] / 255,
    x,
    y,
    z;

  r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
  g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
  b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;

  x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047;
  y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.0;
  z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883;

  x = x > 0.008856 ? Math.pow(x, 1 / 3) : 7.787 * x + 16 / 116;
  y = y > 0.008856 ? Math.pow(y, 1 / 3) : 7.787 * y + 16 / 116;
  z = z > 0.008856 ? Math.pow(z, 1 / 3) : 7.787 * z + 16 / 116;

  return [116 * y - 16, 500 * (x - y), 200 * (y - z)];
}

function genRandColorData() {
  //This is for testing, but it will generate random color data I can use for the graphs
  //Adding in some synthetic RGB data
  var limit = 255;
  var rgbColorData = [
    { color: "red", mean: Math.floor(Math.random() * (limit + 1)) },
    { color: "green", mean: Math.floor(Math.random() * (limit + 1)) },
    { color: "blue", mean: Math.floor(Math.random() * (limit + 1)) },
  ];

  return rgbColorData;
}

function imgTile_rgb2lab(imgTile) {
  /*This will convert an image tile returned from the database into LAB Color Space and return the lab color and tileID*/
  const rgbAvg = imgTile.average;

  var r = rgbAvg[0] / 255,
    g = rgbAvg[1] / 255,
    b = rgbAvg[2] / 255,
    x,
    y,
    z;
  console.log(r, g, b);
  r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
  g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
  b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;

  x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047;
  y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.0;
  z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883;

  x = x > 0.008856 ? Math.pow(x, 1 / 3) : 7.787 * x + 16 / 116;
  y = y > 0.008856 ? Math.pow(y, 1 / 3) : 7.787 * y + 16 / 116;
  z = z > 0.008856 ? Math.pow(z, 1 / 3) : 7.787 * z + 16 / 116;

  console.log(rgbAvg);
  console.log([116 * y - 16, 500 * (x - y), 200 * (y - z)]);
  return {
    averageRGB: rgbAvg,
    localTileId: imgTile.localTileId,
    averageLAB: [116 * y - 16, 500 * (x - y), 200 * (y - z)],
  };
}

// calculate the perceptual distance between colors in CIELAB
// https://github.com/THEjoezack/ColorMine/blob/master/ColorMine/ColorSpaces/Comparisons/Cie94Comparison.cs

function deltaE(labA, labB) {
  // const labB = imgTile.averageLAB;
  var deltaL = labA[0] - labB[0];
  var deltaA = labA[1] - labB[1];
  var deltaB = labA[2] - labB[2];
  var c1 = Math.sqrt(labA[1] * labA[1] + labA[2] * labA[2]);
  var c2 = Math.sqrt(labB[1] * labB[1] + labB[2] * labB[2]);
  var deltaC = c1 - c2;
  var deltaH = deltaA * deltaA + deltaB * deltaB - deltaC * deltaC;
  deltaH = deltaH < 0 ? 0 : Math.sqrt(deltaH);
  var sc = 1.0 + 0.045 * c1;
  var sh = 1.0 + 0.015 * c1;
  var deltaLKlsl = deltaL / 1.0;
  var deltaCkcsc = deltaC / sc;
  var deltaHkhsh = deltaH / sh;
  var i =
    deltaLKlsl * deltaLKlsl + deltaCkcsc * deltaCkcsc + deltaHkhsh * deltaHkhsh;
  return i < 0 ? 0 : Math.sqrt(i);
}

function findSimilarTilesLocalData(refFeatureId) {
  /*This version just uses data that is already available in the client
For version one, I am using the .average property and .localTileId as the relevant properties for computing
the euclidean distance */
  d3.selectAll(".gutmansSquare").style("opacity", 0);

  const distanceThresh = webix.$$("similarityCutOff").getValue();

  /* Damn it.. the average color is showing up as a string not an array */
  var RGB_refColor = d3
    .select(`#grid-${refFeatureId}`)
    .attr("averageColor")
    .split(",");
  const LAB_refColor = rgb2lab(RGB_refColor);

  // const labDataArray = currentFeatureSet.map((imgTile) => rgb2lab(imgTile));
  // // const distanceData = labDataArray.map((t) => deltaE(LAB_refColor, t));
  var labColorArray = [];
  var colorDeltaDist = [];

  currentFeatureSet.forEach((cfs) => {
    const labColor = rgb2lab(cfs.average);

    var colorDelta = deltaE(labColor, LAB_refColor);
    colorDeltaDist.push(colorDelta);

    if (colorDelta < distanceThresh) {
      d3.select("#grid-" + cfs.localTileId)
        .style("fill", "blue")
        .style("opacity", 0.5);
    }
  });

  var chartContainer = document.getElementById("plotlyHistDiv");

  //Update the graph data
  var distHistObject = webix.$$("featureDistanceHistogram").$plotlyGraphObject;
  distHistObject.data[0].x = colorDeltaDist;
  Plotly.update(chartContainer, distHistObject.data, distHistObject.layout);
}

function findSimilarTiles(avgColor, refFeatureId, ftxract_id) {
  /* Query the backend server and pull tiles within some distance threshold */
  const distanceThresh = webix.$$("similarityCutOff").getValue();
  const selectedFeatureSet = webix.$$("featureSetTable").getSelectedItem();

  findSimilarTilesLocalData(refFeatureId);

  // //Why in theh ell does this work this way??
  // var ftxract_id_two = webix.$$("featureSetTable").getSelectedItem()[
  //   "ftxract_id"
  // ];
  // console.log(ftxract_id_two);
  //console.log(avgColor, distanceThresh, ftxract_id, refFeatureId);
  // console.log(selectedFeatureSet);
  // console.log(refFeatureId);

  //I tried setting fill to none and it just broke everyhint.. no  idea why

  // $.getJSON(constants.TILE_FEATURES_URL + "?ftxtract_id=" + ftxract_id);
  // $.getJSON(
  //   constants.SIMILAR_FEATURES_URL +
  //     "?ftxtract_id=" +
  //     ftxract_id +
  //     "&distanceThresh=" +
  //     distanceThresh +
  //     "&refFeatureId=" +
  //     refFeatureId
  // ).then((similarFeatureData) => {
  //   console.log(similarFeatureData);
  //   similarFeatureData.forEach((ftr) => {
  //     const localTileId = ftr[0];
  //     const curFeatureDist = ftr[1];
  //     if (curFeatureDist < distanceThresh) {
  //       d3.select(`.gutmansSquare[localTileId="${localTileId}"]`)
  //         .style("fill", "orange")
  //         .style("opacity", 0.2);
  //       // } else {
  //       //   d3.select(`.gutmansSquare[localTileId="${localTileId}"]`).style(
  //       //     "fill",
  //       //     "blue"
  //       //   );
  //     }
  //   });
  // });
  //   d3.selectAll(".gutmansSquare").style("fill", "none");

  //   // console.table(similarFeatureData);

  //   });
  //  };

  // ).then((featureData) => {
  //   // console.table(featureData);
  //   currentFeatureData.parse(featureData); //Update local copy so I can run stats
  //   renderFeatures.renderGrid(featureData, overlay);
  // });

  //fxtract_id
}

function handleMouseOver(d, i) {
  // Add interactivity
  // Use D3 to select element, change color and size
  //console.log(this )
  var avgColor = this.getAttribute("averageColor");
  var localTileId = this.getAttribute("localTileId");

  webix
    .$$("mouseTrackerBox")
    .setHTML(
      "<div style='background-color:rgb(" +
        avgColor +
        ")'>" +
        this.id +
        "</div>"
    );

  /* this is the logic that grabs the tile data and passes it to compute similarity */
  var ftxtract_id = webix.$$("featureSetTable").getSelectedItem().ftxtract_id;

  //console.log(avgColor, localTileId, ftxtract_id);
  findSimilarTiles(avgColor, localTileId, ftxtract_id);
}

function renderGrid(gridData, overlayHandler) {
  /* This will take the current viewer and generate a square grid on top */
  d3.selectAll(".gutmansSquare").remove();
  //console.log(gridData);
  // print(gridData.length);
  var tileIndex = 0;
  // randInt = Math.floor(Math.random() * 20);
  // fillColor = d3.schemeCategory20[randInt % 20];
  gridData.forEach(function (r, idx) {
    var randColorLookup = genRandColorData();
    randColorLookup = JSON.stringify(randColorLookup);
    var a = r.average;
    var fillColor = rgbToHex(parseInt(a[0]), parseInt(a[1]), parseInt(a[2]));
    d3.select(overlayHandler.node())
      .append("rect")
      .attr("x", r.topX)
      .attr("y", r.topY)
      .attr("width", r.width)
      .attr("height", r.width)
      .style("fill", fillColor)
      .attr("opacity", 0.7)
      .attr("class", "gutmansSquare")
      .attr("stroke", "blue")
      .attr("stroke-width", 1)
      .attr("id", "grid-" + r.localTileId)
      .attr("origColor", fillColor) //need this if I want to switch color back
      .attr("colorImgLookup", randColorLookup)
      .attr("averageColor", a)
      .attr("tileDataInfo", r.tileDataInfo)
      .attr("localTileId", r.localTileId)
      .on("mouseover", handleMouseOver);
    // .on("mouseout", handleMouseOut);
  });
}

function renderNFTData(NTFdata, overlayHandler) {
  console.log(NTFdata);
  d3.selectAll(".gutmansSquare").remove();
  //console.log(gridData);
  // print(gridData.length);
  var tileIndex = 0;
  // randInt = Math.floor(Math.random() * 20);
  // fillColor = d3.schemeCategory20[randInt % 20];
  NTFdata.forEach(function (r, idx) {
    if (r.classLabel == "iNFT") {
      var fillColor = "rgb(0,0,255";
    } else {
      var fillColor = "rgb(255,0,0)";
    }

    // var fillColor = rgbToHex(parseInt(a[0]), parseInt(a[1]), parseInt(a[2]));
    d3.select(overlayHandler.node())
      .append("rect")
      .attr("x", r.topX)
      .attr("y", r.topY)
      .attr("width", r.roiWidth)
      .attr("height", r.roiHeight)
      .style("fill", fillColor)
      .attr("opacity", 0.7)
      .attr("class", "gutmansSquare")
      .attr("stroke", "blue")
      .attr("stroke-width", 1)
      .attr("id", "grid-" + r.id)
      .attr("origColor", fillColor) //need this if I want to switch color back
      // .attr("colorImgLookup", randColorLookup)
      // .attr("averageColor", a)
      // .attr("tileDataInfo", r.tileDataInfo)
      // .attr("localTileId", r.localTileId)
      .on("mouseover", handleMouseOver);
    // .on("mouseout", handleMouseOut);
  });
}

export default {
  rgbToHex: rgbToHex,
  renderGrid: renderGrid,
  renderNFTData: renderNFTData,
};

//   d3.selectAll("#" + this.id).style("fill", "blue");
//   d3.selectAll("#" + this.id).style("opacity", "0.5");

//   origTileColor = d3.select(this).attr("origColor");
//   // fillColor =   d3.select(this).style('fill');

//   // console.log(origTileColor);
//   // console.log(d3.selectAll("#" + this.id));

//   //    tileAvgColor = JSON.parse(d3.selectAll("#" + this.id).style('fill'))
//   tileAvgColor = d3.selectAll("#" + this.id).style("fill");
//   tileDataInfo = JSON.parse(d3.selectAll("#" + this.id).attr("tileDataInfo"));

//   colorLookupData = JSON.parse(
//     d3.selectAll("#" + this.id).attr("colorLookupData")
//   );
//   //this used to be colorlookupData
//   // console.log(colorLookupData,tileDataInfo);

//   //This should only run if I am in that mode..
//   if ($$("findSimilarTiles").getValue()) {
//     lookupSimilars(origTileColor, tileDataInfo);
//   } else if ($$("paintMode").getValue()) {
//     console.log("paint/....");
//   }

//   //THIS IS A DISASTER IN TERMS OF EFFICIENCY
//   //THIS ITERATION ALLOWS ME TO PAINT!!
//   $$("spxName").setValue(this.id);
//   $$("rgbChart").clearAll();

//   //need to reformat the HEX color and put it into the chart format
//   rgb = colorToRGBArray(origTileColor);
//   chartData = [
//     { color: "red", mean: rgb[0] },
//     { color: "blue", mean: rgb[1] },
//     { color: "green", mean: rgb[2] },
//   ];

//   //Convert the colorLookupData to the format the
//   $$("rgbChart").parse(chartData);
