/// <reference path="http://localhost/global/jscripts/edrlibrary.js" />
/// <reference path="http://localhost/global/sharedresources/edrmapping/scripts/EDRMapV2.js" />

EDR.EDRMapV2GoogleV3 = {};

/**************************************************************************
START: EDR.EDRMapV2GoogleV3.Marker

Marker information implementation for Google Map API v3.

This class creates the valid and invalid marker images in the constructor
to for initial use. The intent is for user to call createValidMarkerImage()
and createInValidMarkerImage() respectively if the attributes of the image
got changed.
**************************************************************************/
EDR.EDRMapV2GoogleV3.Marker = function (markerInfo)
{
	if (this instanceof EDR.EDRMapV2GoogleV3.Marker)
	{
		// inheritance via constructor stealing
		EDR.EDRMapV2.Marker.apply(this, arguments);
		this.base = EDR.EDRMapV2.Marker.prototype;

		// create images
		this.markerIcon = this.createMarkerImage();
		this.markerInvalidIcon = this.createInvalidMarkerImage();
	}
	else
		return EDR.EDRMapV2GoogleV3.Marker(markerInfo);
};

// inheritance
EDR.EDRMapV2GoogleV3.Marker.prototype = new EDR.EDRMapV2.Marker(null);
EDR.EDRMapV2GoogleV3.Marker.prototype.constructor = EDR.EDRMapV2GoogleV3.Marker;

// returns google map v3 MarkerImage object for valid polygon
EDR.EDRMapV2GoogleV3.Marker.prototype.createMarkerImage = function ()
{
	var img = new google.maps.MarkerImage(this.markerIconURL);
	img.anchor = new google.maps.Point(this.markerIconAnchorX, this.markerIconAnchorY);

	return img;
};

// returns google map v3 MarkerImage object for invalid polygon
EDR.EDRMapV2GoogleV3.Marker.prototype.createInvalidMarkerImage = function ()
{
	var img = new google.maps.MarkerImage(this.markerInvalidIconURL);
	img.anchor = new google.maps.Point(this.markerInvalidIconAnchorX, this.markerInvalidIconAnchorY);

	return img;
};
/**************************************************************************
END: EDR.EDRMapV2GoogleV3.Marker
**************************************************************************/

/**************************************************************************
START: EDR.EDRMapV2GoogleV3.PolygonOptions

Polygon options object for Google Map API V3.

This class creates the valid and invalid marker images in the constructor
to for initial use. The intent is for user to call createValidMarkerImage()
and createInValidMarkerImage() respectively if the attributes of the image
got changed.
**************************************************************************/
EDR.EDRMapV2GoogleV3.PolygonOptions = function (opts)
{
	if (this instanceof EDR.EDRMapV2GoogleV3.PolygonOptions)
	{
		// inherits via constructor stealing
		EDR.EDRMapV2.PolygonOptions.apply(this, arguments);
		this.base = EDR.EDRMapV2.PolygonOptions.prototype;

		// create images
		this.validMarkerImage = this.createValidMarkerImage();
		this.inValidMarkerImage = this.createInValidMarkerImage();
	}
	else
		return new EDR.EDRMapV2GoogleV3.PolygonOptions(opts);
};

//inheritance and constructor
EDR.EDRMapV2GoogleV3.PolygonOptions.prototype = new EDR.EDRMapV2.PolygonOptions();
EDR.EDRMapV2GoogleV3.PolygonOptions.prototype.constructor = EDR.EDRMapV2GoogleV3.PolygonOptions;

// returns google map v3 MarkerImage object for valid polygon
EDR.EDRMapV2GoogleV3.PolygonOptions.prototype.createValidMarkerImage = function ()
{
	var img = new google.maps.MarkerImage(this.validMarkerIconURL);
	img.anchor = new google.maps.Point(this.validMarkerIconAnchorX, this.validMarkerIconAnchorY);

	return img;
};

// returns google map v3 MarkerImage object for invalid polygon
EDR.EDRMapV2GoogleV3.PolygonOptions.prototype.createInValidMarkerImage = function ()
{
	var img = new google.maps.MarkerImage(this.inValidMarkerIconURL);
	img.anchor = new google.maps.Point(this.inValidMarkerIconAnchorX, this.inValidMarkerIconAnchorY);

	return img;
};

// returns google map v3 PolygonOptions object for valid polygon
EDR.EDRMapV2GoogleV3.PolygonOptions.prototype.createValidPolygonOptions = function ()
{
	return { clickable: true, fillColor: this.validPolygonFill, fillOpacity: this.validPolygonOpacity, strokeColor: this.validPolygonLineColor, strokeOpacity: this.validPolygonLineOpacity, strokeWeight: this.validPolygonLineWeight, zIndex: 1 };
};

// returns google map v3 PolygonOptions object for invalid polygon
EDR.EDRMapV2GoogleV3.PolygonOptions.prototype.createInValidPolygonOptions = function ()
{
	return { clickable: true, fillColor: this.inValidPolygonFill, fillOpacity: this.inValidPolygonOpacity, strokeColor: this.inValidPolygonLineColor, strokeOpacity: this.inValidPolygonLineOpacity, strokeWeight: this.inValidPolygonLineWeight, zIndex: 1 };
};

EDR.EDRMapV2GoogleV3.PolygonOptions.prototype.createTaxParcelPolygonOptions = function() {
	return { clickable: true, fillColor: '#ffcc00', fillOpacity: 0.2, strokeOpacity: 0.0, strokeWeight: 0, zIndex: 4 };
};
/**************************************************************************
END: EDR.EDRMapV2GoogleV3.PolygonOptions
**************************************************************************/

/**************************************************************************
START: EDR.EDRMapV2GoogleV3.PolygonPoint

Polygon point object for Google Map API V3.
**************************************************************************/
EDR.EDRMapV2GoogleV3.PolygonPoint = function (map, latlng, polyOpts)
{
	if (this instanceof EDR.EDRMapV2GoogleV3.PolygonPoint)
	{
		// inheritance via constructor stealing
		EDR.EDRMapV2.PolygonPoint.apply(this, arguments);
		this.base = EDR.EDRMapV2.PolygonPoint.prototype;

		// create the marker
		this.marker = new google.maps.Marker({ position: latlng });
		if (polyOpts.validMarkerImage != null)
			this.marker.setIcon(polyOpts.validMarkerImage);
		else
			this.marker.setIcon(polyOpts.createValidMarkerImage());

		// creats new eventobjects
		this.eventObjects = { markerDragEvent: null, markerDragStartEvent: null, leftClickEvent: null, rightClickEvent: null };
	}
	else
		return new EDR.EDRMapV2GoogleV3.PolygonPoint(map, latlng, polyOpts);
};

// inheritance and constructor
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype = new EDR.EDRMapV2.PolygonPoint();
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.constructor = EDR.EDRMapV2GoogleV3.PolygonPoint;

