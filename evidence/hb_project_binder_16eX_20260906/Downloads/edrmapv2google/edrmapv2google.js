/// <reference path="http://localhost/global/jscripts/edrlibrary.js" />
/// <reference path="http://localhost/global/sharedresources/edrmapping/scripts/EDRMapV2.js" />
/*
Name:	EDRMapV2Google.js
Desc:	This js library provides all the functionality needed for a google Map.
Note:	This js library requires that EDRLibrary (EDR namespace definition) be included in the host page before this reference.
*/
//Namespace declarations
EDR.EDRMapV2Google = {};
EDR.EDRMapV2Google.CustomMapOptions = {};
EDR.EDRMapV2Google.CustomPolygonMarker = {};

var infoWindow = null;
var map = null;
var marker = null;
var base = null;

var mapObject = null;
var tpMarker = null;
var markerOptions = null;
var markerPosition = null;
var markerSettings = null;
var edrLogoDiv = null;
var edrLogo = null;

var geocoder = new google.maps.Geocoder();
var tooltip = null;

/*
Custom properties that set base and google maps custom properties
*/

EDR.EDRMapV2Google = function (appName, mapHostDivID, tpInfo, mapOptions)
{

	this.MapProperties = new EDR.EDRMapV2(appName, mapHostDivID, tpInfo, mapOptions);
	this.MapProperties.TPMarker = new EDR.EDRMapV2GoogleV3.Marker(tpInfo);

	if (mapOptions instanceof EDR.EDRMapV2Google.CustomMapOptions)
	{
		this.MapProperties.CustomMapOptions = mapOptions;
	} 
	else if (mapOptions != null)
	{
		this.MapProperties.CustomMapOptions = new EDR.EDRMapV2Google.CustomMapOptions(mapOptions);
	} 
	else
	{
		this.MapProperties.CustomMapOptions = new EDR.EDRMapV2Google.CustomMapOptions();
	}

	base = this.MapProperties;

	//initialize map to div and set map options		
	if (tpInfo != null)
	{
		markerSettings = this.MapProperties.TPMarker;
		map = EDR.EDRMapV2Google.InitializeMap(this, null);

		var latLng = new google.maps.LatLng(markerSettings.latitude, markerSettings.longitude);

		map.setCenter(latLng);
		map.setOptions({
			zoom: this.MapProperties.MapOptions.TPZoomLevel
		});

		EDR.EDRMapV2Google.SetTPMarker(map, latLng, markerSettings);

	} 
	else
	{
		markerPosition = new google.maps.LatLng(this.MapProperties.MapOptions.InitialLatitude, this.MapProperties.MapOptions.InitialLongitude);
		map = EDR.EDRMapV2Google.InitializeMap(this, markerPosition);

		map.setCenter(markerPosition);
		map.setOptions({
			zoom: this.MapProperties.MapOptions.InitialZoomLevel
		});
	}

	//set map div height/width
	mapObject = document.getElementById(mapHostDivID);
	//mapObject.style.width = EDR.EDRMapV2Google.ValidateSize(this.MapProperties.MapOptions.MapWidth);
	//mapObject.style.height = EDR.EDRMapV2Google.ValidateSize(this.MapProperties.MapOptions.MapHeight);
};

EDR.EDRMapV2Google.prototype.constructor = EDR.EDRMapV2Google;

// Events
EDR.EDRMapV2Google.prototype.OnTPMarkerMoved = null;

//Property Definitions - general
EDR.EDRMapV2Google.prototype.CustomMapOptions = null;

// *********** Properties that are specific to Google Maps only *********** //
EDR.EDRMapV2Google.CustomMapOptions = function (mapOptions)
{
	if (this instanceof EDR.EDRMapV2Google.CustomMapOptions)
	{
		if (mapOptions != null)
		{
			EDR.CopyObjectData(mapOptions, this);
		} //convert from json to our object so all default values, etc. are correctly set
	} else
	{
		return new EDR.EDRMapV2Google.CustomMapOptions(mapOptions);
	}
};

// constructor
EDR.EDRMapV2Google.CustomMapOptions.prototype.constructor = EDR.EDRMapV2Google.CustomMapOptions;

//Property Definitions - Zoom Control Options
EDR.EDRMapV2Google.CustomMapOptions.prototype.ZoomControlPosition = 1;
EDR.EDRMapV2Google.CustomMapOptions.prototype.ZoomStyleType = 2; // this is zoom control type based (specific to API implementation)
EDR.EDRMapV2Google.CustomMapOptions.prototype.EnumZoomStyleTypes = {
	DEFAULT: 1,
	LARGE: 2,
	SMALL: 3
};

//Property Definitions - Pan Control Options
EDR.EDRMapV2Google.CustomMapOptions.prototype.ShowPanControl = true;
EDR.EDRMapV2Google.CustomMapOptions.prototype.PanControlPosition = 1;

//Property Definitions - Scale Control Options
EDR.EDRMapV2Google.CustomMapOptions.prototype.ShowScaleControl = true;
EDR.EDRMapV2Google.CustomMapOptions.prototype.ScaleControlStyleType = 1; //Currently only has default styling
EDR.EDRMapV2Google.CustomMapOptions.prototype.EnumScaleControlStyleTypes = {
	DEFAULT: 1
};
EDR.EDRMapV2Google.CustomMapOptions.prototype.ScaleControlPosition = 9;

