/// <reference path="http://localhost/global/jscripts/edrlibrary.js" />
/*
Name:	EDRMapV2.js
Desc:	This js library provides all the functionality needed for an EDR Map.
Note:	This js library requires that EDRLibrary (EDR namespace definition) be included in the host page before this reference.
Created:05-11-2011 5:11:00 PM
*/
//Namespace declarations
EDR.EDRMapV2 = {};
EDR.EDRMapV2.MapOptions = {};
EDR.EDRMapV2.Marker = {};
EDR.EDRMapV2.PolygonMarker = {};
EDR.EDRMapV2.Polygon = {};
EDR.EDRMapV2.PolygonUtilities = {};

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDR.EDRMapV2 = function (appName, mapHostDivID, tpInfo, mapOptions)
{
	if (this instanceof EDR.EDRMapV2)
	{
		//Initialize
		this.LastErrorMessage = '';
		this.ApplicationName = EDR.Trim(appName);
		this.MapDivID = EDR.Trim(mapHostDivID);

		//Check app name validitity
		if (this.ApplicationName == '')
		{
			this.LastErrorMessage = 'Application Name is not specified.';
			return;
		}

		//Check map div validitity
		if (this.MapDivID == '')
		{
			this.LastErrorMessage = 'Map DivID is not specified.';
			return;
		}

		this.MapDiv = EDR.DOM.GetElement(this.MapDivID);
		if (this.MapDiv == null)
		{
			this.LastErrorMessage = 'Map Div element not found.';
			return;
		}

		// set TP information if given
		if (tpInfo != null)
		{
			this.TPMarker = new EDR.EDRMapV2.Marker(tpInfo);
		}
		else
		{
			this.TPMarker = new EDR.EDRMapV2.Marker();
		}

		// convert options
		if (mapOptions instanceof EDR.EDRMapV2.MapOptions)
		{
			this.MapOptions = mapOptions;
		}
		else if (mapOptions != null)
		{
			this.MapOptions = new EDR.EDRMapV2.MapOptions(mapOptions);
		}
		else
		{
			this.MapOptions = new EDR.EDRMapV2.MapOptions();
		}

		// all good
		this.IsBaseInitError = false;
	}
	else
	{
		return new EDR.EDRMapV2(appName, mapHostDivID, tpInfo, mapOptions);
	}
};

// constructor
EDR.EDRMapV2.prototype.constructor = EDR.EDRMapV2;

//Property Definitions - general
EDR.EDRMapV2.prototype.MapOptions = null;
EDR.EDRMapV2.prototype.IsPolyMode = false;
EDR.EDRMapV2.prototype.ApplicationName = '';
EDR.EDRMapV2.prototype.LastErrorMessage = '';
EDR.EDRMapV2.prototype.IsBaseInitError = true;
EDR.EDRMapV2.prototype.TPMarker = null;

//Events
EDR.EDRMapV2.prototype.OnMarkerChange = null;
EDR.EDRMapV2.prototype.OnTPMarkerMoved = null;
EDR.EDRMapV2.prototype.OnMapEvents = null;
EDR.EDRMapV2.prototype.OnInfoWindowEvents = null;
EDR.EDRMapV2.prototype.OnTPPolygonPointEvent = null;
EDR.EDRMapV2.prototype.OnError = null;

//Functions
EDR.EDRMapV2.prototype.InitializeMap = function () { };
EDR.EDRMapV2.prototype.SetTPMarker = function () { };
EDR.EDRMapV2.prototype.ChangeMapAttr = function () { };
EDR.EDRMapV2.prototype.DrawMarker = function () { };
EDR.EDRMapV2.prototype.RemoveMarker = function () { };
EDR.EDRMapV2.prototype.ClearTPPolygon = function () { };
EDR.EDRMapV2.prototype.CreateTPPolygon = function () { };
EDR.EDRMapV2.prototype.UnloadMap = function ()
{
	// clean up
	this.MapDiv = null;
	return true;
};
EDR.EDRMapV2.prototype.ResizeMap = function () { };
EDR.EDRMapV2.prototype.GetTPMarker = function () { };
EDR.EDRMapV2.prototype.GetTPPolygon = function () { };
EDR.EDRMapV2.prototype.IsPolygonValid = function () { };
EDR.EDRMapV2.prototype.IsTPValid = function () { }; //Will return null, true, or false
EDR.EDRMapV2.prototype.IsLatLongValid = function () { };

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDR.EDRMapV2.MapOptions = function (mapOptions)
{
	if (this instanceof EDR.EDRMapV2.MapOptions)
	{
		if (mapOptions != null)
		{
			EDR.CopyObjectData(mapOptions, this);
		} //convert from json to our object so all default values, etc. are correctly set
	} else
	{
		return new EDR.EDRMapV2.MapOptions(mapOptions);
	}
};

// constructor
EDR.EDRMapV2.MapOptions.prototype.constructor = EDR.EDRMapV2.MapOptions;

//Property Definitions - Basic map options
EDR.EDRMapV2.MapOptions.prototype.MapEngine = 1;
EDR.EDRMapV2.MapOptions.prototype.EnumMapEngines = {
	GOOGLE: 1
}; //Add additional types here
EDR.EDRMapV2.MapOptions.prototype.Tilt = 0;
EDR.EDRMapV2.MapOptions.prototype.InitialLatitude = 39.02010;
EDR.EDRMapV2.MapOptions.prototype.InitialLongitude = -96.926791;
EDR.EDRMapV2.MapOptions.prototype.MapWidth = 975;
EDR.EDRMapV2.MapOptions.prototype.MapHeight = 660;
EDR.EDRMapV2.MapOptions.prototype.Images = []; // array of EDR.ImageInformation
EDR.EDRMapV2.MapOptions.prototype.ImageTypes = {
	TPMARKER: 1,
	TPMARKERDRAG: 2
};
EDR.EDRMapV2.MapOptions.prototype.EdrLogoPath = '/global/images/edrlogo.png';

//Property Definitions - Zoom options
EDR.EDRMapV2.MapOptions.prototype.ShowZoomControl = true; // true - show zoom control, false - no zoom control
EDR.EDRMapV2.MapOptions.prototype.ZoomStyleType = 4; // this is zoom control type based (specific to API implementation)
EDR.EDRMapV2.MapOptions.prototype.EnumZoomStyleTypes = {
	DEFAULT: 1,
	SMALL: 2,
	SMALL3D: 3,
	LARGE: 4,
	LARGE3D: 5
}; // this is zoom control types based (specific to API implementation)
EDR.EDRMapV2.MapOptions.prototype.InitialZoomLevel = 4;
EDR.EDRMapV2.MapOptions.prototype.TPZoomLevel = 18;
EDR.EDRMapV2.MapOptions.prototype.MinZoomLevel = 0;
EDR.EDRMapV2.MapOptions.prototype.MaxZoomLevel = 50;

