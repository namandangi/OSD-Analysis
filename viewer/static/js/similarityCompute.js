/* This contains functions related to computed similarity */

function computeEuclideanDistance(a, b) {
  var sum = 0;
  var n;
  for (n = 0; n < a.length; n++) {
    sum += Math.pow(a[n] - b[n], 2);
  }
  return sum;
}

//https://github.com/antimatter15/rgb-lab/blob/master/color.js

// the following functions are based off of the pseudocode
// found on www.easyrgb.com

function lab2rgb(lab) {
  var y = (lab[0] + 16) / 116,
    x = lab[1] / 500 + y,
    z = y - lab[2] / 200,
    r,
    g,
    b;

  x = 0.95047 * (x * x * x > 0.008856 ? x * x * x : (x - 16 / 116) / 7.787);
  y = 1.0 * (y * y * y > 0.008856 ? y * y * y : (y - 16 / 116) / 7.787);
  z = 1.08883 * (z * z * z > 0.008856 ? z * z * z : (z - 16 / 116) / 7.787);

  r = x * 3.2406 + y * -1.5372 + z * -0.4986;
  g = x * -0.9689 + y * 1.8758 + z * 0.0415;
  b = x * 0.0557 + y * -0.204 + z * 1.057;

  r = r > 0.0031308 ? 1.055 * Math.pow(r, 1 / 2.4) - 0.055 : 12.92 * r;
  g = g > 0.0031308 ? 1.055 * Math.pow(g, 1 / 2.4) - 0.055 : 12.92 * g;
  b = b > 0.0031308 ? 1.055 * Math.pow(b, 1 / 2.4) - 0.055 : 12.92 * b;

  return [
    Math.max(0, Math.min(1, r)) * 255,
    Math.max(0, Math.min(1, g)) * 255,
    Math.max(0, Math.min(1, b)) * 255,
  ];
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

// calculate the perceptual distance between colors in CIELAB
// https://github.com/THEjoezack/ColorMine/blob/master/ColorMine/ColorSpaces/Comparisons/Cie94Comparison.cs

function deltaE(labA, labB) {
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

function colorToRGBArray(colorInfo) {
  //This will be a generic function that will interpret the raw data it is sent
  // and if its hex it will convert it to RGB values and if it's a d3color also output
  // an array of R G B

  if (colorInfo[0] == "#") {
    //convert hex to rgb...
    rgbVals = hexToRgb(colorInfo);
  } else {
    console.log(colorInfo);
    rgbVals = colorInfo;
  }
  // console.log(selectedRGBData,rgbVals);
  rgb = new Array(3);
  rgb[0] = rgbVals["r"];
  rgb[1] = rgbVals["g"];
  rgb[2] = rgbVals["b"];
  return rgb;
}

//Additional Color Helpers I grabbed from stack

// function handleMouseOver(d, i) { // Add interactivity
//   // Use D3 to select element, change color and size
//   d3.selectAll("#" + this.id).style("fill", "blue")
//   d3.selectAll("#" + this.id).style("opacity", "0.5")

//   origTileColor = d3.select(this).attr('origColor');
//   // fillColor =   d3.select(this).style('fill');

//   // console.log(origTileColor);
//   // console.log(d3.selectAll("#" + this.id));

//   //    tileAvgColor = JSON.parse(d3.selectAll("#" + this.id).style('fill'))
//   tileAvgColor = d3.selectAll("#" + this.id).style('fill');
//   tileDataInfo = JSON.parse(d3.selectAll("#" + this.id).attr('tileDataInfo'))

//   colorLookupData = JSON.parse(d3.selectAll("#" + this.id).attr('colorLookupData'))
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
//   chartData = [{ "color": "red", "mean": rgb[0] }, { "color": "blue", "mean": rgb[1] }, { "color": "green", "mean": rgb[2] }]

//   //Convert the colorLookupData to the format the
//   $$("rgbChart").parse(chartData);
// }

function lookupSimilars(selectedRGBData, tileDataInfo) {
  /*compute euclidean distance and show similar tiles...*/
  /* Walk through the color tiles and paint all of the tiles that share the same color... */
  //Currently selected tile kicks this off...
  referenceRGB = colorToRGBArray(selectedRGBData);
  referenceLAB = rgb2lab(referenceRGB);

  d3.selectAll(".gutmansSquare").each(function (d) {
    curTileColor = d3.select(this).attr("origColor");
    useLab = true;
    if (useLab) {
      curLabColor = rgb2lab(colorToRGBArray(curTileColor));
      colorDistance = deltaE(curLabColor, referenceLAB);
    } else {
      colorDistance = computeEuclideanDistance(
        colorToRGBArray(curTileColor),
        referenceRGB
      );
    }

    if (colorDistance < $$("similarityCutOff").getValue()) {
      d3.select(this).style("fill", "orange");
      d3.select(this).style("opacity", 1);
    } else {
      d3.select(this).style("opacity", 0);
    }
  });
}

export default { computeEuclideanDistance: computeEuclideanDistance };