//Property Definitions - Street View Control Options
EDR.EDRMapV2Google.CustomMapOptions.prototype.ShowStreetViewControl = true;
EDR.EDRMapV2Google.CustomMapOptions.prototype.StreetViewControlPosition = 3;

//Property Definitions - Specific to Google Maps API
EDR.EDRMapV2Google.CustomMapOptions.prototype.map = null;

// Property Definitions - Custom WMS Overlay Map Type Control Options
// JSON Format:  [{ name: '<CONTROL_TITLE>', typeID: '<LAYER_TYPE_ID>', url: '<WMS_URL>', opacity: <OPACITY>, index: '<CONTROL_INDEX>' }]
EDR.EDRMapV2Google.CustomMapOptions.prototype.OverlayMapTypeOptions = null;

EDR.EDRMapV2Google.CustomMapOptions.prototype.MapEventHandlers = null;

//Function - Return specified zoom control enum
EDR.EDRMapV2Google.ResolveEnum = function (enumMapOptions, targetEnum)
{
	for (var type in enumMapOptions)
	{
		if (enumMapOptions[type] == targetEnum)
		{
			return type.toLowerCase();
		}
	}
}

EDR.EDRMapV2Google.ResolveEnum.prototype.constructor = EDR.EDRMapV2Google.ResolveEnum;

// ************************************************************************ //
//Utility function that is used to resolve possible height/width inputs of the map. Certain browsers like
//firefox require the use of units after the height and width while IE has no preference (shockingly).
//This function could be expanded later to use other units like 'em'
EDR.EDRMapV2Google.ValidateSize = function (size)
{
	if (size.toString().indexOf("PX") != -1)
	{
		return size;
	} else if (size.toString().indexOf("Px") != -1)
	{
		return size;
	} else if (size.toString().indexOf("px") != -1)
	{
		return size;
	} else
	{
		return size + "px";
	}
};

// constructor
EDR.EDRMapV2Google.ValidateSize.prototype.constructor = EDR.EDRMapV2Google.ValidateSize;

// ************************************************************************ //
/*
Events that are specific to Google maps
*/

EDR.EDRMapV2Google.Log = function(message) {
	///<summary> Handles logging the given message </summary>
	try {
		console.log('[EDR.EDRMapV2Google] ' + message);
	}
	catch(e) {
		// do nothing for now
	}
};

