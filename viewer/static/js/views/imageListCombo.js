/*This is the image list combo */
import constants from "../constants";

var imageSelector = {
  view: "combo",
  label: "Image Selector",
  id: "imageSelectCombo",
  dataFeed: constants.IMAGE_LIST_URL,
  options: { body: { template: "#imageName#" } },
  width: 400,
  on: {
    onChange: function (newv, oldv) {
      /* get the imageId for the selected image, and then need to populate the list of available features */
      var selectedImage = $$(this).getPopup().getList().getItem(newv);

      var ts = buildImageTileSource(selectedImage);
      console.log(ts);
      var ftrLookupUrl =
        constants.FEATURE_LIST_URL + "?imageId=" + selectedImage.imageId;
      osdViewer.open(ts);

      $.getJSON(ftrLookupUrl).then(function (featureSetData) {
        $$("featureSetTable").clearAll();
        $$("featureSetTable").parse(featureSetData);
      });
    },
  },
};