//Property Definitions - Map type options
EDR.EDRMapV2.MapOptions.prototype.ShowMapTypesControl = true; // true - show map type control, false otherwise
EDR.EDRMapV2.MapOptions.prototype.DefaultMapType = 1; // map type (bitwise) (specific to API implementation)
EDR.EDRMapV2.MapOptions.prototype.MapType = 1; // map type (bitwise) (specific to API implementation)
EDR.EDRMapV2.MapOptions.prototype.EnumMapTypes = {
	ROADMAP: 1,
	SATELLITE: 2,
	HYBRID: 4,
	TERRAIN: 8
}; // map types (specific to API implementation)
EDR.EDRMapV2.MapOptions.prototype.MapTypeControlPosition = 7;
EDR.EDRMapV2.MapOptions.prototype.MapTypeControlStyle = 2; // map type control style (specific to API implementation)
EDR.EDRMapV2.MapOptions.prototype.EnumMapTypeControlStyles = {
	NORMAL: 1,
	DROPDOWN: 2,
	HORIZONTAL: 3
}; // map type control styles (specific to API implementation)
//Property Definitions - Map behaviors
EDR.EDRMapV2.MapOptions.prototype.IsMapDraggable = true; // true - enable map to be draggable
EDR.EDRMapV2.MapOptions.prototype.IsMarkerDraggable = true; // true - enable marker to be draggable
EDR.EDRMapV2.MapOptions.prototype.IsMouseWheelEnabled = true; // true - allow mousewheel feature
EDR.EDRMapV2.MapOptions.prototype.IsKeyboardEnabled = true; // true - allow keyboard shortcuts feature
EDR.EDRMapV2.MapOptions.prototype.AutoSnapToTP = true; // true - snap center of the map to TP when SetTP() is called
EDR.EDRMapV2.MapOptions.prototype.InitializeTPMap = true; // true - initialize map automatically, false otherwise (caller needs to specifically call SetTP())

/**************************************************************************
START: EDR.EDRMapV2.Marker

Base class for marker information (usually used for TP marker but can be
used for any other marker type as well).
**************************************************************************/
EDR.EDRMapV2.Marker = function (markerInfo)
{
	if (this instanceof EDR.EDRMapV2.Marker)
	{
		if ((typeof(markerInfo) != 'undefined') && (markerInfo != null))
		{
			EDR.CopyObjectData(markerInfo, this);
		} //convert from json to our object so all default values, etc. are correctly set
	} 
	else 
		return new EDR.EDRMapV2.Marker(markerInfo);
};

// constructor
EDR.EDRMapV2.Marker.prototype.constructor = EDR.EDRMapV2.Marker;
EDR.EDRMapV2.Marker.prototype.base = null;	// set by derived class

//Property Definitions - Basic marker options
EDR.EDRMapV2.Marker.prototype.siteName = null;
EDR.EDRMapV2.Marker.prototype.address = null;
EDR.EDRMapV2.Marker.prototype.city = null;
EDR.EDRMapV2.Marker.prototype.state = null;
EDR.EDRMapV2.Marker.prototype.zipCode = null;
EDR.EDRMapV2.Marker.prototype.fips = null;
EDR.EDRMapV2.Marker.prototype.county = null;
EDR.EDRMapV2.Marker.prototype.postalCity = null;
EDR.EDRMapV2.Marker.prototype.latitude = null;
EDR.EDRMapV2.Marker.prototype.longitude = null;

EDR.EDRMapV2.Marker.prototype.markerIcon = null;
EDR.EDRMapV2.Marker.prototype.markerInvalidIcon = null;
EDR.EDRMapV2.Marker.prototype.markerIconURL = '/Global/images/EDRGoogleMap/tpstar.png';
EDR.EDRMapV2.Marker.prototype.markerIconAnchorX = 13;
EDR.EDRMapV2.Marker.prototype.markerIconAnchorY = 13;
EDR.EDRMapV2.Marker.prototype.markerInvalidIconURL = '/Global/images/EDRGoogleMap/tpstarred.png';
EDR.EDRMapV2.Marker.prototype.markerInvalidIconAnchorX = 13;
EDR.EDRMapV2.Marker.prototype.markerInvalidIconAnchorY = 13;
EDR.EDRMapV2.Marker.prototype.infoWindowStyle = {};
EDR.EDRMapV2.Marker.prototype.tooltipText = null;
EDR.EDRMapV2.Marker.prototype.tooltipStyle = 'baseTooltip';
EDR.EDRMapV2.Marker.prototype.isDraggable = true;
EDR.EDRMapV2.Marker.prototype.EnumActionModes = {
	MouseOver: 1,
	MouseOut: 2,
	Click: 4
};
EDR.EDRMapV2.Marker.prototype.showTooltipMode = 1; //Bitwise
EDR.EDRMapV2.Marker.prototype.hideTooltipMode = 0; //Bitwise
EDR.EDRMapV2.Marker.prototype.showInfoWindowMode = 1; //Bitwise
EDR.EDRMapV2.Marker.prototype.hideInfoWindowMode = 0; //Bitwise

// when overriden, returns the marker image object for valid polygon which is also
// used as default icon (specific to the engine)
EDR.EDRMapV2.Marker.prototype.createMarkerImage = function () { return null };

// when overriden, returns the marker image object for invalid polygon (specific to the engine)
EDR.EDRMapV2.Marker.prototype.createInvalidMarkerImage = function () { return null };

/**************************************************************************
END: EDR.EDRMapV2.Marker
**************************************************************************/

//************************************************************************************************
//NOTE: EDRLibrary.js, EDRMapV2.js and jquery-1.5.js are required to use the classes, objects, etc in this file
//************************************************************************************************

//Instantiate Namespaces
EDR.EDRMapV2.GeocodeResult = {};
EDR.EDRMapV2.GeocodedLocation = {};
EDR.EDRMapV2.GeocodedLastLine = {};

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//EDR Map Geocode Result Class
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDR.EDRMapV2.GeocodeResult = function ()
{
	try
	{
		//check if the object is of type GeocodeResult
		if (this instanceof EDR.EDRMapV2.GeocodeResult)
		{
		}
		else
		{
			//if not, instantiate a new object as GeocodeResult and return that object
			return new EDR.EDRMapV2.GeocodeResult();
		}
	}
	catch (err)
	{
		alert(err);
	}
};