//Function that is used to initialize the map
EDR.EDRMapV2Google.InitializeMap = function (options, markerPosition)
{
	var mapSettings = {
		zoom: options.MapProperties.MapOptions.InitialZoomLevel,
		mapTypeId: EDR.EDRMapV2Google.ResolveEnum(options.MapProperties.MapOptions.EnumMapTypes, options.MapProperties.MapOptions.MapType),
		zoomControl: options.MapProperties.MapOptions.ShowZoomControl,
		zoomControlOptions: {
			style: options.MapProperties.CustomMapOptions.ZoomStyleType,
			position: options.MapProperties.CustomMapOptions.ZoomControlPosition
		},
		minZoom: options.MapProperties.MapOptions.MinZoomLevel,
		maxZoom: options.MapProperties.MapOptions.MaxZoomLevel,
		mapTypeControl: options.MapProperties.MapOptions.ShowMapTypesControl,
		mapTypeControlOptions: {
			style: options.MapProperties.MapOptions.MapTypeControlStyle,
			position: options.MapProperties.MapOptions.MapTypeControlPosition
		},
		scaleControl: options.MapProperties.CustomMapOptions.ShowScaleControl,
		scaleControlOptions: {
			style: options.MapProperties.CustomMapOptions.ScaleControlStyleType,
			//Currently only has default styling
			position: options.MapProperties.CustomMapOptions.ScaleControlPosition
		},
		streetViewControl: options.MapProperties.CustomMapOptions.ShowStreetViewControl,
		streetViewControlOptions: {
			position: options.MapProperties.CustomMapOptions.StreetViewControlPosition
		},
		panControl: options.MapProperties.CustomMapOptions.ShowPanControl,
		panControlOptions: {
			position: options.MapProperties.CustomMapOptions.PanControlPosition
		},
		draggable: options.MapProperties.MapOptions.IsMapDraggable,
		scrollwheel: options.MapProperties.MapOptions.IsMouseWheelEnabled,
		keyboardShortcuts: options.MapProperties.MapOptions.IsKeyboardEnabled,
		center: markerPosition,
		tilt: options.MapProperties.MapOptions.Tilt
	}

	map = new google.maps.Map(document.getElementById(options.MapProperties.MapDivID), mapSettings);

	//Add EdrLogo
	edrLogoDiv = document.createElement('DIV');
	edrLogo = new EDR.EDRMapV2Google.edrLogoOnMap(edrLogoDiv, options.MapProperties.MapOptions.EdrLogoPath);
	edrLogoDiv.index = 1;
	map.controls[google.maps.ControlPosition.BOTTOM_LEFT].push(edrLogoDiv);

	//Set up map type control
	//var topoMap = new google.maps.ImageMapType({
	//	getTileUrl: function (coord, zoom)
	//	{
	//		var proj = map.getProjection();
	//		var zfactor = Math.pow(2, zoom);
	//		// get Long Lat coordinates
	//		var top = proj.fromPointToLatLng(
  //          new google.maps.Point(coord.x * 256 / zfactor, coord.y * 256 / zfactor));
	//		var bot = proj.fromPointToLatLng(
  //          new google.maps.Point((coord.x + 1) * 256 / zfactor, (coord.y + 1) * 256 / zfactor));

	//		var deltaX = 0;
	//		var deltaY = 0;

	//		//create the Bounding box string
	//		var bbox = (top.lng() + deltaX) + "," + (bot.lat() + deltaY) + "," + (bot.lng() + deltaX) + "," + (top.lat() + deltaY);

	//		//base WMS URL
	//		return options.MapProperties.MapOptions.WMSURL; // return URL for the tile    
	//	},

	//	tileSize: new google.maps.Size(256, 256),
	//	isPng: true,
	//	maxZoom: 16,
	//	name: "Topo Map",
	//	alt: "Show USGS DRG Topo Map"
	//});

	var styledMapOptions = {
		map: map,
		name: "Simple Map",
		alt: "Show simplified street map"
	}

	//see EDRMapStyles.js for EDRMapJSON definition		
	var simpleGoogleMap = new google.maps.StyledMapType(EDRMapJSON, styledMapOptions);

	map.mapTypes.set('Simple Map', simpleGoogleMap);
	////set the default map type to Simple Map
	//map.setMapTypeId('Simple Map');
	//set the default map type to Map
	map.setMapTypeId('roadmap');

	//map.mapTypes.set('Topo Map', topoMap);
	
	// set the default map types
	var mapTypes = [google.maps.MapTypeId.ROADMAP, 'Simple Map', google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.HYBRID];
		
	// update the map options
	map.setOptions({
		mapTypeControlOptions: {
			mapTypeIds: mapTypes
		}
	});
	
	// add overlay map types, if applicable
	var overlayOptions = options.MapProperties.CustomMapOptions.OverlayMapTypeOptions;
	var overlayMaps = new Array();
	if ((overlayOptions != null) && (overlayOptions.length > 0)){
		var wmsTypeID;
		var wmsURL;
		var wmsName;
		var wmsOpacity;
		var wmsIndex;
		var curOption;
		
		for (var i = 0; i < overlayOptions.length; i++) {
			curOption = overlayOptions[i];
			
			// validate the values
			wmsTypeID = EDRV2.trim(curOption.typeID);
			if (wmsTypeID === '') { continue; }
			
			wmsURL = EDRV2.trim(curOption.url);
			if (wmsURL === '') { continue; }
			
			wmsName = EDRV2.trim(curOption.name);
			if (wmsName === '') { 
				wmsName = wmsTypeID;
				curOption.name = wmsName;
			}
			
			// opacity is an optional value.  by default, set it to 100%
			if ((typeof(curOption.opacity) == 'undefined') || (curOption.opacity == null)) { curOption.opacity = 1; }
			wmsOpacity = curOption.opacity;
			
			// index is an optional value.  by default, pre-pend the option
			if ((typeof(curOption.index) == 'undefined') || (curOption.index == null)) { curOption.index = 0; }
			wmsIndex = curOption.index;
			
			// add the overlay control option
			EDR.EDRMapV2Google.addOverlayControlOption(map, curOption);
		}
	};	
	
	// bind the map event handlers
	var mapEvents = options.MapProperties.CustomMapOptions.MapEventHandlers;
	if (mapEvents != null) {
		for (var i = 0; i < mapEvents.length; i++) {
			var curEvt = mapEvents[i];
			var action = EDRV2.trim(curEvt.action);
			if (action == '') { continue; }
			
			if ((typeof(curEvt.callback) === 'undefined') | (curEvt.callback == null)) { continue; }
			
			// add the listener to the map
			EDR.EDRMapV2Google.addListener(map, action, curEvt.callback, map);
		}
	}
	
	return map;
};

EDR.EDRMapV2Google.addListener = function(target, name, callback, callbackData) {
	// Adds the listener to google map events
	try {
		// validate
		if ((typeof(target) == 'undefined') || (target == null)) { throw new Error('Event target is required'); }
		
		name = EDRV2.trim(name);
		if (name === '') { throw new Error('Event name is required'); }
		
		google.maps.event.addListener(target, name, function(evt) {
			EDR.EDRMapV2Google.Log('Event Triggered: ' + name);
			
			// check if there is a callback
			if (typeof(callback) == 'function') {
				if (typeof(callbackData) == 'undefined') { callbackData = null; }
				callback(evt, callbackData);
			}
		});
	}
	catch(e) {
		EDR.EDRMapV2Google.Log('setupListener(): ' + e.message);
	}
};

// constructor
EDR.EDRMapV2Google.InitializeMap.prototype.constructor = EDR.EDRMapV2Google.InitializeMap;


//******************************************************************************
//Map overlay functionality

EDR.EDRMapV2Google.EnumMapOverlayEvents = {
	MAPOVERLAYENABLED: 'MAPOVERLAYENABLED',
	MAPOVERLAYDISABLED: 'MAPOVERLAYDISABLED',
	OVERLAYOPTIONADDED: 'OVERLAYOPTIONADDED'
};

