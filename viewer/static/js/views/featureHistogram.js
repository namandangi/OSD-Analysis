/*This is a plotly component*/

webix.protoUI(
  {
    name: "plotlyChart",
    $init: function (config) {
      this.$view.innerHTML = `<div style='width:100%; height:100%;' id='${config.chartConfig.chartId}'></div>`;

      this.$ready.push(() => {
        this._initChart(config);
      });
    },
    $setSize: function (x, y) {
      if (webix.ui.view.prototype.$setSize.call(this, x, y))
        Plotly.Plots.resize(this.$view.firstChild);
    },
    $plotlyGraphObject: {},
    _initChart: function (config) {
      var chart = config.chartConfig;
      var layout = chart.layout;

      this._plChartPromise = new Plotly.newPlot(this.$view.firstChild, chart);

      this._plChartPromise.then((plChartNode) => {
        console.log(plChartNode.layout);
        console.log(plChartNode.data);

        this.$plotlyGraphObject = plChartNode;
      });
    },
    getHistogramNode: function () {
      return this.$view.firstChild;
    },
  },
  webix.ui.view
);

var trace = {
  x: [],
  type: "histogram",
  title: "Holder",
};
var layout = { title: "Histogram of Distance from Current Feature" };
export const featureHistogram = {
  view: "plotlyChart",
  id: "featureDistanceHistogram",
  chartConfig: { data: [trace], chartId: "plotlyHistDiv", layout: layout },
};

export default {};

// import lodash from "lodash";
// import Plotly from "plotly.js-dist-min";
// import {JetView} from "webix-jet";

// import constants from "../../constants";

// export default class PlotlyChart extends JetView {
// 	constructor(app, config = {}) {
// 		super(app, config);
// 		this._histogramContainerId = `histogram-container-${webix.uid()}`;
// 		this._cnf = config;
// 		this.width = config.width || 330;
// 		this.height = config.height || 270;
// 		this.localId = config.localId;
// 	}

// 	config() {
// 		return {
// 			...this._cnf,
// 			css: "histogram-chart",
// 			template: () => ""
// 		};
// 	}

// 	makeChart(data, yScaleType) {
// 		const template = this.$chartTemplate();
// 		template.refresh();
// 		if (lodash.isEmpty(data)) {
// 			return;
// 		}
// 		const templateNode = template.getNode();
// 		// Create element with histogramContainerId for Plotly chart
// 		templateNode.innerHTML = `<div id="${this._histogramContainerId}"/>`;
// 		this._renderChart(data, yScaleType);
// 		webix.TooltipControl.addTooltip(templateNode);
// 	}

// 	_renderChart(data, yScaleType) {
// 		const layout = {
// 			width: this.width,
// 			height: this.height,
// 			title: yScaleType === constants.LOGARITHMIC_SCALE_VALUE
// 				? "Histogram logarithmic scale"
// 				: "Histogram linear scale",
// 			yaxis: yScaleType === constants.LOGARITHMIC_SCALE_VALUE
// 				? {
// 					type: "log",
// 					autorange: true
// 				}
// 				: {
// 					type: "linear",
// 					autorange: true
// 				},
// 			margin: {
// 				l: 40,
// 				t: 30,
// 				r: 20,
// 				b: 20
// 			}
// 		};

// 		const histogramTrace = {
// 			type: "bar",
// 			x: data.map(item => Number(item.name)),
// 			y: data.map(item => Number(item.value))
// 		};

// 		const plotlyConfig = {
// 			/* TODO: consider these application settings
// 			displayModeBar: false
// 			scrollZoom: true
// 			editable: true
// 			staticPlot: true
// 			toImageButtonOptions: {
// 				format: 'svg', // one of png, svg, jpeg, webp
// 				filename: 'custom_image',
// 				height: 500,
// 				width: 700,
// 				scale: 1 // Multiply title/legend/axis/canvas sizes by this factor
// 			}
// 			modeBarButtonsToRemove: ['toImage'],
// 			displaylogo: false,
// 			responsive: true
// 			*/
// 			displaylogo: false,
// 			responsive: true
// 		};

// 		const plotlyOptions = {
// 			data: [histogramTrace],
// 			layout,
// 			config: plotlyConfig
// 		};

// 		const histogramChartDiv = this.getHistogramDiv();

// 		Plotly.newPlot(histogramChartDiv, plotlyOptions);
// 	}

// 	$chartTemplate() {
// 		return this.getRoot();
// 	}

// 	getHistogramDiv() {
// 		return document.getElementById(this._histogramContainerId);
// 	}
// }