//Constructor
EDR.EDRMapV2.GeocodeResult.prototype.constructor = EDR.EDRMapV2.GeocodeResult;

//Properties
EDR.EDRMapV2.GeocodeResult.prototype.EnumGeocodeStatus = { EXACTMATCH: 1, ADDRESSCANDIDATES: 2, LASTLINECANDIDATES: 3, ERROR: 4, NONE: 5 };
EDR.EDRMapV2.GeocodeResult.prototype.GeocodeStatus = null;
EDR.EDRMapV2.GeocodeResult.prototype.ErrorMessage = "";
EDR.EDRMapV2.GeocodeResult.prototype.ExactMatch = null; 		//GeocodeLocation
EDR.EDRMapV2.GeocodeResult.prototype.AddressCandidates = null; 	//GeocodedLocation[]
EDR.EDRMapV2.GeocodeResult.prototype.LastLineCandidates = null; //GeocodedLastLine[]
EDR.EDRMapV2.GeocodeResult.prototype.CandidatesListHTML = ''; // candidates list HTML fragment

//Functions
//Parses xml document and populates properties (xmlDoc is jQuery xmlDoc)
EDR.EDRMapV2.GeocodeResult.prototype.LoadFromXML = function (xmlDoc)
{
	try
	{
		this.GeocodeStatus = this.EnumGeocodeStatus.NONE;
		if (xmlDoc != null)
		{
			var status = null;
			//find the status node and get the result value
			status = EDR.Trim(xmlDoc.find("status").attr('result'));

			//check if geocode status exists
			if (status == null)
			{
				//since no status was found, set the status to error
				this.GeocodeStatus = EnumGeocodeStatus.ERROR;
				this.ErrorMessage = "Failed to retrieve geocode status!";
				return false;
			}


			//convert the status value to EnumGeocodeStatus	and set the values
			switch (status)
			{
				case "exactmatch":
					this.GeocodeStatus = this.EnumGeocodeStatus.EXACTMATCH;

					var location = new EDR.EDRMapV2.GeocodedLocation();
					location.LoadFromXML(xmlDoc.find("exactmatch"));
					this.ExactMatch = location;

					break;
				case "addresscandidates":
					this.GeocodeStatus = this.EnumGeocodeStatus.ADDRESSCANDIDATES;

					var locationList = new Array();
					var j = 0;
					xmlDoc.find("addresscandidates").each(function ()
					{
						var location = new EDR.EDRMapV2.GeocodedLocation();
						location.LoadFromXML($(this));
						locationList[j] = location;
						j += 1;
					});
					this.AddressCandidates = locationList;

					break;
				case "lastlinecandidates":
					this.GeocodeStatus = this.EnumGeocodeStatus.LASTLINECANDIDATES;

					var lastLineList = new Array();
					var j = 0;
					xmlDoc.find("lastlinecandidates").each(function ()
					{
						var lastLine = new EDR.EDRMapV2.GeocodedLastLine();
						lastLine.LoadFromXML($(this));
						lastLineList[j] = lastLine;
						j += 1;
					});
					this.LastLineCandidates = lastLineList;
					break;
				case "error":
					this.GeocodeStatus = this.EnumGeocodeStatus.ERROR;
					this.ErrorMessage = EDR.Trim(xmlDoc.find("error").attr("message"));
					break;
				default:
					this.GeocodeStatus = this.EnumGeocodeStatus.NONE;
			}

			// convert html fragment
			var htmlNode = xmlDoc.find("candidateshtmlfragment");
			if (htmlNode != null) this.CandidatesListHTML = EDR.Trim(htmlNode.attr("html"));
		}
	}
	catch (err)
	{
		alert(err);
	}
};


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//EDR Map Geocode Location Class
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDR.EDRMapV2.GeocodedLocation = function ()
{
	try
	{
		//check if the object is of type GeocodedLocation
		if (this instanceof EDR.EDRMapV2.GeocodedLocation)
		{
		}
		else
		{
			//if not, instantiate a new object as GeocodedLocation and return that object
			return new EDR.EDRMapV2.GeocodedLocation();
		}
	}
	catch (err)
	{
		alert(err);
	}
};

//Constructor
EDR.EDRMapV2.GeocodedLocation.prototype.constructor = EDR.EDRMapV2.GeocodedLocation;

//Properties
EDR.EDRMapV2.GeocodedLocation.prototype.SiteName = "";
EDR.EDRMapV2.GeocodedLocation.prototype.Address = "";
EDR.EDRMapV2.GeocodedLocation.prototype.City = "";
EDR.EDRMapV2.GeocodedLocation.prototype.State = "";
EDR.EDRMapV2.GeocodedLocation.prototype.ZipCode = "";
EDR.EDRMapV2.GeocodedLocation.prototype.Latitude = 0;
EDR.EDRMapV2.GeocodedLocation.prototype.Longitude = 0;
EDR.EDRMapV2.GeocodedLocation.prototype.FIPS = "";
EDR.EDRMapV2.GeocodedLocation.prototype.County = "";
EDR.EDRMapV2.GeocodedLocation.prototype.PostalCity = "";
EDR.EDRMapV2.GeocodedLocation.prototype.GeocodedScore = 0;

//Functions
//Parses xml node and populates properties (xmlDoc is jQuery xmlDoc)
EDR.EDRMapV2.GeocodedLocation.prototype.LoadFromXML = function (xmlNode)
{
	if (xmlNode)
	{
		this.SiteName = EDR.Trim(xmlNode.attr("sitename"));
		this.Address = EDR.Trim(xmlNode.attr("address"));
		this.City = EDR.Trim(xmlNode.attr("city"));
		this.State = EDR.Trim(xmlNode.attr("state"));
		this.ZipCode = EDR.Trim(xmlNode.attr("zipcode"));
		var lat = EDR.Trim(xmlNode.attr("latitude"));
		if (lat == "") lat = "0";
		this.Latitude = parseFloat(lat);
		var lng = EDR.Trim(xmlNode.attr("longitude"));
		if (lng == "") lng = "0";
		this.Longitude = parseFloat(lng);
		this.FIPS = EDR.Trim(xmlNode.attr("fips"));
		this.County = EDR.Trim(xmlNode.attr("county"));
		this.PostalCity = EDR.Trim(xmlNode.attr("postalcity"));
		var score = EDR.Trim(xmlNode.attr("geocodedscore"));
		if (score == "") score = "0";
		this.GeocodedScore = parseInt(score);
	}
};


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//EDR Map Geocode LastLine Class
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDR.EDRMapV2.GeocodedLastLine = function ()
{
	//check if the object is of type GeocodedLastLine
	if (this instanceof EDR.EDRMapV2.GeocodedLastLine)
	{
	}
	else
	{
		//if not, instantiate a new object as GeocodedLastLine and return that object
		return new EDR.EDRMapV2.GeocodedLastLine();
	}
};