EDR.EDRMapV2Google.setOverlayMapType = function (name, url, opacity)
{
    ////First see if we already have the objects created
    var existingWMSMapType = null;
   
    //Create our options
    var wmsOptions =
    {
        alt: "MapServer Layer",
        getTileUrl: this.mapWMSGetTileUrl,
        isPng: true,
        maxZoom: 20,
        minZoom: 1,
        opacity: opacity,
        name: name,
        tileSize: new google.maps.Size(256, 256),
        map: map,
        url: url
    };

    //Create the image map type and insert it
    existingWMSMapType = new google.maps.ImageMapType(wmsOptions);
	
    map.overlayMapTypes.insertAt(0, existingWMSMapType);
};

EDR.EDRMapV2Google.hasOverlayMapType = function (name)
{
	var result = false;
	var mapTypeItems = map.overlayMapTypes.getArray();
    var i;
    for (i = 0; i < mapTypeItems.length; i++)
    {
        //Find the match
        if (mapTypeItems[i].name == name)
        {
            result = true;  //Match found, set indicator and exit immediately
            break;
        }
    }
	//Return our final result
	return result;
};

EDR.EDRMapV2Google.getOverlayMapType = function(name) {
	var mapTypeItems = map.overlayMapTypes.getArray();
    var i;
    for (i = 0; i < mapTypeItems.length; i++)
    {
        //Find the match
        if (mapTypeItems[i].name == name)
        {
           return mapTypeItems[i];
        }
    }    
}

EDR.EDRMapV2Google.removeOverlayMapType = function (name)
{   
    var mapTypeItems = map.overlayMapTypes.getArray();
    var i;
    for (i = 0; i < mapTypeItems.length; i++)
    {
        //Find the match
        if (mapTypeItems[i].name == name)
        {
            map.overlayMapTypes.removeAt(i);  //Match found so remove it
            break;
        }
    }    
};

EDR.EDRMapV2Google.adjustOverlayMapTypeOpacity = function (name, newOpacityValue)
{
    //Get the map types array
    var mapTypeItems = map.overlayMapTypes.getArray();
    for (j = 0; j < mapTypeItems.length; j++)
    {
        //Find the match set the opacity
        if (mapTypeItems[j].name == name)
        {
            map.overlayMapTypes.getAt(j).setOpacity(newOpacityValue);
            break;
        }
    }
};

//EDRV2.EDRMAPV3GOOGLEV3.Map.prototype.mapWMSUrl = '';
EDR.EDRMapV2Google.mapWMSGetTileUrl = function (tile, zoom)
{
    //Perform our required calculations to bet the bounding box
    var projection = map.getProjection();
    var zpow = Math.pow(2, zoom);
    var ul = new google.maps.Point(tile.x * 256.0 / zpow, (tile.y + 1) * 256.0 / zpow);
    var lr = new google.maps.Point((tile.x + 1) * 256.0 / zpow, (tile.y) * 256.0 / zpow);
    var ulw = projection.fromPointToLatLng(ul);
    var lrw = projection.fromPointToLatLng(lr);
    var bbox = ulw.lng() + "," + ulw.lat() + "," + lrw.lng() + "," + lrw.lat();

    //Calcuate the resultant URL and return it
    var resultURL = this.url;
    resultURL += ("&WIDTH=" + this.tileSize.width + "&HEIGHT=" + this.tileSize.height);
    resultURL += ("&BBOX=" + bbox);
    return resultURL;
};

