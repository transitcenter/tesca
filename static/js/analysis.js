var zoom = 10.9
var lat = "43.715877"
var lon = "-79.3243027"

console.log(lat, lon)

var map = L.map('map',
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

var cartoLabels = L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_only_labels/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>',
  pane: 'labels'
}).addTo(map);

var scaleBar = L.control.scale().addTo(map)

boundary = new L.GeoJSON.AJAX('/static/data/toronto.geojson', {
    style: {
      color: '#6C154B',
      weight: 2,
      opacity: 0.6,
      fillOpacity: 0
    }
  }).addTo(map)

console.log(config)

if(config["points"] != null){
    console.log(config["points"])
    var markerOptions = {
      radius: 10,
      fillColor: "#000000",
      color: "#000",
      opacity: 1,
      weight: 2
    };
    var points = new L.GeoJSON.AJAX("/cache/" + config["analysis_id"] + "/points.geojson", {
      pointToLayer: function (feature, latlng) {
        var m = L.circleMarker(latlng, markerOptions);
        m.bindPopup("<b>" + feature['properties']['project_id'] + "</b>: " + feature['properties']['details']);
        return m;
      }
    }).addTo(map)
}

if(config["lines"] != null){
  var lines = new L.GeoJSON.AJAX("/cache/" + config["analysis_id"] + "/lines.geojson", {
    style: {
      color: '#000000',
      opacity: 1,
      weight: 8
    },
    onEachFeature: function(feature, layer){
      console.log(feature);
      layer.bindPopup("<b>" + feature['properties']['project_id'] + "</b>: " + feature['properties']['details']);
    }
  }).addTo(map)
}

if(config["areas"] != null){
  var lines = new L.GeoJSON.AJAX("/cache/" + config["analysis_id"] + "/areas.geojson", {
    style: {
      color: '#000000',
      opacity: 1,
      weight: 2
    },
    onEachFeature: function(feature, layer){
      console.log(feature);
      layer.bindPopup("<b>" + feature['properties']['project_id'] + "</b>: " + feature['properties']['details']);
    }
  }).addTo(map)
}