// setup point for polygon editting
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.polygonEditStart = function ()
{
	// trap the dragend event for this point
	var polyPoint = this;

	if (this.eventObjects.markerDragStartEvent == null) this.eventObjects.markerDragStartEvent = google.maps.event.addListener(this.marker, "dragstart", function (event) { polyPoint.onMarkerDragStart(event); });
	if (this.eventObjects.markerDragEvent == null) this.eventObjects.markerDragEvent = google.maps.event.addListener(this.marker, "dragend", function (event) { polyPoint.onMarkerDragged(event); });
	if (this.eventObjects.leftClickEvent == null) this.eventObjects.leftClickEvent = google.maps.event.addListener(this.marker, "click", function (event) { polyPoint.onMarkerLeftClicked(event); });
	if (this.eventObjects.rightClickEvent == null) this.eventObjects.rightClickEvent = google.maps.event.addListener(this.marker, "rightclick", function (event) { polyPoint.onMarkerRightClicked(event); });

	// show this marker
	this.marker.setMap(this.mapObject);
	this.marker.setDraggable(true);

	// show the polyline
};

// setup point to stop polygon editing
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.polygonEditStop = function ()
{
	// hide this marker 
	this.marker.setMap(null);
	this.marker.setDraggable(false);	
};

EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.onMarkerDragStart = function (mouseEvt)
{
	// call event handler
	var pt = this;
	if (this.onPolygonPointDragStart != null) this.onPolygonPointDragStart(pt);
};

// handle marker dragged end event
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.onMarkerDragged = function (mouseEvt)
{
	// call event handler
	var pt = this;
	if (this.onPolygonPointDragEnd != null) this.onPolygonPointDragEnd(pt);
	if (this.onPolygonPointMoved != null) this.onPolygonPointMoved(pt);
};

// handle marker left click event
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.onMarkerLeftClicked = function (mouseEvt)
{
	// call event handler
	var pt = this;
	if (this.onPolygonPointClicked != null) this.onPolygonPointClicked(pt, true);
};

// handle marker right click event
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.onMarkerRightClicked = function (mouseEvt)
{
	// call event handler
	var pt = this;
	if (this.onPolygonPointClicked != null) this.onPolygonPointClicked(pt, false);
};

// clears this point
EDR.EDRMapV2GoogleV3.PolygonPoint.prototype.clearPoint = function ()
{
	// untrap events
	if (this.eventObjects.markerDragEvent != null)
	{
		google.maps.event.removeListener(this.eventObjects.markerDragEvent);
		this.eventObjects.markerDragEvent = null;
	}

	if (this.eventObjects.markerDragStartEvent != null)
	{
		google.maps.event.removeListener(this.eventObjects.markerDragStartEvent);
		this.eventObjects.markerDragStartEvent = null;
	}

	if (this.eventObjects.leftClickEvent != null)
	{
		google.maps.event.removeListener(this.eventObjects.leftClickEvent);
		this.eventObjects.leftClickEvent = null;
	}

	if (this.eventObjects.rightClickEvent != null)
	{
		google.maps.event.removeListener(this.eventObjects.rightClickEvent);
		this.eventObjects.rightClickEvent = null;
	}

	this.marker.setMap(null);
	this.base.clearPoint();
};
/**************************************************************************
END: EDR.EDRMapV2GoogleV3.PolygonPoint
**************************************************************************/