//Constructor
EDR.EDRMapV2.GeocodedLastLine.prototype.constructor = EDR.EDRMapV2.GeocodedLastLine;

//Properties
EDR.EDRMapV2.GeocodedLastLine.prototype.City = "";
EDR.EDRMapV2.GeocodedLastLine.prototype.State = "";
EDR.EDRMapV2.GeocodedLastLine.prototype.ZipCode = "";

//Functions
//Parses xml node and populates properties (xmlDoc is jQuery xmlDoc)
EDR.EDRMapV2.GeocodedLastLine.prototype.LoadFromXML = function (xmlNode)
{
	if (xmlNode)
	{
		this.City = EDR.Trim(xmlNode.attr("city"));
		this.State = EDR.Trim(xmlNode.attr("state"));
		this.ZipCode = EDR.Trim(xmlNode.attr("zipcode"));
	}
};

//************************************************************************************************
//NOTE: EDRLibrary.js, EDRMapV2.js and jquery-1.5.js are required to use the classes, objects, etc in this file
//************************************************************************************************

//Instantiate Namespaces
EDR.EDRMapV2.ReverseGeocodeResult = {};

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//EDR Map Reverse Geocode Class
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDR.EDRMapV2.ReverseGeocodeResult = function ()
{
	try
	{
		//check if the object is of type ReverseGeocode
		if (this instanceof EDR.EDRMapV2.ReverseGeocodeResult)
		{
		}
		else
		{
			//if not, instantiate a new object as ReverseGeocode and return that object
			return new EDR.EDRMapV2.ReverseGeocodeResult();
		}
	}
	catch (err)
	{
		alert(err);
	}
}

//Constructor
EDR.EDRMapV2.ReverseGeocodeResult.prototype.constructor = EDR.EDRMapV2.ReverseGeocodeResult;

//Properties
EDR.EDRMapV2.ReverseGeocodeResult.prototype.EnumReverseGeocodeStatus = { SUCCESSFULL: 1, ERROR: 2, NONE: 3 };
EDR.EDRMapV2.ReverseGeocodeResult.prototype.ReverseGeocodeStatus = null;
EDR.EDRMapV2.ReverseGeocodeResult.prototype.ErrorMessage = "";
EDR.EDRMapV2.ReverseGeocodeResult.prototype.County = "";
EDR.EDRMapV2.ReverseGeocodeResult.prototype.City = "";
EDR.EDRMapV2.ReverseGeocodeResult.prototype.State = "";
EDR.EDRMapV2.ReverseGeocodeResult.prototype.FIPS = "";
EDR.EDRMapV2.ReverseGeocodeResult.prototype.PostalCity = "";
EDR.EDRMapV2.ReverseGeocodeResult.prototype.ZipCode = "";

//Functions (xmlDoc is jQuery xmlDoc)
EDR.EDRMapV2.ReverseGeocodeResult.prototype.LoadFromXML = function (xmlDoc)
{
	try
	{
		if (xmlDoc != null)
		{
			var status = null;
			//find the status node and get the result value
			status = EDR.Trim(xmlDoc.find("status").attr("result"));

			//check if status exists
			if (status == null)
			{
				//since no status was found, set the status to error
				this.ReverseGeocodeStatus = this.EnumReverseGeocodeStatus.ERROR;
				this.ErrorMessage = "Failed to retrieve reverse geocode status!";
				return false;
			}

			switch (status)
			{
				case "ok":
					//get the addressinfo node
					var addrInfoNode = xmlDoc.find("addressinfo");
					if (addrInfoNode != null)
					{
						this.County = EDR.Trim(addrInfoNode.attr("county"));
						this.City = EDR.Trim(addrInfoNode.attr("city"));
						this.State = EDR.Trim(addrInfoNode.attr("state"));
						this.FIPS = EDR.Trim(addrInfoNode.attr("fips"));
						this.PostalCity = EDR.Trim(addrInfoNode.attr("postalcity"));
						this.ZipCode = EDR.Trim(addrInfoNode.attr("zipcode"));
						//set the status
						this.ReverseGeocodeStatus = this.EnumReverseGeocodeStatus.SUCCESSFULL;
					}
					else
					{
						this.ReverseGeocodeStatus = this.EnumReverseGeocodeStatus.ERROR;
						this.ErrorMessage = "Found insufficient address information in the result!";
					}
					break;
				case "error":
					this.ReverseGeocodeStatus = this.EnumReverseGeocodeStatus.ERROR;
					this.ErrorMessage = EDR.Trim(xmlDoc.find("error").attr("message"));
					break;
				default:
					this.ReverseGeocodeStatus = this.EnumReverseGeocodeStatus.NONE;
			}
		}
	}
	catch (err)
	{
		alert(err);
	}
}

//Instantiate Namespaces
EDR.EDRMapV2.SavePolygonInfoResult = {};

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//EDR Map Reverse Geocode Class
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
EDR.EDRMapV2.SavePolygonInfoResult = function ()
{
	try
	{
		//check if the object is of type SavePolygonInfoResult
		if (this instanceof EDR.EDRMapV2.SavePolygonInfoResult)
		{
		}
		else
		{
			//if not, instantiate a new object as SavePolygonInfoResult and return that object
			return new EDR.EDRMapV2.SavePolygonInfoResult();
		}
	}
	catch (err)
	{
		alert(err);
	}
}

//Constructor
EDR.EDRMapV2.SavePolygonInfoResult.prototype.constructor = EDR.EDRMapV2.SavePolygonInfoResult;

//Properties
EDR.EDRMapV2.SavePolygonInfoResult.prototype.EnumSavePolygonInfoStatus = { SUCCESSFULL: 1, ERROR: 2, NONE: 3 };
EDR.EDRMapV2.SavePolygonInfoResult.prototype.SavePolygonInfoStatus = null;
EDR.EDRMapV2.SavePolygonInfoResult.prototype.ErrorMessage = "";