EDR.EDRMapV2Google.addOverlayControlOption = function(map, overlayOptions) {
	///<summary>Adds a selectable overlay control option</summary>
	try {
		// create the parent container
		var controlDiv = document.createElement('div');
		controlDiv.style.margin = '5px';

		// add the main container 
		// NOTE: the syling here TOTALLY depends on the having only 3 google "base map" buttons (Map, Simple Map, Satellite)
		// so if that changes - we have to update the style
		var controlUI = document.createElement('div');
		controlUI.className = 'mapOverlayOption';
		// controlUI.style.backgroundColor = 'white';
		// controlUI.style.borderStyle = 'solid';
		// controlUI.style.borderWidth = '1px';
		// controlUI.style.borderColor = 'rgba(0, 0, 0, 0.14902)';
		// controlUI.style.cursor = 'pointer';
		// controlUI.style.textAlign = 'center';
		// controlUI.style.fontFamily = 'Roboto,Arial,sans-serif';
		// controlUI.style.fontSize = '11px';
		// controlUI.style.fontWeight = 'bold';
		// controlUI.style.padding = '1px 6px';
		// controlUI.style.marginRight = '-11px';
		controlDiv.appendChild(controlUI);	
		
		// add the tax map checkbox
		var cbToggleID = 'cb' + overlayOptions.typeID
		var toggleOverlayMap = document.createElement('input');
		toggleOverlayMap.type = 'checkbox';
		toggleOverlayMap.style.verticalAlign = 'middle';
		toggleOverlayMap.style.marginRight = '2px';
		toggleOverlayMap.style.marginTop = '-2px';
		toggleOverlayMap.style.marginLeft = '-2px';
		toggleOverlayMap.style.cursor = 'pointer';
		toggleOverlayMap.checked = true;
		toggleOverlayMap.id = cbToggleID;
		controlUI.appendChild(toggleOverlayMap);
		controlUI.appendChild(document.createTextNode(overlayOptions.name));

		// setup the click event listener
		google.maps.event.addDomListener(toggleOverlayMap, 'click', function(options) {
			if ((typeof(toggleOverlayMap) == 'undefined') || (toggleOverlayMap == null)) { return; }
			
			EDR.EDRMapV2Google.Log(JSON.stringify(overlayOptions));
			if (toggleOverlayMap.checked === true) {				
				// fire an event to tell that overlay map option is enabled
				EDRV2.EventCollector.fire({ type: EDR.EDRMapV2Google.EnumMapOverlayEvents.MAPOVERLAYENABLED, layer: overlayOptions.name, map: map });
				//EDR.EDRMapV2Google.setOverlayMapType(overlayOptions.typeID, overlayOptions.url, overlayOptions.opacity);			
			}
			else {
				// fire an event to tell that overlay map option is disabled
				EDRV2.EventCollector.fire({ type: EDR.EDRMapV2Google.EnumMapOverlayEvents.MAPOVERLAYDISABLED, layer: overlayOptions.name, map: map });
				//EDR.EDRMapV2Google.removeOverlayMapType(overlayOptions.typeID);			
			}
		});
		
		// add the option to the top right
		map.controls[google.maps.ControlPosition.TOP_RIGHT].push(controlDiv);
		
		// fire an event to tell that overlay map option has been added
		EDRV2.EventCollector.fire({ type: EDR.EDRMapV2Google.EnumMapOverlayEvents.OVERLAYOPTIONADDED, layer: overlayOptions.name, map: map });
		EDRV2.EventCollector.fire({ type: EDR.EDRMapV2Google.EnumMapOverlayEvents.MAPOVERLAYENABLED, layer: overlayOptions.name, map: map });
	}
	catch(e){
		EDR.EDRMapV2Google.Log('[ERROR] addOverlayControlOption: ' + e.message);
	}
};


EDR.EDRMapV2Google.triggerMapOverlayOption = function(layerName, show) {
	///<summary> Triggers the overlay map option control onclick event </summary>
	
	try {
		// validate
		layerName = EDRV2.trim(layerName);
		var overlayOption = document.getElementById('cb' + layerName);
		if (overlayOption == null) { return; }
		
		// trigger the onclick event
		if (typeof(show) != 'boolean') { show = true; }
		overlayOption.checked = show;
		google.maps.event.trigger(overlayOption, 'click');
	}
	catch(e) {
		return null;
	}
};

EDR.EDRMapV2Google.showInfoWindow = function(options) {
	/// <summary> Displays the info window </summary>
	/// <param name="options"> 
	///	Info window options - JSON object:
	///		content: Info window content
	///		marker: (optional) If given, attaches the info window to the given marker.
	///		coords: (optional) If given, displays the info window at the given coords. JSON object: { latitude: <value>, longitude: <value> }
	///	</param>
	
	try {
		// validate
		if ((typeof(options) == 'undefined') || (options == null)) { return; }
		
		var content = EDRV2.trim(options.content);
		
		var infoWindow = new google.maps.InfoWindow({
			content: content,
			pixelOffset: 0
		});
		
		if ((typeof(options.marker) == 'undefined') || (options.marker == null)) {
			// check if coords have been assigned
			if ((typeof(options.coords) == 'undefined') || (options.coords == null)) { throw new Error('Either marker, or the lat/long needs to be defined in order to display the info window'); }
			
			// convert lat/long to google latLng
			var coords = options.coords;
			if ((typeof(coords.latitude) == 'undefined') || (coords.latitude == null) || (isNaN(coords.latitude))) { throw new Error('Found invalid latitude'); }			
			if ((typeof(coords.longitude) == 'undefined') || (coords.longitude == null) || (isNaN(coords.longitude))) { throw new Error('Found invalid longitude'); }
			
			var position = new google.maps.LatLng(coords.latitude, coords.longitude);
			if (position == null) { throw new Error('Unable to convert coordinates to google LatLng point'); }
			
			// set the position of the info window
			infoWindow.setPosition(position);
			
			// display the info window
			infoWindow.open(map);
		}
		else {
			infoWindow.open(map, marker);
		}
	}
	catch(e) {
		EDR.EDRMapV2Google.Log('showInfoWindow():' + e.message);
	}
};

//******************************************************************************
//Function that is used to remove the marker
EDR.EDRMapV2Google.RemoveTPMarker = function ()
{
	if (tpMarker != null) tpMarker.setMap(null);
}

EDR.EDRMapV2Google.RemoveTPMarker.prototype.constructor = EDR.EDRMapV2Google.RemoveTPMarker;

// ************************************************************************ //
//Function that is used to initialize the marker
EDR.EDRMapV2Google.SetTPMarkerToMapCenter = function ()
{
	EDR.EDRMapV2Google.RemoveTPMarker();
	EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(map.center.lat(), map.center.lng()), base.TPMarker);
}
// constructor
EDR.EDRMapV2Google.SetTPMarkerToMapCenter.prototype.constructor = EDR.EDRMapV2Google.SetTPMarkerToMapCenter;

//Function to get the current tp marker
EDR.EDRMapV2Google.GetTPMarker = function ()
{
	return tpMarker;
}