/****************************************************************
START: EDR.EDRMapV2GoogleV3.PolygonUtilities

Static utility functions/methods for google map V3 polygon.
*****************************************************************/
EDR.EDRMapV2GoogleV3.PolygonUtilities =
{
	/*
	calculateMaxVertexesDistance

	Return the maximum distance between vertexes.

	latLngs : Array of latLng object.
	*/
	calculateMaxVertexesDistance: function (latLngs)
	{
		// validate data
		if ((latLngs == null) || (latLngs.length == 0)) return 0;

		var maxDist = 0; // this is in meters
		var curDist = 0;

		// loop through all points except the last one since that will be measured already by the end
		// of this process
		for (var i = 0; i < (latLngs.length - 2); i++)
		{
			// loop through the points starting from i+1 (the next point from the outer loop)
			for (var j = (i + 1); j < (latLngs.length - 1); j++)
			{
				curDist = google.maps.geometry.spherical.computeDistanceBetween(latLngs[i], latLngs[j]);
				if (curDist > maxDist) maxDist = curDist;
			}
		}

		// convert to feet
		return maxDist * 3.280839895;
	},

	calculatePolygonPerimeterArea: function (polygon)
	{
		///<summary>Calculates polygon perimeter and area.</summary>
		///<param name="polygon">google.maps.Polygon object.</param>
		///<returns>EDR.EDRMapV2.PolygonInformation</returns>

		//Declare our work variables
		var polygonPath = polygon.getPath();
		var arrLatLngs = polygonPath.getArray();

		// calculate area
		var areaInMeters = google.maps.geometry.spherical.computeArea(polygonPath);
		var areaInFeet = (areaInMeters * 10.7639104); 	// convert to sq feet

		// calculate perimeter by measuring each line - in this case we are using google maps to do the work
		var perimeterInMeters = google.maps.geometry.spherical.computeLength(polygonPath);

		// convert to feet
		var perimeterInFeet = 0;
		perimeterInFeet = (perimeterInMeters * 3.2808399);

		//Create the polygon perimeter return object
		var retVal = new EDR.EDRMapV2.PolygonInformation();
		retVal.perimeterInFeet = perimeterInFeet;
		retVal.areaInSquareFeet = areaInFeet;
		retVal.perimeterFactoredInFeet = -1;
		retVal.maxDistanceInFeet = -1;

		//Return it!
		return retVal;
	},

	/*
	Name:	EDR.EDRMapV2GoogleV3.PolygonUtilities.CalculateLongestPolygonPointDistance()
	Desc:	Function to get the farthest distance  between the TP and the polygon points
	Output:	Distance of farthest point
	*/
	calculateLongestPolygonPointDistance: function (polygon, tp)
	{
		//Preconditions
		if ((!polygon) || (!polygon.getPath())) { return 0; } //if no polygon then we can just exit (0)

		var tpLatLng = tp.getPosition();
		if ((!tp) || (!tpLatLng) || tpLatLng.lat() == 0 || tpLatLng.lng() == 0) { throw new Error("Target property has not been set"); }

		//Get the lat/lng pairs and validate
		var polyLatLngs = polygon.getPath().getArray();
		if (polyLatLngs == null || polyLatLngs.length < 1) { return 0; } //If no polygon points, then just exit (0)

		//We now have the polygon points and the tp lat long, so lets compute the distance for each and find that largest value
		var greatestDistance = 0;
		var currentDistance = 0;
		for (var i = 0; i < polyLatLngs.length; i++)
		{
			currentDistance = google.maps.geometry.spherical.computeDistanceBetween(tpLatLng, polyLatLngs[i]);
			if (currentDistance > greatestDistance) { greatestDistance = currentDistance; }
		}

		// convert to feet
		return greatestDistance * 3.280839895;
	},

	/*
	Name:	EDR.EDRMapV2GoogleV3.PolygonUtilities.getPolygonCoordinatesWithClosure()
	Desc:	Function to get the coordinates of the polygon - will add the last point to close the polygon if not already there
	Output:	Null, or an array of lat lngs
	*/
	getPolygonCoordinatesWithClosure: function (poly)
	{
		//Precondition: if no polygon then we can just exit
		if ((!poly) || (!poly.getPath())) { return null; }

		//Get the lat/lng pairs and validate
		var polyLatLngs = poly.getPath().getArray();
		if (polyLatLngs == null || polyLatLngs.length < 1) { return null; }

		//Make sure 1st and last lat/lng pair are the same, if not then add a duplicate point to the end that has same lat/lng as 1st item
		if ((polyLatLngs[0].lat() != polyLatLngs[(polyLatLngs.length - 1)].lat()) || (polyLatLngs[0].lng() != polyLatLngs[(polyLatLngs.length - 1)].lng()))
		{
			//First and last items do not match, so make it
			polyLatLngs[polyLatLngs.length] = new google.maps.LatLng(polyLatLngs[0].lat(), polyLatLngs[0].lng())
		}

		//Return our result
		return polyLatLngs;
	},

	/*
	Name:	EDR.EDRMapV2GoogleV3.PolygonUtilities.isTargetPropertyWithinPolygon()
	Desc:	Checks to see if the TP is within the polygon
	Output:	True or False
	*/
	isTargetPropertyWithinPolygon: function (poly, tp)
	{
		//Preconditions
		if ((!poly) || (!poly.getPath())) { return 0; } //if no polygon then we can just exit (0)
		var tpLatLng = tp.getPosition();
		if ((!tp) || (!tpLatLng) || tpLatLng.lat() == 0 || tpLatLng.lng() == 0) { throw new Error("Target property has not been set"); }

		// Exclude points outside of bounds as there is no way they are in the poly
		var bounds = new google.maps.LatLngBounds();
		var paths = poly.getPaths();
		var path;
		for (var p = 0; p < paths.getLength(); p++)
		{
			path = paths.getAt(p);
			for (var i = 0; i < path.getLength(); i++)
			{
				bounds.extend(path.getAt(i));
			}
		}
		//We now have the bounds, so perform our basic check for the tp lat long being contained within it
		if (bounds != null && !bounds.contains(tpLatLng))
		{
			return false;
		}

		//Now we need to do a detailed check
		// Raycast point in polygon method
		var inPoly = false;

		var numPaths = poly.getPaths().getLength();
		for (var p = 0; p < numPaths; p++)
		{
			var path = poly.getPaths().getAt(p);
			var numPoints = path.getLength();
			var j = numPoints - 1;

			for (var i = 0; i < numPoints; i++)
			{
				var vertex1 = path.getAt(i);
				var vertex2 = path.getAt(j);

				if (vertex1.lng() < tpLatLng.lng() && vertex2.lng() >= tpLatLng.lng() || vertex2.lng() < tpLatLng.lng() && vertex1.lng() >= tpLatLng.lng())
				{
					if (vertex1.lat() + (tpLatLng.lng() - vertex1.lng()) / (vertex2.lng() - vertex1.lng()) * (vertex2.lat() - vertex1.lat()) < tpLatLng.lat())
					{
						inPoly = !inPoly;
					}
				}
				j = i;
			}
		}
		return inPoly;
	},

	/*
	Name:	EDR.EDRMapV2GoogleV3.PolygonUtilities.isBowTiePolygon()
	Desc:	check for bowtie condition)
	Output:	True or False
	*/
	isBowTiePolygon: function (poly)
	{
		//Get our polygon lat lngs
		var polyLatLngs = EDR.EDRMapV2GoogleV3.PolygonUtilities.getPolygonCoordinatesWithClosure(poly);

		//Loop each lat/lng
		var line1Coord1;
		var line1Coord2;
		var line2Coord1;
		var line2Coord2;
		for (var i = 0; i < (polyLatLngs.length - 1); i++)
		{
			//Set our first line coordinates
			line1Coord1 = { "y": polyLatLngs[i].lat(), "x": polyLatLngs[i].lng() };
			line1Coord2 = { "y": polyLatLngs[i + 1].lat(), "x": polyLatLngs[i + 1].lng() };

			for (var j = i + 1; j < (polyLatLngs.length - 1); j++)
			{
				//Set our second line coordinates
				//if (i == j) { continue; } //If we are on the same item then skip
				line2Coord1 = { "y": polyLatLngs[j].lat(), "x": polyLatLngs[j].lng() };
				line2Coord2 = { "y": polyLatLngs[j + 1].lat(), "x": polyLatLngs[j + 1].lng() };

				//Call to validate
				if (EDR.EDRMapV2.PolygonUtilities.areIntersectingCoordinates(line1Coord1, line1Coord2, line2Coord1, line2Coord2))
				{
					/*
					if ((EDR.WEBGEOCODER.urlHost == 'localhost') || (EDR.WEBGEOCODER.urlHost == 'idgstage02'))
					{
					document.getElementById('_CoorsPolyDebug').innerHTML = EDR.WEBGEOCODER.polygonHandler.getPolygonDVGCoordinates();
					document.getElementById('_CoorsNewPointDebug').innerHTML = 'L1C1: [' + line1Coord1.y + '/' + line1Coord1.x + '] L1C2: [' + line1Coord2.y + '/' + line1Coord2.x + '] L2C1: [' + line2Coord1.y + '/' + line2Coord1.x + '] L2C2: [' + line2Coord2.y + '/' + line2Coord2.x + ']';
					EDR.DOM.ShowHide('_CoorDebugPanel', true);
					}
					*/

					return true;
				}
			}
		}

		//We fell through, so we are valid
		return false;
	},

	/*
	Name:	EDR.EDRMapV2GoogleV3.PolygonUtilities.changePolygonColors()
	Desc:	Adjusts polygon color scheme
	Output:	UI polygon points and fill updated
	*/
	changePolygonColors: function (poly, polyPoints, polyOpts, polyPointImage)
	{
		// set polygon options
		if (poly != null) poly.setOptions(polyOpts);

		// set markers icon
		if (polyPoints && polyPoints.length > 0)
		{
			for (var i = 0; i < polyPoints.length; i++)
			{
				polyPoints[i].marker.setIcon(polyPointImage);
			}
		}
	}

};
/****************************************************************
END: EDR.EDRMapV2GoogleV3.PolygonUtilities
*****************************************************************/

/****************************************************************
START: Custom extension for google map api Polygon object.

// Polygon getBounds extension - google-maps-extensions
// http://code.google.com/p/google-maps-extensions/source/browse/google.maps.Polygon.getBounds.js
*****************************************************************/
if (!google.maps.Polygon.prototype.getBounds)
{
	google.maps.Polygon.prototype.getBounds = function (latLng)
	{
		var bounds = new google.maps.LatLngBounds();
		var paths = this.getPaths();
		var path;

		for (var p = 0; p < paths.getLength(); p++)
		{
			path = paths.getAt(p);
			for (var i = 0; i < path.getLength(); i++)
			{
				bounds.extend(path.getAt(i));
			}
		}

		return bounds;
	}
}