//Functions (xmlDoc is jQuery xmlDoc)
EDR.EDRMapV2.SavePolygonInfoResult.prototype.LoadFromXML = function (xmlDoc)
{
	try
	{
		if (xmlDoc != null)
		{
			var status = null;
			//find the status node and get the result value
			status = EDR.Trim(xmlDoc.find("status").attr("result"));

			//check if status exists
			if (status == null)
			{
				//since no status was found, set the status to error
				this.SavePolygonInfoStatus = this.EnumSavePolygonInfoStatus.ERROR;
				this.ErrorMessage = "Failed to retrieve save polygon information status!";
				return false;
			}

			switch (status)
			{
				case "ok":
					//get the addressinfo node
					this.SavePolygonInfoStatus = this.EnumSavePolygonInfoStatus.SUCCESSFULL;
					this.ErrorMessage = "";
					break;
				case "error":
					this.SavePolygonInfoStatus = this.EnumSavePolygonInfoStatus.ERROR;
					this.ErrorMessage = EDR.Trim(xmlDoc.find("error").attr("message"));
					break;
				default:
					this.SavePolygonInfoStatus = this.EnumSavePolygonInfoStatus.NONE;
			}
		}
	}
	catch (err)
	{
		alert(err);
	}
}

/****************************************************************
START: EDR.EDRMapV2.PolygonInformation

Class to hold polygon information such as area, perimeter, and
max distance.
*****************************************************************/
EDR.EDRMapV2.PolygonInformation = function (result)
{
	if (this instanceof EDR.EDRMapV2.PolygonInformation)
	{
		if ((typeof (polygonInfo) != 'undefined') && (polygonInfo != null)) EDR.CopyObjectData(result, this);
	}
	else
		return new EDR.EDRMapV2.PolygonInformation(result);
};

// constructor
EDR.EDRMapV2.PolygonInformation.prototype.constructor = EDR.EDRMapV2.PolygonInformation;
EDR.EDRMapV2.PolygonInformation.prototype.base = null; // should be set by derived class

// properties
EDR.EDRMapV2.PolygonInformation.prototype.maxDistanceInFeet = -1;
EDR.EDRMapV2.PolygonInformation.prototype.areaInSquareFeet = -1;
EDR.EDRMapV2.PolygonInformation.prototype.perimeterInFeet = -1;
EDR.EDRMapV2.PolygonInformation.prototype.perimeterFactoredInFeet = -1;
/****************************************************************
END: EDR.EDRMapV2.PolygonInformation
*****************************************************************/

/****************************************************************
START: EDR.EDRMapV2.PolygonValidationResult

Class to hold polygon validation result. This class contains the
the information whether polygon is valid or not. If it is valid,
it also contains attributes of the polygon.
*****************************************************************/
EDR.EDRMapV2.PolygonValidationResult = function (result)
{
	if (this instanceof EDR.EDRMapV2.PolygonValidationResult)
	{
		// inheritance via constructor stealing
		EDR.EDRMapV2.PolygonInformation.apply(this, arguments);
		this.base = EDR.EDRMapV2.PolygonInformation.prototype;
	}
	else
		return new EDR.EDRMapV2.PolygonValidationResult(result);
};

// constructor
EDR.EDRMapV2.PolygonValidationResult.prototype.constructor = EDR.EDRMapV2.PolygonValidationResult;

// properties
EDR.EDRMapV2.PolygonValidationResult.prototype.isValidPolygon = false;
EDR.EDRMapV2.PolygonValidationResult.prototype.errorMessage = '';
EDR.EDRMapV2.PolygonValidationResult.prototype.errorMessages = new Array();
/****************************************************************
END: EDR.EDRMapV2.PolygonValidationResult
*****************************************************************/

/**************************************************************************
START: EDR.EDRMapV2.PolygonOptions

Base class for polygon options. Note that there are few methods
that are required to be overridden due to specific implementation of
mapping engine.

Derived class should set the validMarkerImage and inValidMarker image in
the constructor so that only 1 instance of each image types are created. 
Of course this is optional depending on implementation.
**************************************************************************/
EDR.EDRMapV2.PolygonOptions = function (opts)
{
	if (this instanceof EDR.EDRMapV2.PolygonOptions)
	{
		if ((typeof (opts) != 'undefined') && (opts != null)) EDR.CopyObjectData(opts, this); 	// copy options from argument
	}
	else
		return new EDR.EDRMapV2.PolygonOptions(opts);
};

// constructor
EDR.EDRMapV2.PolygonOptions.prototype.constructor = EDR.EDRMapV2.PolygonOptions;
EDR.EDRMapV2.PolygonOptions.prototype.base = null; // base should be set by the derived class

// extent settings (normally used to limit where polygon can be drawn
EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentRadius = 0;

EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentFill = 'transparent';
EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentOpacity = 0.0;

EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentLineColor = '#C0C0C0';
EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentLineWeight = 2;
EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentLineOpacity = 1;

EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentSelectedFill = 'transparent';
EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentSelectedOpacity = 0.0;

EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentSelectedLineColor = '#505050';
EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentSelectedLineWeight = 2;
EDR.EDRMapV2.PolygonOptions.prototype.polygonExtentSelectedLineOpacity = 0.7;

EDR.EDRMapV2.PolygonOptions.prototype.autoEditPolygon = true;

// valid polygon marker image information
EDR.EDRMapV2.PolygonOptions.prototype.validMarkerImage = null;
EDR.EDRMapV2.PolygonOptions.prototype.validMarkerIconURL = '/global/sharedresources/edrmapping/images/drawhandle.png';
EDR.EDRMapV2.PolygonOptions.prototype.validMarkerIconAnchorX = 8;
EDR.EDRMapV2.PolygonOptions.prototype.validMarkerIconAnchorY = 8;

// invalid polygon marker image information
EDR.EDRMapV2.PolygonOptions.prototype.inValidMarkerImage = null;
EDR.EDRMapV2.PolygonOptions.prototype.inValidMarkerIconURL = '/global/sharedresources/edrmapping/images/drawhandlered.png';
EDR.EDRMapV2.PolygonOptions.prototype.inValidMarkerIconAnchorX = 8;
EDR.EDRMapV2.PolygonOptions.prototype.inValidMarkerIconAnchorY = 8;

// valid polygon options
EDR.EDRMapV2.PolygonOptions.prototype.validPolygonFill = '#9CD6B1';
EDR.EDRMapV2.PolygonOptions.prototype.validPolygonOpacity = 0.35;

EDR.EDRMapV2.PolygonOptions.prototype.validPolygonLineColor = '#267208';
EDR.EDRMapV2.PolygonOptions.prototype.validPolygonLineWeight = 3;
EDR.EDRMapV2.PolygonOptions.prototype.validPolygonLineOpacity = 0.8;