//****************************************************************************************
//Function that is used to initialize the marker
EDR.EDRMapV2Google.SetTPMarker = function (map, position, markerSettings, reZoomCenter)
{

	var autoZoomCenter = false;
	if ((typeof (reZoomCenter) != 'undefined') && (reZoomCenter != null)) autoZoomCenter = reZoomCenter;

	if (tpMarker == null)
	{
		// create marker
		tpMarker = new google.maps.Marker({
			draggable: markerSettings.isDraggable,
			icon: markerSettings.markerIcon
		});

		// trap evevnt
		if (markerSettings.showInfoWindowMode == true)
		{
			google.maps.event.addListener(tpMarker, 'dragend', function (event)
			{
				// trigger on marker moved event
				EDR.WEBGEOCODER.onTPMarkerMoved(tpMarker);
			});
		}
	}

	// set position and display
	tpMarker.setPosition(position);
	tpMarker.setMap(map);

	// zoom & center to map if needed
	if (autoZoomCenter)
	{
		map.setCenter(position);
		map.setZoom(18);
	}

	return tpMarker;
};

// constructor
EDR.EDRMapV2Google.SetTPMarker.prototype.constructor = EDR.EDRMapV2Google.SetTPMarker;

//*************************************************************************************
EDR.EDRMapV2Google.edrLogoOnMap = function (controlDiv, logoPath)
{

	var logoHrefLink = document.createElement('A');
	logoHrefLink.setAttribute('href', '#');
	logoHrefLink.setAttribute('target', '_blank');

	var logoImage = document.createElement('IMG');

	logoImage.setAttribute('height', '47px');
	logoImage.setAttribute('width', '117px');
	logoImage.setAttribute('border', '0');
	logoImage.setAttribute('alt', 'EDR Logo');
	logoImage.setAttribute('src', logoPath);

	logoHrefLink.appendChild(logoImage);
	controlDiv.appendChild(logoHrefLink);

	// Adding padding to logo
	controlDiv.style.padding = '3px';

	google.maps.event.addDomListener(controlDiv, 'click', function ()
	{
		window.location.href = 'http://www.edrnet.com';
	});

}

EDR.EDRMapV2Google.edrLogoOnMap.prototype.constructor = EDR.EDRMapV2Google.edrLogoOnMap;

//************************************************************************************************************************
// Define the overlay, derived from google.maps.OverlayView
EDR.EDRMapV2Google.MarkerLabel = function (opt_options, markerSettings)
{
	// Initialization
	this.setValues(opt_options);

	// Label specific
	var span = this.span_ = document.createElement('span');
	span.setAttribute("class", opt_options.markerSettings.tooltipStyle);
	span.setAttribute("id", "mapTooltip");
	span.style.visibility = 'hidden';
	/*  span.style.cssText = 'position: relative; left: -50%; top: 10px; ' +
	'white-space: nowrap; border: 1px solid blue; ' +
	'padding: 10px; background-color: white'; */

	var div = this.div_ = document.createElement('div');
	div.appendChild(span);
	div.style.cssText = 'position: absolute; display: none';
};

EDR.EDRMapV2Google.MarkerLabel.prototype = new google.maps.OverlayView;

// Implement onAdd
EDR.EDRMapV2Google.MarkerLabel.prototype.onAdd = function ()
{
	var pane = this.getPanes().overlayLayer;
	pane.appendChild(this.div_);

	// Ensures the label is redrawn if the text or position is changed.
	var me = this;
	this.listeners_ = [
    google.maps.event.addListener(this, 'position_changed', function ()
    {
    	me.draw();
    }), google.maps.event.addListener(this, 'text_changed', function ()
    {
    	me.draw();
    })];
};

// Implement onRemove
EDR.EDRMapV2Google.MarkerLabel.prototype.onRemove = function ()
{
	this.div_.parentNode.removeChild(this.div_);

	// Label is removed from the map, stop updating its position/text.
	for (var i = 0, I = this.listeners_.length; i < I; ++i)
	{
		google.maps.event.removeListener(this.listeners_[i]);
	}
};

// Implement draw
EDR.EDRMapV2Google.MarkerLabel.prototype.draw = function ()
{
	var projection = this.getProjection();
	var position = projection.fromLatLngToDivPixel(this.get('position'));

	var div = this.div_;
	div.style.left = position.x + 'px';
	div.style.top = position.y + 'px';
	div.style.display = 'block';

	if (this.get('text') != null) this.span_.innerHTML = this.get('text').toString();
};

/*
	EDR Google Map Draggable Popup
*/

EDR.EDRMapV2Google.DraggablePopup = function (map, options) {
	/// <summary> Initializes the Draggable popup </summary>
	/// <param name="map"> Google map object that the popup will bind to. </param>
	/// <param name="options"> Draggable popup options. </param>

	try {
		// validate
		if ((typeof (map) == 'undefined') || (map == null)) { throw new Error('Google map object is required.'); }
		
		if (typeof draw === 'function') {
			this.draw = draw;
		}
		
		options.map = map;
		
		this.setValues(options);
	}
	catch (e) {
		this.log('[ERROR]: ' + e.message);
	}
};