// Polygon containsLatLng - method to determine if a latLng is within a polygon
google.maps.Polygon.prototype.containsLatLng = function (latLng)
{
	// Exclude points outside of bounds as there is no way they are in the poly
	var bounds = this.getBounds();

	if (bounds != null && !bounds.contains(latLng))
	{
		return false;
	}

	// Raycast point in polygon method
	var inPoly = false;

	var numPaths = this.getPaths().getLength();
	for (var p = 0; p < numPaths; p++)
	{
		var path = this.getPaths().getAt(p);
		var numPoints = path.getLength();
		var j = numPoints - 1;

		for (var i = 0; i < numPoints; i++)
		{
			var vertex1 = path.getAt(i);
			var vertex2 = path.getAt(j);

			if (vertex1.lng() < latLng.lng() && vertex2.lng() >= latLng.lng() || vertex2.lng() < latLng.lng() && vertex1.lng() >= latLng.lng())
			{
				if (vertex1.lat() + (latLng.lng() - vertex1.lng()) / (vertex2.lng() - vertex1.lng()) * (vertex2.lat() - vertex1.lat()) < latLng.lat())
				{
					inPoly = !inPoly;
				}
			}

			j = i;
		}
	}

	return inPoly;
};
/****************************************************************
END: Custom extension for google map api Polygon object.
*****************************************************************/

/**************************************************************************
START: EDR.EDRMapV2GoogleV3.PolygonHandler

Polygon handler object for Google Map API V3.
**************************************************************************/
EDR.EDRMapV2GoogleV3.PolygonHandler = function (map, tpMarker, polyOpts, dvgPolyCoorsString)
{
	if (this instanceof EDR.EDRMapV2GoogleV3.PolygonHandler)
	{
		try
		{
			// validations
			if (typeof (map) == 'undefined') throw new Error('Map object is undefined.');
			if (map == null) throw new Error('Map object is null.');
			if (!(map instanceof google.maps.Map)) throw new Error('Map object is not Google Map API object.');

			// tp marker
			if ((typeof (tpMarker) != 'undefined') && (tpMarker != null)) this.tpMarker = tpMarker;

			// options
			if ((typeof (polyOpts) != 'undefined') && (polyOpts != null)) EDR.CopyObjectData(polyOpts, this.polygonOptions);

			// setup class
			this.mapObject = map;

			// create container for polygon point tooltip
			this.polyPointToolTipContainer = document.createElement('div');
			EDR.DOM.ApplyStyle(this.polyPointToolTipContainer, "position: absolute; top: 0px; left: 0px; border: 1px #1e7142 solid; font-family: Arial; font-size: 12px; display: none; z-index: 100000000;");
			map.getDiv().appendChild(this.polyPointToolTipContainer);

			// create dummy google map overlay for generic use
			this.overlay = new google.maps.OverlayView();
			this.overlay.draw = function () { };
			this.overlay.setMap(map);
			
			// add polygon click events
			if ((this.polygon != null) && (this.polygonOptions.autoEditPolygon == true))
			{
				var handler = this;
				this.eventObjects.polygonLeftClickEvent = google.maps.event.addListener(this.polygon, 'click', function (event) { handler.onPolygonLeftClicked(event); });
				this.eventObjects.polygonRightClickEvent = google.maps.event.addListener(this.polygon, 'rightclick', function (event) { handler.onPolygonRightClicked(event); });
			}
		}
		catch (err)
		{
			this.isUsable = false;
			this.initializationErrorMessage = err.Message;

			alert('Unable to create polygon handler: ' + err.message);
		}
	}
	else
		return new EDR.EDRMapV2GoogleV3.PolygonHandler(map, tpMarker, polyOpts, dvgPolyCoorsString);
};

// properties
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.isUsable = true;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.initializationErrorMessage = '';
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.isInEditMode = false;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.mapObject = null;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.tpMarker = null;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygon = null;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonOptions = new EDR.EDRMapV2GoogleV3.PolygonOptions(null);

// polygon point handlers
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polyPoint = null;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polyPointToolTipContainer = null;

// internal vars - not to be used from external sources
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.eventObjects = { mapLeftClickEvent: null, mapRightClickEvent: null, markerMoveEvent: null, mapMouseMoveEvent: null, polygonLeftClickEvent: null, polygonRightClickEvent: null };
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.overlay = null;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonExtent = null;
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonExtentBounds = null;

// events
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onPolygonEditStart = function () { return true; };
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onPolygonEditStop = function () { return true; };
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onPolygonUpdated = function () { return true; };
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onPolygonClicked = function () { return true; };

// methods
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.displayMessage = function (msg)
{
	alert(msg);
	return false;
};

// starts polygon editing process
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonEditStart = function ()
{
	// validation
	if (!this.isUsable) return this.displayMessage('Unable to start polygon editor: ' + this.initializationErrorMessage);

	// set edit mode flag
	this.isInEditMode = true;

	// keep pointer to this instance so that we can use it in the anonymous function
	var handler = this;

	// use extent if radius is set to > 0 (in feet) - if not use the whole map
	if ((this.polygonOptions.polygonExtentRadius > 0) && (this.tpMarker != null))
	{
		this.showExtent(true);
	}
	else
	{
		// change cursor to crosshair
		this.mapObject.setOptions({ draggableCursor: 'crosshair' });
	}

	// trap map event
	this.eventObjects.mapLeftClickEvent = google.maps.event.addListener(this.mapObject, 'click', function (event) { handler.onMapClicked(event); });
	this.eventObjects.mapRightClickEvent = google.maps.event.addListener(this.mapObject, 'rightclick', function (event) { handler.onMapRightClicked(event); });

	// remove polygon click events
	if (this.eventObjects.polygonLeftClickEvent != null) google.maps.event.removeListener(this.eventObjects.polygonLeftClickEvent);
	this.eventObjects.polygonLeftClickEvent = null;

	if (this.eventObjects.polygonRightClickEvent != null) google.maps.event.removeListener(this.eventObjects.polygonRightClickEvent);
	this.eventObjects.polygonRightClickEvent = null;

	// turn on polygon editing for points
	var curPolyPt = this.polyPoint;
	while (curPolyPt != null)
	{
		curPolyPt.polygonEditStart();
		curPolyPt = curPolyPt.next;
	}

	// raise event
	if (this.onPolygonEditStart != null) this.onPolygonEditStart();

	return true;
};

// stops polygon editing process
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonEditStop = function ()
{
	// validation
	if (!this.isUsable) return false;

	// set edit mode flag
	this.isInEditMode = false;

	// change cursor to crosshair
	this.mapObject.setOptions({ draggableCursor: null });

	// remove map click event
	var handler = this;
	if (this.eventObjects.mapLeftClickEvent != null) google.maps.event.removeListener(this.eventObjects.mapLeftClickEvent);
	this.eventObjects.mapLeftClickEvent = null;

	if (this.eventObjects.mapRightClickEvent != null) google.maps.event.removeListener(this.eventObjects.mapRightClickEvent);
	this.eventObjects.mapRightClickEvent = null;

	if (this.eventObjects.mapMouseMoveEvent != null) google.maps.event.removeListener(this.eventObjects.mapMouseMoveEvent);
	this.eventObjects.mapMouseMoveEvent = null;

	if (this.eventObjects.markerMoveEvent != null) google.maps.event.removeListener(this.eventObjects.markerMoveEvent);
	this.eventObjects.markerMoveEvent = null;

	// add polygon click events
	if ((this.polygon != null) && (this.polygonOptions.autoEditPolygon == true))
	{
		this.eventObjects.polygonLeftClickEvent = google.maps.event.addListener(this.polygon, 'click', function (event) { handler.onPolygonLeftClicked(event); });
		this.eventObjects.polygonRightClickEvent = google.maps.event.addListener(this.polygon, 'rightclick', function (event) { handler.onPolygonRightClicked(event); });
	}

	// hide polygon extent
	this.showExtent(false);

	// stop markers event
	var curPolyPt = this.polyPoint;
	while (curPolyPt != null)
	{
		// stop current marker
		curPolyPt.polygonEditStop();
		curPolyPt = curPolyPt.next;
	}
	
	// hide the polygon point tooltip
	this.polyPointHideToolTip();

	// raise event
	if (this.onPolygonEditStop != null) this.onPolygonEditStop();

	return true;
};