// invalid polygon options
EDR.EDRMapV2.PolygonOptions.prototype.inValidPolygonFill = '#EA5F5F';
EDR.EDRMapV2.PolygonOptions.prototype.inValidPolygonOpacity = 0.35;

EDR.EDRMapV2.PolygonOptions.prototype.inValidPolygonLineColor = '#ED0C0C';
EDR.EDRMapV2.PolygonOptions.prototype.inValidPolygonLineWeight = 3;
EDR.EDRMapV2.PolygonOptions.prototype.inValidPolygonLineOpacity = 0.8;

// when overriden, returns the marker image object for valid polygon which is also
// used as default icon (specific to the engine)
EDR.EDRMapV2.PolygonOptions.prototype.createValidMarkerImage = function () { return null };

// when overriden, returns the marker image object for invalid polygon (specific to the engine)
EDR.EDRMapV2.PolygonOptions.prototype.createInValidMarkerImage = function () { return null };

// when overriden, returns the polygon options for valid polygon which is also
// used as default options (specific to the engine)
EDR.EDRMapV2.PolygonOptions.prototype.createValidPolygonOptions = function () { return null };

// when overriden, returns the polygon options for invvalid polygon (specific to the engine)
EDR.EDRMapV2.PolygonOptions.prototype.createInValidPolygonOptions = function () { return null };
/**************************************************************************
END: EDR.EDRMapV2.PolygonOptions
**************************************************************************/

/**************************************************************************
START: EDR.EDRMapV2.PolygonPoint

Base class for polygon point. Note that there are few methods
that are required to be overridden due to specific implementation of
mapping engine.

Derived class should set the validMarkerImage and inValidMarker image in
the constructor so that only 1 instance of each image types are created. 
Of course this is optional depending on implementation.
**************************************************************************/
EDR.EDRMapV2.PolygonPoint = function (map, latlng, polyOpts)
{
	if (this instanceof EDR.EDRMapV2.PolygonPoint)
	{
		// save map and create marker
		this.mapObject = map;

		// options
		if ((typeof (polyOpts) != 'undefined') && (polyOpts != null))
		{
			// use the passed in options object
			this.polygonOptions = polyOpts;
		}
	}
	else
		return new EDR.EDRMapV2.PolygonPoint(map);
};

// constructor
EDR.EDRMapV2.PolygonPoint.prototype.constructor = EDR.EDRMapV2.PolygonPoint;
EDR.EDRMapV2.PolygonPoint.prototype.base = null; // base should be set by the derived class

// properties
EDR.EDRMapV2.PolygonPoint.prototype.mapObject = null;
EDR.EDRMapV2.PolygonPoint.prototype.marker = null; 		// marker should be set by the derived class
EDR.EDRMapV2.PolygonPoint.prototype.validMarkerImage = null;
EDR.EDRMapV2.PolygonPoint.prototype.inValidMarkerImage = null;

// default options - intended for derived class to set to correct options object
EDR.EDRMapV2.PolygonPoint.prototype.polygonOptions = new EDR.EDRMapV2.PolygonOptions(null);

// internal vars - not to be used from external class - mean
EDR.EDRMapV2.PolygonPoint.prototype.eventObjects = { markerDragEvent: null, markerDragStartEvent: null, leftClickEvent: null, rightClickEvent: null };

// link list properties (pointers to next and previous point)
EDR.EDRMapV2.PolygonPoint.prototype.next = null;
EDR.EDRMapV2.PolygonPoint.prototype.prev = null;

// events
EDR.EDRMapV2.PolygonPoint.prototype.onPolygonPointDragStart = function (polyPt) { return false; };
EDR.EDRMapV2.PolygonPoint.prototype.onPolygonPointDragEnd = function (polyPt) { return false; };
EDR.EDRMapV2.PolygonPoint.prototype.onPolygonPointMoved = function (polyPt) { return false; };
EDR.EDRMapV2.PolygonPoint.prototype.onPolygonPointClicked = function (polyPt, isLeftClick) { return false; };

// when overridden, setup polygon point for editing process.
EDR.EDRMapV2.PolygonPoint.prototype.polygonEditStart = function () { return false; };

// when overridden, setup polygon point to stop editing process.
EDR.EDRMapV2.PolygonPoint.prototype.polygonEditStop = function () { return false; };

// when overridden (optional), can be used by polygonEditStart() as event handler
// for marker dragstart event
EDR.EDRMapV2.PolygonPoint.prototype.onMarkerDragStart = function (mouseEvt) { return false; };

// when overridden (optional), can be used by polygonEditStart() as event handler
// for marker dragend event
EDR.EDRMapV2.PolygonPoint.prototype.onMarkerDragged = function (mouseEvt) { return false; };

// when overridden (optional), can be used by polygonEditStart() as event handler
// for marker left-clicked event
EDR.EDRMapV2.PolygonPoint.prototype.onMarkerLeftClicked = function (mouseEvt) { return false; };

// when overridden (optional), can be used by polygonEditStart() as event handler
// for marker right-clicked event
EDR.EDRMapV2.PolygonPoint.prototype.onMarkerRightClicked = function (mouseEvt) { return false; };

// when overriden, clears the current instance
EDR.EDRMapV2.PolygonPoint.prototype.clearPoint = function ()
{
	this.mapObject = null;
	this.marker = null;
	this.validMarkerImage = null;
	this.inValidMarkerImage = null;
};

// methods
EDR.EDRMapV2.PolygonPoint.prototype.getIndex = function ()
{
	if (this.prev != null)
		return this.prev.getIndex() + 1;
	else
		return 0;
};
/**************************************************************************
END: EDR.EDRMapV2.PolygonPoint
**************************************************************************/

/**************************************************************************
START: EDR.EDRMapV2.StateDefaultMappingOptions

Default coordinates and zoom levels for states.

Note that loadFromXML() takes jQuery xmlNode object.
**************************************************************************/
EDR.EDRMapV2.StateDefaultMappingOptions = function () 
{
    /// <summary>Creates new instance of EDR.EDRMapV2.StateDefaultMappingOptions object.</summary>
    if (this instanceof EDR.EDRMapV2.StateDefaultMappingOptions) 
    {
    	// inheritance via constructor stealing
    	EDR.ObjectBase.apply(this, arguments);
    	this.base = EDR.ObjectBase.prototype;
    }
    else 
    {
        return new EDR.EDRMapV2.StateDefaultMappingOptions();
    }
};
// inheritance
EDR.EDRMapV2.StateDefaultMappingOptions.prototype = new EDR.ObjectBase();
EDR.EDRMapV2.StateDefaultMappingOptions.prototype.constructor = EDR.EDRMapV2.StateDefaultMappingOptions;