// constructor
EDR.EDRMapV2Google.DraggablePopup.prototype = new google.maps.OverlayView();

// properties
EDR.EDRMapV2Google.DraggablePopup.prototype.map = null;
EDR.EDRMapV2Google.DraggablePopup.prototype.position = null;
EDR.EDRMapV2Google.DraggablePopup.prototype.title = null;
EDR.EDRMapV2Google.DraggablePopup.prototype.content = null;
EDR.EDRMapV2Google.DraggablePopup.prototype.isDraggable = true;
EDR.EDRMapV2Google.DraggablePopup.prototype.isClosable = true;
EDR.EDRMapV2Google.DraggablePopup.prototype.autoMoveIntoView = true;
EDR.EDRMapV2Google.DraggablePopup.prototype.enableLogging = true;
EDR.EDRMapV2Google.DraggablePopup.prototype.pixelOffset = 0;
EDR.EDRMapV2Google.DraggablePopup.prototype.autoPan = true;
EDR.EDRMapV2Google.DraggablePopup.prototype.arrow = {
	src: '/global/images/arrow_tooltip.png',
	width: 31,
	height: 22,
	offset: 1
};

EDR.EDRMapV2Google.DraggablePopup.prototype.onDragStart = null;
EDR.EDRMapV2Google.DraggablePopup.prototype.onDragStop = null;
EDR.EDRMapV2Google.DraggablePopup.prototype.onPopupClosed = null;
EDR.EDRMapV2Google.DraggablePopup.prototype.onDraw = null;

// css properties
EDR.EDRMapV2Google.DraggablePopup.prototype.parentCssClass = '';

// methods
EDR.EDRMapV2Google.DraggablePopup.prototype.log = function (message) {
	try {
		if (!this.enableLogging) { return; }
		console.log('[DraggablePopup] ' + message);
	}
	catch (e) {
		// do nothing
	}
};

EDR.EDRMapV2Google.DraggablePopup.prototype.isPopupDragInProgress = function() {
	/// <summary> </summary>
	try {
		// NOTE: map's draggable property is disabled when the popup is being dragged
		return !this.map.get('draggable');
	}
	catch(e) {
		this.log('Unable to get "draggable" flag');
		return true;
	}
}

EDR.EDRMapV2Google.DraggablePopup.prototype.onAdd = function () {
	try {		
		// create the container
		var container = document.createElement('div');
		
		// create a reference to the object (will be used by child event handlers)
		var that = this;

		// set the parent css class
		if (this.parentCssClass != '') {
			container.className = this.parentCssClass;
		}
		
		container.style.position = 'absolute';
		
		// add draggable attribute
		if (this.isDraggable) { container.draggable = true; }
		
		// create the main div
		var main = document.createElement('div');
		main.className = 'dragpopup-main';
		
		// create the arrow div
		var arrow = document.createElement('img');
		arrow.className = 'dragpopup-arrow';		
		arrow.src = this.arrow.src;
		arrow.style.width = this.arrow.width;
		arrow.style.height = this.arrow.height;
		
		// add the arrow to the main container
		main.appendChild(arrow);
		
		// create the body div
		var body = document.createElement('div');
		body.className = 'dragpopup-body';

		// create the header div
		var header = document.createElement('div');
		header.className = 'dragpopup-header';
		if (this.isDraggable) {
			header.style.cursor = 'move';
		}
		body.appendChild(header);
		
		var dvTitle = document.createElement('h5');
		dvTitle.className = 'dragpopup-title';
		var title = EDRV2.trim(this.title);
		if (title === '') { title = '&nbsp;'; }
		dvTitle.innerHTML = title;
		header.appendChild(dvTitle);
		
		// add the close button if needed
		var dvClose = null;
		if (this.isClosable) {
			dvClose = document.createElement('div');
			dvClose.className = 'dragpopup-close';
			dvClose.innerHTML = 'x';
			header.appendChild(dvClose);
		}

		// add the content div
		var dvContent = document.createElement('div');
		dvContent.className = 'dragpopup-content';
		var content = EDRV2.trim(this.content);
		dvContent.innerHTML = content;
		body.appendChild(dvContent);
		
		// add the body to main container
		main.appendChild(body);
		
		// add the main container
		container.appendChild(main);
		
		google.maps.event.addDomListener(container, 'click', function(evtData) {
			
			that.log('container click event triggered');
			
			evtData.cancelBubble = true;
			if (evtData.stopPropagation) { evtData.stopPropagation(); }
		});
		
		google.maps.event.addDomListener(container, 'dblclick', function(evtData) {
			
			that.log('container double click event triggered');
			
			evtData.cancelBubble = true;
			if (evtData.stopPropagation) { evtData.stopPropagation(); }
		});
		
		google.maps.event.addDomListener(dvContent, 'mousedown', function (evtData) {
			try {
				that.log('popup content mousedown event triggered');			
				//cancel the propagation in order for the dropdown click event to work on the popup
				evtData.cancelBubble = true;
				if (evtData.stopPropagation) { evtData.stopPropagation(); }
			}
			catch(e) {
				this.log('[ERROR]: ' + e.message);				
			}
		});
		
		// add the event handlers
		google.maps.event.addListener(this.get('map').getDiv(), 'mouseleave', function () {
			try {
				that.log('map mouseleave event triggered');
				
				google.maps.event.trigger(container, 'mouseup');
			}
			catch(e) {
				that.log('[ERROR]: ' + e.message);
			}
		});	

		google.maps.event.addDomListener(header, 'mousedown', function (evtData) {
			try {
				that.log('header mousedown event triggered');				
				
				this.style.cursor = 'move';
				that.map.set('draggable', false);
				that.set('origin', evtData);

				that.moveHandler = google.maps.event.addDomListener(that.get('map').getDiv(), 'mousemove', function (mapEvt) {
					try {
						that.log('map mousemove event triggered');
					
						var origin = that.get('origin');
						var left = origin.clientX - mapEvt.clientX;
						var top = origin.clientY - mapEvt.clientY;
						var pos = that.getProjection().fromLatLngToDivPixel(that.get('position'));
						var latLng = that.getProjection().fromDivPixelToLatLng(new google.maps.Point(pos.x - left, pos.y - top));

						that.set('origin', mapEvt);
						that.set('position', latLng);
						that.draw();
					}
					catch (e) {
						that.log('[ERROR]: ' + e.message);
					}
				});
			}
			catch(e) {
				this.log('[ERROR]: ' + e.message);				
			}
		});

		google.maps.event.addDomListener(header, 'mouseup', function (evtData) {
			try {
				that.log('header mouseup event triggered');
				
				that.map.set('draggable', true);
				//this.style.cursor = 'default';			
				google.maps.event.removeListener(that.moveHandler);
			}
			catch(e) {
				that.log('[ERROR]: ' + e.message);
			}
		});

		if (dvClose != null) {
			google.maps.event.addDomListener(dvClose, 'click', function () {
				that.remove();
			});
		}

		this.set('container', container)
		this.getPanes().floatPane.appendChild(container);
	}
	catch (e) {
		this.log('[ERROR]: ' + e.message);
	}
};