// handles map right-click event to show tooltip to add point
// note that using the polygon point tooltip here as well
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onMapRightClicked = function (mouseEvt)
{
	if (!this.isUsable) return false;

	// set new position
	var divCoor = this.overlay.getProjection().fromLatLngToContainerPixel(mouseEvt.latLng);
	EDR.DOM.ApplyStyle(this.polyPointToolTipContainer, 'top: ' + divCoor.y + 'px; left: ' + divCoor.x + 'px;');

	// build content
	var handler = this;
	var tt = '<div id=\'_GMapPolyPointTT\' style=\'padding: 2px; background-color: #f3f4c5; color: black; cursor: pointer;\' onmouseover="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointTT\', \'background-color: #1e7142; color: White;\');" onmouseout="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointTT\', \'background-color: #f3f4c5; color: Black;\');">Add point here</div>';
	tt += '<div id=\'_GMapPolyPointClose\' style=\'padding: 2px; background-color: #f3f4c5; color: black; cursor: pointer;\' onmouseover="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointClose\', \'background-color: #1e7142; color: White;\');" onmouseout="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointClose\', \'background-color: #f3f4c5; color: Black;\');">Cancel</div>';
	this.polyPointToolTipContainer.innerHTML = tt;

	// get the content to trap the onclick event
	var ttDiv = document.getElementById('_GMapPolyPointTT');
	ttDiv.onclick = function () { return handler.onMapClicked(mouseEvt); };

	ttDiv = document.getElementById('_GMapPolyPointClose');
	ttDiv.onclick = function () { return handler.polyPointHideToolTip(); };

	// show it
	EDR.DOM.ShowHide(this.polyPointToolTipContainer, true);

	return true;
};

// handles map/extent click event to add new point to the polygon
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onMapClicked = function (mouseEvt)
{
	// validation
	if (!this.isUsable) return false;

	// if polygon point was just dragged - reset flag and exit
	if (this.polygonPointDragged)
	{
		this.polygonPointDragged = false;
		return false;
	}

	// also check if extent exists, this is within the extent
	if ((this.polygonExtent != null) && (!this.polygonExtentBounds.contains(mouseEvt.latLng))) return false;

	var handler = this;

	// create polypoint
	var poly = new EDR.EDRMapV2GoogleV3.PolygonPoint(this.mapObject, mouseEvt.latLng, this.polygonOptions);
	poly.polygonEditStart();
	poly.onPolygonPointDragStart = function (pt) { handler.polygonPointDragStart(pt); };
	poly.onPolygonPointDragEnd = function (pt) { handler.polygonPointDragEnd(pt); };
	//poly.onPolygonPointMoved = function (pt) { handler.updatePolygon(pt); };
	poly.onPolygonPointClicked = function (pt, isLeftClick) { handler.polygonPointClicked(pt, isLeftClick); };

	if (this.polyPoint == null)
	{
		// this is the first point
		this.polyPoint = poly;
	}
	else
	{
		// get current coordinates
		var addToEnd = true;
		var curPolyPts = this.getPolygonPoints();

		if ((curPolyPts.length >= 3) && (this.tpMarker != null))
		{
			// to find the nearest points to add this point to
			// find the shortest intersecting line between the new point and TP
			var tpLatLng = this.tpMarker.getPosition();

			var l1c1 = { y: mouseEvt.latLng.lat(), x: mouseEvt.latLng.lng() };
			var l1c2 = { y: tpLatLng.lat(), x: tpLatLng.lng() };

			var l2c1 = null;
			var l2c2 = null;

			var curDist = -1;
			var l2Dist2 = -1;
			var l2Dist1 = -1;
			var l2Dist2 = -1;
			var intersectPt = null;

			var curNearestDist = -1;
			var closestPt1IsDefault = true;
			var closestPt1 = null;

			// set the closest

			for (var i = 0; i < curPolyPts.length; i++)
			{
				l2c1 = { y: curPolyPts[i].marker.getPosition().lat(), x: curPolyPts[i].marker.getPosition().lng() };

				if (i == (curPolyPts.length - 1))
				{
					// this is the last point - pair it w/ the first
					l2c2 = { y: curPolyPts[0].marker.getPosition().lat(), x: curPolyPts[0].marker.getPosition().lng() };
				}
				else
					l2c2 = { y: curPolyPts[i + 1].marker.getPosition().lat(), x: curPolyPts[i + 1].marker.getPosition().lng() };

				intersectPt = EDR.EDRMapV2.PolygonUtilities.getIntersectingCoordinates(l1c1, l1c2, l2c1, l2c2, false);
				if (intersectPt != null)
				{
					// found intersection - make sure this intersection is on the second line

					// distance between new point to intersection
					curDist = Math.abs(google.maps.geometry.spherical.computeDistanceBetween(mouseEvt.latLng, new google.maps.LatLng(intersectPt.y, intersectPt.x)));

					// get the max distance between line 2 to the intersection
					l2Dist = Math.abs(google.maps.geometry.spherical.computeDistanceBetween(new google.maps.LatLng(l2c1.y, l2c1.x), new google.maps.LatLng(l2c2.y, l2c2.x)));
					l2Dist1 = Math.abs(google.maps.geometry.spherical.computeDistanceBetween(new google.maps.LatLng(l2c1.y, l2c1.x), new google.maps.LatLng(intersectPt.y, intersectPt.x)));
					l2Dist2 = Math.abs(google.maps.geometry.spherical.computeDistanceBetween(new google.maps.LatLng(l2c2.y, l2c2.x), new google.maps.LatLng(intersectPt.y, intersectPt.x)));

					l2Dist1 = Math.max(l2Dist1, l2Dist2);

					// we can only consider this intersection if the max distance of line to the intersection point <= line 2 distance
					// which indicates the the 2 line SEGMENTS actually intersect
					if (l2Dist1 <= l2Dist)
					{
						// only use this point if the closest point is not yet set or the distance is shorter
						if ((curNearestDist == -1) || (curDist < curNearestDist))
						{
							// set current line as the closest
							curNearestDist = curDist;
							closestPt1 = curPolyPts[i];

							// reset flag
							closestPt1IsDefault = false;
						}
					}
				}
			}

			// at this point closestPt1 contains the point to add this new poly to
			if (closestPt1 != null)
			{
				// if closest point is the default - reset point back to last point of the polygon
				if (closestPt1IsDefault == true) closestPt1 = curPolyPts[curPolyPts.length - 1];

				poly.prev = closestPt1;
				poly.next = closestPt1.next;
				if (poly.next != null) poly.next.prev = poly;
				closestPt1.next = poly;

				// already added - so turn this off
				addToEnd = false;
			}
			else
			{
				// THIS IS JUST FOR DEBUGGING PURPOSES - comment out if not debugging
				if (EDR.WEBGEOCODER.urlHost == 'aujang')
				{
					alert('Unable to get closest line.')

					document.getElementById('_CoorsPolyDebug').innerHTML = this.getPolygonDVGCoordinates();
					document.getElementById('_CoorsNewPointDebug').innerHTML = 'Lat: ' + mouseEvt.latLng.lat().toString() + ' Lng: ' + mouseEvt.latLng.lng().toString();
					EDR.DOM.ShowHide('_CoorDebugPanel', true);
				}
			}
		}

		// by default add to end of points except when flag is set to false
		if (addToEnd)
		{
			var curPolyPt = this.polyPoint;
			while (curPolyPt.next != null)
			{
				curPolyPt = curPolyPt.next;
			}

			// set new item
			curPolyPt.next = poly;
			poly.prev = curPolyPt;
		}
	}

	// update polygon
	this.updatePolygon(true);

	return true;
};