// properties
EDR.EDRMapV2.StateDefaultMappingOptions.prototype.state = '';
EDR.EDRMapV2.StateDefaultMappingOptions.prototype.stateName = '';
EDR.EDRMapV2.StateDefaultMappingOptions.prototype.centerLatitude = 0.0;
EDR.EDRMapV2.StateDefaultMappingOptions.prototype.centerLongitude = 0.0;
EDR.EDRMapV2.StateDefaultMappingOptions.prototype.zoomLevel = 0;

//functions
//Parses xml node and populates properties. (xmlnode is jQuery xmlnode)
EDR.EDRMapV2.StateDefaultMappingOptions.prototype.loadFromXML = function (xmlNode) {
    if (xmlNode) {
        this.state = EDR.Trim(xmlNode.attr("State")).toUpperCase();
        this.stateName = EDR.Trim(xmlNode.attr("StateName"));
        var lat = EDR.Trim(xmlNode.attr("CenterLatitude"));
        if (lat == "") lat = "0.0";
        this.centerLatitude = parseFloat(lat);
        var lng = EDR.Trim(xmlNode.attr("CenterLongitude"));
        if (lng == "") lng = "0.0";
        this.centerLongitude = parseFloat(lng);
        var zoom = EDR.Trim(xmlNode.attr("ZoomLevel"));
        if (zoom == "") zoom = "0";
        this.zoomLevel = parseInt(zoom);
    }
};
/**************************************************************************
END: EDR.EDRMapV2.StateDefaultMappingOptions
**************************************************************************/

/****************************************************************
START: EDR.EDRMapV2.Utilities

Static generic (not specific to map API) utility functions/methods.
*****************************************************************/
EDR.EDRMapV2.Utilities = 
{
	// returns array of EDR.EDRMapV2.StateDefaultMappingOptions
	// keyed to the 2digits state abbreviation
	getStatesDefaultMappingOptions: function (xmlURL)
	{
		var retVal = new Array();
		
		try
		{
			// get xmlDoc
			var xmlDoc = EDR.XML.XMLDocumentFromHTTPGet(xmlURL);
			if (xmlDoc == null) return retVal;
			
			var data = null;
			var tmpArray = new Array();
			
			// use jQuery
			$(xmlDoc).find("state").each(
				function (i, stateNode)
				{
					try
					{
						// exit if node does not exist
						if (stateNode == null) return;
						
						data = new EDR.EDRMapV2.StateDefaultMappingOptions();
						data.loadFromXML($(stateNode));
						
						// only add if 2 digits abbreviation is there
						if (data.state != '') tmpArray[data.state] = data;
					}
					catch (err)
					{
						//alert(err.message);
					}
				}
			);
			
			// return data
			retVal = tmpArray;
		}
		catch(err)
		{
			alert('Unable to get states default mapping options: ' + err.message);
		}
		
		return retVal;
	}
};

/****************************************************************
END: EDR.EDRMapV2.Utilities
*****************************************************************/