EDR.EDRMapV2Google.DraggablePopup.prototype.draw = function () {
	try {		
		if ((typeof(this.getProjection) == 'undefined') || (this.getProjection() == null)) {
			this.log('draw function triggered: Unable to get projection');
			return; 
		}
		var pos = this.getProjection().fromLatLngToDivPixel(this.get('position'));
		this.log('draw function triggered: ' + pos.x + ', ' + pos.y);
		
		var container = this.get('container');
		container.style.left = pos.x + 'px';
		container.style.top = pos.y + 'px';
				
		// update the height of the main container to be the height of the body
		var body = container.querySelectorAll('.dragpopup-body')[0];
		var main = container.querySelectorAll('.dragpopup-main')[0];
		main.style.height = body.clientHeight + 'px';
		
		// adjust the body, and arrow position
		var arrow = container.querySelectorAll('.dragpopup-arrow')[0];
		arrow.style.top = (-1 * (this.arrow.height / 2)) + 'px';
		arrow.style.left = this.pixelOffset + this.arrow.offset + 'px';
		
		var bodyOffsetX = this.pixelOffset + this.arrow.width;
		body.style.left = bodyOffsetX + 'px';
		
		if (this.onDraw != null) {
			this.onDraw(container);
		}
		
		// check if the offset needs to auto-panned
		if ((!this.isPopupDragInProgress()) && (this.autoPan)) {
			// figure out the body's bottom-left, and top-right point values
			var blX = pos.x + bodyOffsetX;
			var trY = pos.y + Math.abs(body.offsetTop);
			var blY = trY - body.clientHeight;
			var trX = blX + body.clientWidth;
			
			var blPoint = new google.maps.Point(blX, blY);
			var trPoint = new google.maps.Point(trX, trY);
			
			// get the lat/long from the google's point object
			var swCoord = this.getProjection().fromDivPixelToLatLng(blPoint);
			var neCoord = this.getProjection().fromDivPixelToLatLng(trPoint);
			
			this.log('SW COORD: ' + swCoord.lat() + ', ' + swCoord.lng());
			this.log('NE COORD: ' + neCoord.lat() + ', ' + neCoord.lng());
			
			// check if the bounds is inside the extent
			var mapBounds = this.map.getBounds();
			this.log('[MAP BOUNDS] SW COORD: ' + mapBounds.getSouthWest().toString());
			this.log('[MAP BOUNDS] NE COORD: ' + mapBounds.getNorthEast().toString());
			
			if ((!mapBounds.contains(neCoord)) || (!mapBounds.contains(swCoord))) {
				this.map.panToBounds(new google.maps.LatLngBounds(swCoord, neCoord));
			}
		}
	}
	catch (e) {
		this.log('[ERROR] draw(): ' + e.message);
	}
};

EDR.EDRMapV2Google.DraggablePopup.prototype.remove = function () {
	try {
		this.log('remove function triggered');
		
		this.setMap(null);
	}
	catch (e) {
		this.log('[ERROR]: ' + e.message);
	}
};

EDR.EDRMapV2Google.DraggablePopup.prototype.onRemove = function () {
	try {
		var container = this.get('container');
		container.parentNode.removeChild(container);
		
		// fire an event for onpopupclosed
		if (typeof(this.onPopupClosed) == 'function') {
			this.onPopupClosed();
		}
	}
	catch (e) {
		this.log('[ERROR]: ' + e.message);
	}
};