// polygon left click event
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onPolygonLeftClicked = function (mouseEvt)
{
	if (this.onPolygonClicked != null) this.onPolygonClicked(mouseEvt, true);
};

// polygon right click event
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.onPolygonRightClicked = function (mouseEvt)
{
	if (this.onPolygonClicked != null) this.onPolygonClicked(mouseEvt, false);
};

// updates polygon on the map
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.updatePolygon = function (triggerEvent)
{
	if (!this.isUsable) return false;

	// clear polypoint tooltip
	this.polyPointHideToolTip();

	// create points array
	var polyPointCount = 0;

	var polyPoints = this.getPolygonLatLngs();
	if (polyPoints != null) polyPointCount = polyPoints.length;

	// no polygon if point < 3
	if (polyPointCount < 3)
	{
		// clear polygon if needed
		if (this.polygon != null)
		{
			this.polygon.setMap(null);
			this.polygon = null;
		}
	}
	else
	{
		// create new polygon if not yet created - if not just change the points
		if (this.polygon == null)
		{
			this.polygon = new google.maps.Polygon(this.polygonOptions.createValidPolygonOptions());
			this.polygon.setOptions({ clickable: true });
			this.polygon.setPath(polyPoints);
			this.polygon.setMap(this.mapObject);

			// trap polygon click events
			if(this.polygonOptions.autoEditPolygon == true){
				var handler = this;
				this.eventObjects.polygonLeftClickEvent = google.maps.event.addListener(this.polygon, 'click', function (event) {
					EDR.EDRMapV2Google.Log('polygon left click event triggered');
					handler.onPolygonLeftClicked(event); 
				});
				this.eventObjects.polygonRightClickEvent = google.maps.event.addListener(this.polygon, 'rightclick', function (event) { handler.onPolygonRightClicked(event); });
			}			
		}
		else
		{
			this.polygon.setPath(polyPoints);
		}
	}

	// raise event
	var triggerEvt = true;
	if ((typeof (triggerEvent) != 'undefined') && (triggerEvent == false)) triggerEvt = false;
	if ((triggerEvt) && (this.onPolygonUpdated != null)) this.onPolygonUpdated();

	return true;
};

// clears current polygon
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.removePolygon = function (triggerEvent)
{
	if (!this.isUsable) return false;

	// clear polypoint tooltip
	this.polyPointHideToolTip();

	// clear polygon points first
	var curPolyPt = this.polyPoint;
	while (curPolyPt != null)
	{
		curPolyPt.clearPoint();
		curPolyPt = curPolyPt.next;
	}

	this.polyPoint = null;

	// update polygon
	this.updatePolygon(triggerEvent);

	return true;
};

// show/hide polygon extent
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.showExtent = function (show)
{
	// exit if we don't have TP
	if (this.tpMarker == null) return false;
	if (this.polygonOptions.polygonExtentRadius <= 0.0) return false;

	var handler = this;

	// hide?
	if (show == false)
	{
		// hide extent
		if (this.polygonExtent != null) this.polygonExtent.setMap(null);
		return false;
	}
	else
	{
		// extent will be a square containing a circle with polygonExtentRadius radius
		var radius = this.polygonOptions.polygonExtentRadius * 0.3048; // convert to meters

		// create 4 corners
		var tpLatLng = this.tpMarker.getPosition();
		var extentLatLngs = new Array();

		// get offset at 0 degree
		var offSet = google.maps.geometry.spherical.computeOffset(tpLatLng, radius, 0);
		extentLatLngs.push(google.maps.geometry.spherical.computeOffset(offSet, radius, 270)); 	// nw point
		extentLatLngs.push(google.maps.geometry.spherical.computeOffset(offSet, radius, 90)); 	// ne point

		// get offset a 180 degrees
		offSet = google.maps.geometry.spherical.computeOffset(tpLatLng, radius, 180);
		extentLatLngs.push(google.maps.geometry.spherical.computeOffset(offSet, radius, 90)); 	// se point
		extentLatLngs.push(google.maps.geometry.spherical.computeOffset(offSet, radius, 270)); 	// sw point

		// since this is used by polyline we need to close the path
		extentLatLngs.push(extentLatLngs[0]);

		// create bounds
		var bounds = new google.maps.LatLngBounds();
		bounds.extend(extentLatLngs[0]);
		bounds.extend(extentLatLngs[1]);
		bounds.extend(extentLatLngs[2]);
		bounds.extend(extentLatLngs[3]);

		// create rectangle using polyline
		//var rect = new google.maps.Rectangle({ map: this.mapObject, bounds: bounds, fillColor: this.polygonOptions.polygonExtentFill, fillOpacity: this.polygonOptions.polygonExtentOpacity, strokeColor: this.polygonOptions.polygonExtentLineColor, strokeWeight: this.polygonOptions.polygonExtentLineWeight, strokeOpacity: this.polygonOptions.polygonExtentLineOpacity });
		if (this.polygonExtent == null)
		{
			var rect = new google.maps.Polyline({ strokeColor: this.polygonOptions.polygonExtentLineColor, strokeWeight: this.polygonOptions.polygonExtentLineWeight, strokeOpacity: this.polygonOptions.polygonExtentLineOpacity });
			this.polygonExtent = rect;

			//google.maps.event.addListener(rect, 'mouseover', function () { rect.setOptions({ fillColor: handler.polygonOptions.polygonExtentSelectedFill, fillOpacity: handler.polygonOptions.polygonExtentSelectedOpacity, strokeColor: handler.polygonOptions.polygonExtentSelectedLineColor, strokeWeight: handler.polygonOptions.polygonExtentSelectedLineWeight, strokeOpacity: handler.polygonOptions.polygonExtentSelectedLineOpacity }); });
			//google.maps.event.addListener(rect, 'mouseout', function () { rect.setOptions({ fillColor: handler.polygonOptions.polygonExtentFill, fillOpacity: handler.polygonOptions.polygonExtentOpacity, strokeColor: handler.polygonOptions.polygonExtentLineColor, strokeWeight: handler.polygonOptions.polygonExtentLineWeight, strokeOpacity: handler.polygonOptions.polygonExtentLineOpacity }); });
		}

		this.polygonExtent.setMap(this.mapObject);
		this.polygonExtent.setPath(extentLatLngs);
		this.polygonExtentBounds = bounds;

		// trap map mousemove and markermove events
		var mouseOverOpts = { fillColor: handler.polygonOptions.polygonExtentSelectedFill, fillOpacity: handler.polygonOptions.polygonExtentSelectedOpacity, strokeColor: handler.polygonOptions.polygonExtentSelectedLineColor, strokeWeight: handler.polygonOptions.polygonExtentSelectedLineWeight, strokeOpacity: handler.polygonOptions.polygonExtentSelectedLineOpacity };
		var mouseOutOpts = { fillColor: handler.polygonOptions.polygonExtentFill, fillOpacity: handler.polygonOptions.polygonExtentOpacity, strokeColor: handler.polygonOptions.polygonExtentLineColor, strokeWeight: handler.polygonOptions.polygonExtentLineWeight, strokeOpacity: handler.polygonOptions.polygonExtentLineOpacity };

		if (this.eventObjects.mapMouseMoveEvent == null) this.eventObjects.mapMouseMoveEvent = google.maps.event.addListener(this.mapObject, 'mousemove', function (mouseEvt) { if (handler.polygonExtentBounds.contains(mouseEvt.latLng)) { handler.polygonExtent.setOptions(mouseOverOpts); handler.mapObject.setOptions({ draggableCursor: 'crosshair' }); } else { handler.polygonExtent.setOptions(mouseOutOpts); handler.mapObject.setOptions({ draggableCursor: null }); } });
		if (this.eventObjects.markerMoveEvent == null) this.eventObjects.markerMoveEvent = google.maps.event.addListener(this.tpMarker, 'position_changed', function () { handler.polygonPointDragged = true; handler.showExtent(true); window.setTimeout(function () { handler.polygonPointDragged = false; }, 10); });
	}
};