/****************************************************************
START: EDR.EDRMapV2.PolygonUtilities

Static generic (not specific to map API) utility functions/methods 
for polygon.
*****************************************************************/
EDR.EDRMapV2.PolygonUtilities =
{
	// returns intersecting coordinates between line 1 (l1) and line 2 (l2)
	// limited for the 2 line segments as JSON ({x, y}) otherwise null if does 
	// not intersect.
	// The algorithm and explanation can be found here:
	// http://www.topcoder.com/tc?module=Static&d1=tutorials&d2=geometry2
	getIntersectingCoordinates: function (l1c1, l1c2, l2c1, l2c2, validateLineSegment)
	{
		//before even calculating the poi, check if the 2 lines are joint
		if (EDR.EDRMapV2.PolygonUtilities.areCoordinatesEqual(l1c1, l2c1) || EDR.EDRMapV2.PolygonUtilities.areCoordinatesEqual(l1c1, l2c2) || EDR.EDRMapV2.PolygonUtilities.areCoordinatesEqual(l1c2, l2c1) || EDR.EDRMapV2.PolygonUtilities.areCoordinatesEqual(l1c2, l2c1))
		{
			//because the 2 line segments are joint, the line segments do not intersect inside
			return null;
		}
		
		//calucate values for first line
		var a1 = l1c2.y - l1c1.y;
		var b1 = l1c1.x - l1c2.x;
		var c1 = (a1 * l1c1.x) + (b1 * l1c1.y);

		//calculate values for second line
		var a2 = l2c2.y - l2c1.y;
		var b2 = l2c1.x - l2c2.x;
		var c2 = (a2 * l2c1.x) + (b2 * l2c1.y);

		//calculate the intersection point
		var x = NaN;
		var y = NaN;
		var det = (a1 * b2) - (a2 * b1);

		if (det == 0)
			return null;
		else
		{
			var x = ((b2 * c1) - (b1 * c2)) / det;
			var y = ((a1 * c2) - (a2 * c1)) / det;

			var poi = { x: x, y: y, distance: 0.0 };
			
			//set the default validate line segment flag value
			if ((typeof(validateLineSegment) == 'undefined') || (validateLineSegment == null))
			{
				validateLineSegment = true;
			}
			
			if (validateLineSegment == true)
			{
				// temp code to display marker on the Google Map v3 - MUST COMMENT IF NOT DEBUGGING
				/*
				var markLatLng = new google.maps.LatLng(y, x);
				var mark = new google.maps.Marker();
				mark.setPosition(markLatLng);
				mark.setIcon(EDR.WEBGEOCODER.polygonHandler.polygonOptions.inValidMarkerImage);
				mark.setMap(map);
				*/

				if((EDR.EDRMapV2.PolygonUtilities.getPOILineSegmentIntersectionPoint(l1c1, l1c2, poi) == null) || (EDR.EDRMapV2.PolygonUtilities.getPOILineSegmentIntersectionPoint(l2c1, l2c2, poi) == null))
				{
					return null;
				}
				else
				{
					return poi;
				}
			}
			else
			{
				return poi;
			}
		}
	},
	
	//checks if the poi actually lies on the line segment
	getPOILineSegmentIntersectionPoint: function(coord1, coord2, poi)
	{
		//******************************************************************************
		//[SUMMARY: calculate the line segment distance from each of the coordinates to the poi
		//and the length of line segment to figure out if the line intersects]
		
		//[IDEA: if the maximum length from one of the coordinates to poi is greater than 
		//the length of line segment, the 2 line segments don't intersect]
		//******************************************************************************
		
		//dist 1 - length from coord 1 to poi
		var dist1 = EDR.EDRMapV2.PolygonUtilities.getDistanceBetweenPoints(coord1, poi);
		//dist 2 - length from coord 2 to poi
		var dist2 = EDR.EDRMapV2.PolygonUtilities.getDistanceBetweenPoints(coord2, poi);
		//line length - length from coord 1 to coord 2
		var lineLength = EDR.EDRMapV2.PolygonUtilities.getDistanceBetweenPoints(coord1, coord2);
		
		var maxDist = (Math.max(dist1, dist2));
		if (maxDist > lineLength)
		{
			//current line segment doesn't intersect with poi
			return null;
		}
		else
		{
			//line segment intersects, return the poi
			poi.distance = maxDist;
			return poi;
		}
	},

	/*
	Name:	EDR.EDRMapV2Google.areIntersectingCoordinates
	Desc:	Checks if 2 line segments intersect each other
	Params:	JSON coordinate values
	l1c1: line 1 coord 1
	l1c2: line 1 coord 2
	l2c1: line 2 coord 1
	l2c2: line 2 coord 2
	Output:	true if coordinates intersect and are inside the POI, else false.
	*/
	areIntersectingCoordinates: function (l1c1, l1c2, l2c1, l2c2)
	{
		// get intersecting coordinates
		var intersectPt = EDR.EDRMapV2.PolygonUtilities.getIntersectingCoordinates(l1c1, l1c2, l2c1, l2c2);
		if (intersectPt != null)
			return true;
		else
			return false;
	},

	/*
	Name:	EDR.EDRMapV2Google.areCoordinatesEqual
	Desc: Checks if the 2 coordinate are same
	Params: JSON coordinate values
	Output: true if coordinates are the same
	*/
	areCoordinatesEqual: function (coord1, coord2)
	{
		if ((coord1.x == coord2.x) && (coord1.y == coord2.y))
		{
			return true;
		}
		else
		{
			return false;
		}
	},
	
	//returns the distance between 2 coordinates
	getDistanceBetweenPoints: function (coord1, coord2)
	{
		//distance formula sqrt((x2 - x1)^2 + (y2 - y1)^2)
		var dist = Math.sqrt(Math.pow((coord2.x - coord1.x), 2) + Math.pow((coord2.y - coord1.y), 2));
		return dist;
	},
	
	getSphericalDistanceBetweenPoints: function(coord1, coord2, unitOfMeasurement) {
		///<summary> Returns the distance between points </summary>
		///<param name="coord1"> LatLng coordinate </param>
		///<param name="coord2"> LatLng coordinate </param>
		///<param name="unitOfMeasurement"> (Optional) UnitOfDistanceMeasurementEnum.  By default, it is set to Meters. </param>
		
		var distanceInMeters = google.maps.geometry.spherical.computeDistanceBetween(coord1, coord2);
		
		if ((typeof(unitOfMeasurement) == 'undefined') || (unitOfMeasurement == null)) { unitOfMeasurement = this.UnitOfDistanceMeasurementEnum.METERS; }
		
		var distance = distanceInMeters;
		switch (unitOfMeasurement) {
			case this.UnitOfDistanceMeasurementEnum.METERS:
				distance = distanceInMeters;
				break;
			case this.UnitOfDistanceMeasurementEnum.KILOMETERS:
				distance = (distanceInMeters / 1000);
				break;
			case this.UnitOfDistanceMeasurementEnum.MILES:
				distance = (distanceInMeters / 1609.34);
				break;
		}
		
		return distance.toFixed(3);
	},

	// Enumerations
	UnitOfAreaMeasurementEnum: {
		SQUAREMILES: 1,
		ACRES: 2,
		SQUAREMETERS: 3,
		SQUAREKILOMETERS: 4
	},

	UnitOfPerimeterMeasurementEnum: {
		MILES: 1,
		METERS: 2,
		KILOMETERS: 3
	},
	
	UnitOfDistanceMeasurementEnum: {
		MILES: 1,
		METERS: 2,
		KILOMETERS: 3
	},

	/*
	Name:	EDR.EDRMapV2.PolygonUtilities.convertPolygonAreaFromSquareFeet()
	Desc:	Function to convert polygon area from square feet to any one of these units of measurement: SQUAREMILES, ACRES, SQUAREMETERS or SQUAREKILOMETERS.
	Output: The polygon area real number value in the specified unit of measurement.
	*/
	convertPolygonAreaFromSquareFeet: function (area, unitOfMeasurement)
	{
		var returnArea = area;

		switch (unitOfMeasurement)
		{
			case EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREMILES:
				returnArea = (area / 27878400).toFixed(2);
				break;
			case EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.ACRES:
				returnArea = (area / 43560).toFixed(2);
				break;
			case EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREMETERS:
				returnArea = (area * 0.09290304).toFixed(2);
				break;
			case EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREKILOMETERS:
				returnArea = (area * 0.00000009290304).toFixed(2);
				break;
				
			default:
				if (returnArea > 0.0) returnArea = (1.0 * returnArea).toFixed(2);
		}

		return returnArea;
	},

	/*
	Name:	EDR.EDRMapV2.PolygonUtilities.convertPolygonPerimeterFromFeet()
	Desc:	Function to convert polygon perimeter from feet to any one of these units of measurement: MILES, METERS or KILOMETERS.
	Output: The polygon perimeter real number value in the specified unit of measurement.
	*/
	convertPolygonPerimeterFromFeet: function (perimeter, unitOfMeasurement)
	{
		var returnPerimeter = perimeter;

		switch (unitOfMeasurement)
		{
			case EDR.EDRMapV2.PolygonUtilities.UnitOfPerimeterMeasurementEnum.MILES:
				returnPerimeter = (perimeter * 0.000189393939).toFixed(3);
				break;
			case EDR.EDRMapV2.PolygonUtilities.UnitOfPerimeterMeasurementEnum.METERS:
				returnPerimeter = (perimeter * 0.3048).toFixed(3);
				break;
			case EDR.EDRMapV2.PolygonUtilities.UnitOfPerimeterMeasurementEnum.KILOMETERS:
				returnPerimeter = (perimeter * 0.0003048).toFixed(3);
				break;
		}

		return returnPerimeter;
	}
};
/****************************************************************
END: EDR.EDRMapV2.PolygonUtilities
*****************************************************************/
