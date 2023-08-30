

/**
 * Configuration Page
 * This contains code to render the Leaflet map showing the block group centroids.
 */

// Date picker setup for the scenarios
var pickerConfig = {
  initialDate: '',
  format: 'yyyy-mm-dd hh:ii',
  disableDblClickSelection: true,
  pickTime: true
}

$(function () {
  $('#scenario0_start').fdatepicker(pickerConfig);
});

$(function () {
  $('#scenario1_start').fdatepicker(pickerConfig);
});


// Set the starting location (is updated right away), currently Toronto
var zoom = 12
var lat = "43.715877"
var lon = "-79.3243027"

// Initialize the map
var map = L.map('configure-map',
  {
    preferCanvas: true, // Great speedup
    markerZoomAnimation: false
  }
).setView([lat, lon], zoom);

// Load the basemap layer - currently using CartoDB Greyscale.
var cartoLight = L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
}).addTo(map);

// Create the layer group of place labels, which sits highest
map.createPane('labels');
map.getPane('labels').style.zIndex = 650;
map.getPane('labels').style.pointerEvents = 'none';

// Grab the labels map and add it to the map.
var cartoLabels = L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_only_labels/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>',
  pane: 'labels'
}).addTo(map);

// Add a scale bar for scale
var scaleBar = L.control.scale().addTo(map)

// Styling of the circles representing centroids
var markerOptions = {
  radius: 6,
  fillColor: "#000000",
  color: "#000",
  opacity: 1,
  weight: 0
};

// Fetch and render centroids
var points = new L.GeoJSON.AJAX("/cache/" + config["analysis_id"] + "/analysis_centroids.geojson", {
  pointToLayer: function (feature, latlng) {
    var m = L.circleMarker(latlng, markerOptions);
    m.bindPopup("<b>" + feature['properties']['id'] + "</b>");
    return m;
  }
}
).addTo(map)

// Recenter the map on the appropriate layer.
points.on('data:loaded', function () {
  map.fitBounds(points.getBounds());
}.bind(this));