// show polygon point tooltip
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polyPointShowToolTip = function (polyPt)
{
	if (!this.isUsable) return false;

	// set new position
	var divCoor = this.overlay.getProjection().fromLatLngToContainerPixel(polyPt.marker.getPosition());
	EDR.DOM.ApplyStyle(this.polyPointToolTipContainer, 'top: ' + divCoor.y + 'px; left: ' + divCoor.x + 'px;');

	// build content
	var handler = this;
	var tt = '<div id=\'_GMapPolyPointTT\' style=\'padding: 2px; background-color: #f3f4c5; color: black; cursor: pointer;\' onmouseover="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointTT\', \'background-color: #1e7142; color: White;\');" onmouseout="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointTT\', \'background-color: #f3f4c5; color: Black;\');">Remove point</div>';
	tt += '<div id=\'_GMapPolyPointClose\' style=\'padding: 2px; background-color: #f3f4c5; color: black; cursor: pointer;\' onmouseover="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointClose\', \'background-color: #1e7142; color: White;\');" onmouseout="javascript: EDR.DOM.ApplyStyle(\'_GMapPolyPointClose\', \'background-color: #f3f4c5; color: Black;\');">Cancel</div>';
	this.polyPointToolTipContainer.innerHTML = tt;

	// get the content to trap the onclick event
	var ttDiv = document.getElementById('_GMapPolyPointTT');
	ttDiv.onclick = function () { return handler.removePolygonPointByIndex(polyPt.getIndex()); };

	ttDiv = document.getElementById('_GMapPolyPointClose');
	ttDiv.onclick = function () { return handler.polyPointHideToolTip(); };

	// show it
	EDR.DOM.ShowHide(this.polyPointToolTipContainer, true);

	return true;
};

// hide polygon point tooltip
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polyPointHideToolTip = function ()
{
	if (!this.isUsable) return false;

	EDR.DOM.ShowHide(this.polyPointToolTipContainer, false);

	return true;
};

// handles polygon point clicked event
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonPointClicked = function (polyPt, isLeftClick)
{
	// no left click action for now
	if (isLeftClick)
	{
		//alert(polyPt.getIndex());
		return true;
	}

	// show tooltip
	this.polyPointShowToolTip(polyPt);

	return true;
};

// flag to keep track of whether polygon point was just dragged
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonPointDragged = false;

// handles polygon point drag start
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonPointDragStart = function (polyPt)
{
	this.polygonPointDragged = true;

	return true;
};

// handles polygon point drag end
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.polygonPointDragEnd = function (polyPt)
{
	// update polygon
	this.updatePolygon(true);

	// IE has a problem where map click event is still triggered after
	// marker drag end. As a workaround we set polygonPointDragged = true
	// on drag start - we need to reset this flag if map click event does not get 
	// auto-trigger
	var handler = this;
	window.setTimeout(function () { handler.polygonPointDragged = false; }, 10);

	return true;
};

// handles removing polygon point by index
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.removePolygonPointByIndex = function (index)
{
	// loop through to find the index
	var polyPts = this.getPolygonPoints();
	var polyPt = null;

	for (var i = 0; i < polyPts.length; i++)
	{
		if (i == index)
		{
			polyPt = polyPts[i];
			break;
		}
	}

	// remove point
	if (polyPt != null)
	{
		// get prev and next
		var prev = polyPt.prev;
		var next = polyPt.next;

		if ((prev != null) && (next != null))
		{
			// in between points
			prev.next = next;
			next.prev = prev;
		}
		else if ((prev == null) && (next == null))
		{
			// the only point
			this.polygon = null;
			this.polyPoint = null;
		}
		else if (prev == null)
		{
			// this is the first item
			this.polyPoint = this.polyPoint.next;
			this.polyPoint.prev = null;
			polyPt.next = null;
		}
		else if (next == null)
		{
			// this is the last item
			polyPt.prev.next = null;
			polyPt.prev = null;
		}

		// clear point
		polyPt.clearPoint();
		polyPt = null;

		// update polygon
		this.updatePolygon();

		return true;
	}
	else
		return false;
};

// handles removing polygon point
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.removePolygonPoint = function (polyPt)
{
	if ((typeof (polyPt) != 'undefined') && (polyPt != null))
		return this.removePolygonPointByIndex(polyPt.getIndex());
	else
		return false;
};

// sets polygon from DVG polygon string (lng,lat|lng,lat|...)
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.setPolygonDVGCoordinates = function (dvgCoors)
{
	if (!this.isUsable) return false;

	try
	{
		// clear current polygon
		this.removePolygon(false);

		if ((typeof (dvgCoors) != 'undefined') && (EDR.Trim(dvgCoors) != ''))
		{
			// parse
			var polyPts = new Array();
			var polyPt = null;

			// split by |
			var latLngTokens = dvgCoors.split('|');
			var latLng = null;

			var handler = this;

			// ignore the last coordinate since DVG format is closed-loop
			for (var i = 0; i < (latLngTokens.length - 1); i++)
			{
				// split by ,
				latLng = latLngTokens[i].split(',');

				// create point - note DVG format is lng first then lat
				polyPt = new EDR.EDRMapV2GoogleV3.PolygonPoint(this.mapObject, new google.maps.LatLng(latLng[1], latLng[0]), this.polygonOptions);
				polyPt.onPolygonPointMoved = function (pt) { handler.updatePolygon(pt) };
				polyPt.onPolygonPointClicked = function (pt, isLeftClick) { handler.polygonPointClicked(pt, isLeftClick); };

				// add to temp array
				polyPts.push(polyPt);
			}

			// setup points
			if (polyPts.length > 0)
			{
				var firstPt = polyPts[0];
				var prevPt = polyPts[0];

				for (var i = 1; i < polyPts.length; i++)
				{
					// get point
					polyPt = polyPts[i];

					// set link to prev point
					polyPt.prev = prevPt;
					prevPt.next = polyPt;

					// set current point as prev point
					prevPt = polyPt;
				}


				// set the first polygon point
				this.polyPoint = firstPt;
			}
		}
	}
	catch (err)
	{
		alert('Unable to set polygon from DVG coordinates: ' + err.message);
	}

	// update polygon
	this.updatePolygon(true);

	return true;
};

// return polygon coordinates in DVG format
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.getPolygonDVGCoordinates = function ()
{
	if (!this.isUsable) return '';

	// get points
	var polyPts = this.getPolygonLatLngs();
	var retVal = '';

	for (var i = 0; i < polyPts.length; i++)
	{
		retVal += polyPts[i].lng().toString() + ',' + polyPts[i].lat().toString() + '|';
	}

	// DVG format is closed loop
	if (polyPts.length > 0) retVal += polyPts[0].lng().toString() + ',' + polyPts[0].lat().toString();

	return retVal;
};

// returns array of EDR.EDRMapV2GoogleV3.PolygonPoint for the polygon.
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.getPolygonPoints = function ()
{
	if (!this.isUsable) return null;

	// create points array
	var polyPoints = new Array();

	var curPolyPt = this.polyPoint;
	while (curPolyPt != null)
	{
		polyPoints.push(curPolyPt);

		curPolyPt = curPolyPt.next;
	}

	return polyPoints;
};

// returns array of google.maps.LatLng for the polygon.
EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.getPolygonLatLngs = function ()
{
	if (!this.isUsable) return null;

	// create points array
	var polyPoints = new Array();

	var curPolyPt = this.polyPoint;
	while (curPolyPt != null)
	{
		polyPoints.push(curPolyPt.marker.getPosition());

		curPolyPt = curPolyPt.next;
	}

	return polyPoints;
};

EDR.EDRMapV2GoogleV3.PolygonHandler.prototype.validatePolygon = function (maxAreaInSqFt, maxPerimeterInFt, maxVertexDistanceInFt)
{
	///<summary>Validates polygon.</summary>
	///<param name="maxAreaInSqFt">Maximum area allowed in sq-feet.</param>
	///<param name="maxPerimeterInFt">Maximum perimeter allowed in sq-feet.</param>
	///<param name="maxVertexDistanceInFt"></param>
	///<returns>EDR.EDRMapV2.PolygonValidationResult</returns>
	var retVal = new EDR.EDRMapV2.PolygonValidationResult(null);
	retVal.isValid = false;
	retVal.errorMessage = '';
	retVal.errorMessages = new Array();

	// nothing to validate
	if (!this.isUsable)
	{
		retVal.errorMessages.push(this.initializationErrorMessage);
		retVal.errorMessage = this.initializationErrorMessage;
		return retVal;
	}

	// get polygon points
	var polyPts = this.getPolygonLatLngs();
	if (polyPts.length == 0)
	{
		// no polygon
		retVal.isValid = true;
		retVal.maxDistanceInFeet = 0;
		retVal.areaInSquareFeet = 0;
		retVal.perimeterInFeet = 0;
		retVal.perimeterFactoredInFeet = 0;
		return retVal;
	}
	else if (polyPts.length < 3)
	{
		var message = 'Incomplete polygon.';
		retVal.errorMessages.push(message);
		retVal.errorMessage = message;
		return retVal;
	}

	// conversion vars
	var cvtTo = null;
	var curValue = 0;
	var limitValue = 0;

	// constant value for checking ratio between perimeter and distance
	var maxTestAreaInSqFt = Math.pow(400, 2);

	// calculate area, perimeter, perimeter factored 
	// function returns EDR.EDRMapV2.PolygonInformation object
	//			retVal.perimeterInFeet = perimeter;
	//			retVal.areaInSquareFeet = areaInFeet;
	//			retVal.perimeterFactoredInFeet = (perimeterMaxFactor * perimeterInFeetReg);
	//			retval.maxDistanceInFeet = -1;
	var polyAttrs = EDR.EDRMapV2GoogleV3.PolygonUtilities.calculatePolygonPerimeterArea(this.polygon);
	if (polyAttrs.areaInSquareFeet > maxAreaInSqFt)
	{
		cvtTo = EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREMILES;
		curValue = EDR.EDRMapV2.PolygonUtilities.convertPolygonAreaFromSquareFeet(polyAttrs.areaInSquareFeet, cvtTo);
		limitValue = EDR.EDRMapV2.PolygonUtilities.convertPolygonAreaFromSquareFeet(maxAreaInSqFt, cvtTo);

		retVal.errorMessages.push('Current area of ' + curValue.toString() + ' mi<sup>2</sup> exceeds the limit of ' + limitValue.toString() + ' mi<sup>2</sup>.');
	}

	// get the max distance between vertexes
	var maxVertDist = EDR.EDRMapV2GoogleV3.PolygonUtilities.calculateMaxVertexesDistance(polyPts);
	if (maxVertDist > maxVertexDistanceInFt)
	{
		cvtTo = EDR.EDRMapV2.PolygonUtilities.UnitOfPerimeterMeasurementEnum.MILES;
		curValue = EDR.EDRMapV2.PolygonUtilities.convertPolygonPerimeterFromFeet(maxVertDist, cvtTo);
		limitValue = EDR.EDRMapV2.PolygonUtilities.convertPolygonPerimeterFromFeet(maxVertexDistanceInFt, cvtTo);

		retVal.errorMessages.push('Current polygon distance ' + curValue.toString() + ' mi exceeds the limit of ' + limitValue.toString() + ' mi.');
	}

	// validate points within polygon extent
	if (this.polygonExtent != null)
	{
		for (var i = 0; i < polyPts.length; i++)
		{
			if (!this.polygonExtentBounds.contains(polyPts[i]))
			{
				retVal.errorMessages.push('One or more points of the polgon exists outside of extent.');
				break;
			}
		}
	}

	if (EDR.EDRMapV2GoogleV3.PolygonUtilities.isBowTiePolygon(this.polygon)) // check for bowtie
	{
		retVal.errorMessages.push('Polylines cannot intersect.');
	}

	if ((this.tpMarker != null) && (!EDR.EDRMapV2GoogleV3.PolygonUtilities.isTargetPropertyWithinPolygon(this.polygon, this.tpMarker))) // check if TP in polygon
	{
		retVal.errorMessages.push('Target property must be within the polygon.');
	}

	if (retVal.errorMessages.length > 0)
	{
		//set the error message to the first error message
		retVal.errorMessage = retVal.errorMessages[0];
	}
	else
	{
		//no errors found...therefore its a valid polygon
		retVal.isValid = true;
		retVal.maxDistanceInFeet = polyAttrs.maxDistanceInFeet;
		retVal.areaInSquareFeet = polyAttrs.areaInSquareFeet;
		retVal.perimeterInFeet = polyAttrs.perimeterInFeet;
		retVal.perimeterFactoredInFeet = polyAttrs.perimeterFactoredInFeet;
	}

	return retVal;
};
/**************************************************************************
END: EDR.EDRMapV2GoogleV3.PolygonHandler
**************************************************************************/
