/// <reference path="http://localhost/global/jscripts/edrlibrary.js" />

EDR.WEBGEOCODER = {};

EDR.WEBGEOCODER =
{
    // GetResources handler URL
    handlerURL: '/ordering/webgeocoderv3/getresources.ashx',

    // Latitude/longitude control information
    latitudeLongitudeControl: { LatitudeHiddenID: '', LongitudeHiddenID: '' },

    // webGeocoderActionTypes enumeration values
    webGeocoderActionTypes: { WEBGEOV3_PolygonSaved: 73, WEBGEOV3_PolygonMerged: 74, WEBGEOV3_ParcelApi: 75, WEBGEOV3_ParcelDetailApi: 76, WEBGEOV3_MapTypeChanged: 77, WEBGEOV3_MapZoomChanged: 78, WEBGEOV3_ToggleTaxMap: 79, WEBGEOV3_MultiParcelChanged: 80, WEBGEOV3_UIException: 81, WEBGEOV3_TPParcelRemoved: 82, WEBGEOV3_SelectGeocodedParcel: 83, WEBGEOV3_PageLoaded: 84, WEBGEOV3_DrawPolygon: 85, WEBGEOV3_ParcelClicked: 86, WEBGEOV3_ContinueClicked: 87, WEBGEOV3_LoadPolygonFromAPI: 88 },

    // Customer Account Number
    customerAccountNumber: '',

    // Enable/Disable Matomo Event Tracking
    matomoEventTrackingEnable: false,

    // WebGeocoderSession GUID
    webGeocoderSessionGUID: '',

    // WebGeocoder source property GUID
    sourcePropertyGUID: '',

    // maximum polygon area in sq feet
    maxPolygonArea: 0,

    // maximum polygon perimeter in feet
    maxPolygonPerimeter: 0,

    //distance to buffer the polygon before merging
    bufferPolygonByDistance: 0,

    //Tolerance distance for simplifying a merged polygon to reduce number of coordinates
    simplifyPolygonToleranceDistance: 0,

    // radius for polygon extent (box that restrict where polygon must be drawn in)
    polygonExtentRadius: 0,

    // max distance between polygon vertexes
    polygonMaxVertexDistance: 7920,

    // polygon handler object
    polygonHandler: null,

    parcelPolygonHandler: null,

    // temp debugging property
    urlHost: '',

    // maximum distance the TP is allowed to move
    maxTPMoveDistanceInFeet: 0,

    // original latitude
    originalSourcePropertyLatitude: 0,

    // original longitude
    originalSourcePropertyLongitude: 0,

    // URL to get the state default mapping options 
    stateDefaultMappingOptionsURL: '',

    // states default mapping options
    stateDefaultMappingOptions: null,

    //store the dissolved (merged)geomtry to this vairable
    tempMergedGeometry: null,

    // flag to allow polygon modification
    autoEditPolygon: true,

    //Name of Parcel map overlay
    parcelOverlayMapName: 'DMP_WMS_Layer',

    parcelAddressIDSeperator: '##',

    parcelPolygonModified: false,

    enumParcelDetailLevel: { BASIC: 1, SHAPETEXT: 2, SHAPELENGTH: 4, SHAPEAREA: 8, SHAPEMAXDISTANCE: 16 },

    autoSelectTaxMapOverlay: true,

    mergedParcelArray: new Array(),

    parcelChangeModal: {
        title: 'Selecting New Boundary',
        content: '<p>You have selected to use a different property boundary. Any edits to the current property boundary will be lost.</p>'
    },

    parcelRemoveModal: {
        title: 'Removing Property Boundary',
        content: '<p>You have chosen to remove the property boundary. Any edits you have made to the boundary will be lost.</p>'
    },

    log: function (message) {
        ///<summary> Handles logging the given message </summary>
        try {
            console.log('[EDR.WEBGEOCODER] ' + message);
        }
        catch (e) {
            // do nothing for now
        }
    },

    logError: function (message) {
        ///<summary> Handles logging the given message </summary>
        try {
            console.log('[EDR.WEBGEOCODER] UI Exception ' + message);
            //add to tracking log
            EDR.WEBGEOCODER.saveTrackingInformation(new Date(), EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_UIException, '[EDR.WEBGEOCODER] UI Exception ' + message);
        }
        catch (e) {
            // do nothing for now
        }
    },

    dmpMapLayers: null,

    parcelsInComplex: null, //To store the parcels ina multiple/overlapping parcel

    /*Mapping related functions*/
    initializeMap: function (mapDiv, tpInfo, mapOpts) {
        var startTime = new Date();
        EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_PageLoaded, 'WebGeocoderV3 UI is loaded or refreshed');
        // create TP marker
        var tp = null;
        if (tpInfo != null) tp = new EDR.EDRMapV2.Marker(tpInfo);

        // use default map options
        var options = new EDR.EDRMapV2.MapOptions(mapOpts);

        // check if tax map option is available
        if (typeof (EDR.WEBGEOCODER.showTaxMapControl) != 'boolean') { EDR.WEBGEOCODER.showTaxMapControl = false; }

        if (EDR.WEBGEOCODER.showTaxMapControl) {
            // create the overlay options
            var overlayMapOptions = new Array();

            // build the different wms layers for the different map types
            EDR.WEBGEOCODER.dmpMapLayers = [
                { mapType: 'roadmap', wmsURL: EDR.WEBGEOCODER.dmpRoadmapMapWMSLayerURL },
                { mapType: 'Simple Map', wmsURL: EDR.WEBGEOCODER.dmpSimpleMapWMSLayerURL },
                { mapType: 'hybrid', wmsURL: EDR.WEBGEOCODER.dmpSatelliteMapWMSLayerURL }, //satellite - aerial with label is disabled.
                { mapType: 'satellite', wmsURL: EDR.WEBGEOCODER.dmpSatelliteMapWMSLayerURL } //satellite - aerial with label is disabled.
            ];

            // insert tax map overation options
            var taxMapOverlayOptions = { name: 'Tax Map', typeID: EDR.WEBGEOCODER.parcelOverlayMapName, url: EDR.WEBGEOCODER.dmpSimpleMapWMSLayerURL, opacity: 1, index: 1 };
            overlayMapOptions.push(taxMapOverlayOptions);

            options.OverlayMapTypeOptions = overlayMapOptions;

            // setup the map events
            var mapEvents = new Array();
            mapEvents.push({ action: 'tilesloaded', callback: EDR.WEBGEOCODER.onMapLoaded });
            mapEvents.push({ action: 'click', callback: EDR.WEBGEOCODER.onMapClick });
            mapEvents.push({ action: 'zoom_changed', callback: EDR.WEBGEOCODER.onMapZoomChanged });
            mapEvents.push({ action: 'maptypeid_changed', callback: EDR.WEBGEOCODER.onMapTypeChanged });

            options.MapEventHandlers = mapEvents;
        }

        EDRV2.EventCollector.addHandler(EDR.EDRMapV2Google.EnumMapOverlayEvents.MAPOVERLAYENABLED, EDR.WEBGEOCODER.onMapOverlayEnabled);
        EDRV2.EventCollector.addHandler(EDR.EDRMapV2Google.EnumMapOverlayEvents.MAPOVERLAYDISABLED, EDR.WEBGEOCODER.onMapOverlayDisabled);
        //EDRV2.EventCollector.addHandler(EDR.EDRMapV2Google.EnumMapOverlayEvents.OVERLAYOPTIONADDED, EDR.WEBGEOCODER.onOverlayOptionAdded);

        // initialize google mapo
        EDR.EDRMapV2Google('WEBGEOCODERV3', mapDiv, tp, options, null, null);

        // initialize polygon handler (workaround for now till we convert EDRMapV2Google to EDRMapV2GoogleV3 class)
        // note that calling the function above sets bunch of global variables - one of them is map and tpMarker
        EDR.WEBGEOCODER.polygonHandler = new EDR.EDRMapV2GoogleV3.PolygonHandler(map, tpMarker);
        EDR.WEBGEOCODER.polygonHandler.onPolygonUpdated = EDR.WEBGEOCODER.onPolygonUpdated;
        EDR.WEBGEOCODER.polygonHandler.onPolygonClicked = EDR.WEBGEOCODER.onPolygonClicked;
        EDR.WEBGEOCODER.polygonHandler.polygonOptions.polygonExtentRadius = EDR.WEBGEOCODER.polygonExtentRadius;
        EDR.WEBGEOCODER.polygonHandler.polygonOptions.autoEditPolygon = EDR.WEBGEOCODER.autoEditPolygon;

        // get states default mapping options
        if (EDR.WEBGEOCODER.stateDefaultMappingOptionsURL != '') {
            EDR.WEBGEOCODER.stateDefaultMappingOptions = EDR.EDRMapV2.Utilities.getStatesDefaultMappingOptions(EDR.WEBGEOCODER.stateDefaultMappingOptionsURL);
        }
    },

    /***************************************************************************************
    START: Google Map Specific Handlers
    ***************************************************************************************/
    /*
    onTPMarkerMoved()
 
    Event handler when TP is moved by user.
    tpMarker: maps.google.Marker object.
 
    Since this function can be called by internal function, there are cases where
    error information needs to be displayed (errHeader, errMsg)
    */
    onTPMarkerMoved: function (tpMarker, reZoomTPToCenter, errHeader, errMsg) {
        //Clear any previous errors
        EDR.WEBGEOCODER.clearErrorMessages()

        //var startTime = new Date();

        // validate
        if (tpMarker == null) {
            EDR.WEBGEOCODER.setErrorMessages("Invalid operation", "Invalid TP marker object");
            //alert('Unable to move property marker because the marker object is invalid.');
            return false;
        }

        //Check for max move distance compliance
        if (EDR.WEBGEOCODER.isTPWithinMaxMoveDistance(EDR.EDRMapV2Google.GetTPMarker().getPosition()) == false) { return false; } //Exit immediately

        // set polygon handler w/ new marker
        EDR.WEBGEOCODER.polygonHandler.tpMarker = tpMarker;

        // get lat/lon
        var latLng = tpMarker.getPosition();

        // set the UI lat/lon
        var coorCtrlInfo = { LatitudeHiddenID: EDR.WEBGEOCODER.latitudeLongitudeControl.LatitudeHiddenID, LongitudeHiddenID: EDR.WEBGEOCODER.latitudeLongitudeControl.LongitudeHiddenID, Latitude: latLng.lat(), Longitude: latLng.lng() };
        EDR.CONTROLS.LATITUDELONGITUDE.SetCoordinates(coorCtrlInfo);

        if ((typeof (reZoomTPToCenter) == 'undefined') || (reZoomTPToCenter == null)) reZoomTPToCenter = false;
        if ((typeof (errHeader) == 'undefined') || (errHeader == null)) errHeader = '';
        if ((typeof (errMsg) == 'undefined') || (errMsg == null)) errMsg = '';

        if ((errHeader != '') || (errMsg != ''))
            __pleaseWait.show(null, EDR.WEBGEOCODERPAGE.pleaseWaitPosition(), function () { EDR.WEBGEOCODER.executeReverseGeocode(reZoomTPToCenter, true, false); EDR.WEBGEOCODER.setErrorMessages(errHeader, errMsg); });
        else
            __pleaseWait.show(null, EDR.WEBGEOCODERPAGE.pleaseWaitPosition(), function () { EDR.WEBGEOCODER.executeReverseGeocode(reZoomTPToCenter, true, false); });

        //EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_TPMarkerMoved, 'TP Marker is moved to Latitude: ' + latLng.lat() + ' and Longitude : ' + latLng.lng());
    },

    onMapLoaded: function (evtData, map) {
        /// <summary> Event handler for map click </summary>
        try {
            EDR.WEBGEOCODER.log('map loaded');

            // check if the tax map option needs to be applied
            if ((EDR.WEBGEOCODER.showTaxMapControl) && (EDR.WEBGEOCODER.autoSelectTaxMapOverlay)) {
                EDR.EDRMapV2Google.triggerMapOverlayOption(EDR.WEBGEOCODER.parcelOverlayMapName, true);

                // since we don't want to trigger the auto select parcel overlay, set the flag to false
                EDR.WEBGEOCODER.autoSelectTaxMapOverlay = false;
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('onMapLoad(): ' + e.message);
        }
    },

    onMapClickTimeDelegate: null,

    mapClickCoordinate: null,

    onMapClick: function (evtData, map) {
        /// <summary> Event handler for map click </summary>
        try {
            EDR.WEBGEOCODER.log('map click triggered');

            // check if the PARCEL data needs to be displayed
            if (EDR.EDRMapV2Google.hasOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName)) {
                // check if the current zoom level
                if (map.zoom < EDR.WEBGEOCODER.minParcelZoomLevel) { return; }
                // get the center of map
                var centerLatLng = evtData.latLng;

                var data = { extentInMeteres: 1, latitude: centerLatLng.lat(), longitude: centerLatLng.lng(), detailLevel: 15 };

                // check if the time delegate exists
                if (EDR.WEBGEOCODER.onMapClickTimeDelegate != null) {
                    EDR.WEBGEOCODER.log('Clearing mapClickEventDelegateID: ' + EDR.WEBGEOCODER.onMapClickTimeDelegate);
                    clearTimeout(EDR.WEBGEOCODER.onMapClickTimeDelegate);
                }

                // start a new timer to get the parcel details
                EDR.WEBGEOCODER.onMapClickTimeDelegate = setTimeout(function () {
                    EDR.WEBGEOCODER.log('Executing mapClickEventDelegateID: ' + EDR.WEBGEOCODER.onMapClickTimeDelegate);
                    // get the parcel details
                    EDR.WEBGEOCODER.getParcelByCoordinate(data);

                    // reset the time delegate
                    EDR.WEBGEOCODER.onMapClickTimeDelegate = null;
                }, 300);

                var startTime = new Date();
                EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_ParcelClicked, 'WebGeocoderV3 UI user clicked on the map');

                EDR.WEBGEOCODER.log('Initiated mapClickEventDelegateID: ' + EDR.WEBGEOCODER.onMapClickTimeDelegate);
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('onMapClick(): ' + e.message);
        }
    },

    onMapZoomChanged: function (evtData, map) {
        /// <summary> Event handler for map zoom level changed</summary>
        try {
            var startTime = new Date();
            EDR.WEBGEOCODER.log('map zoom changed event triggered');

            // show/hide if the PARCEL data needs to be displayed
            EDR.WEBGEOCODER.showHideParcelOverlayMap(map);

            EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_MapZoomChanged, 'Map Zoom Changed');
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('onMapZoomChanged(): ' + e.message);
        }
    },

    showHideParcelOverlayMap: function (map) {
        try {
            // check if the PARCEL data needs to be displayed
            if (EDR.EDRMapV2Google.hasOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName)) {
                // get the map layer
                var parcelLayer = EDR.EDRMapV2Google.getOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName);
                if (parcelLayer == null) { throw new Error('Unable to find the parcel overlay map layer'); }
                // check if the current zoom level is lower than the minimum parcel zoom level
                if (map.zoom < EDR.WEBGEOCODER.minParcelZoomLevel) {
                    // hide the layer
                    parcelLayer.setOpacity(0);

                    // disable the map overlay option
                    $('.mapOverlayOption input').attr('disabled', true);
                }
                else {
                    // show the layer
                    parcelLayer.setOpacity(1);

                    // enable the map overlay option
                    $('.mapOverlayOption input').attr('disabled', false);
                }
            }
            else {
                // the wms layer isn't enabled, do nothing
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('showHideParcelOverlayMap(): ' + e.message);
        }
    },

    onMapTypeChanged: function (evtData, map) {
        /// <summary> Event handler for map type changed</summary>
        try {
            var startTime = new Date();
            var mapType = map.getMapTypeId();
            EDR.WEBGEOCODER.log('map type changed: ' + mapType);

            // check if the PARCEL data needs to be displayed
            if ((EDR.EDRMapV2Google.hasOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName)) && (EDR.WEBGEOCODER.dmpMapLayers != null)) {
                // update the wms layer to the correct map type
                var layers = EDR.WEBGEOCODER.dmpMapLayers
                for (var i = 0; i < layers.length; i++) {
                    if (layers[i].mapType === mapType) {
                        EDR.WEBGEOCODER.removeOverlayMapType();
                        EDR.WEBGEOCODER.setOverlayMapType(layers[i].wmsURL, 1);
                        //EDR.WEBGEOCODER.parcelOverlayMapName.refresh();
                        EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_MapTypeChanged, 'Map Type Changed to ' + mapType);
                        return;
                    }
                }
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('onMapTypeChanged(): ' + e.message);
        }
    },

    setOverlayMapType: function (url, opacity) {
        try {
            EDR.EDRMapV2Google.setOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName, url, opacity);
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('setOverlayMapType(): ' + e.message);
        }
    },

    removeOverlayMapType: function () {
        try {
            EDR.EDRMapV2Google.removeOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName);
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('removeOverlayMapType(): ' + e.message);
        }
    },

    onTaxMapChecked: function (map) {
        /// <summary> Event handler for Tax Map checkbox enabled</summary>
        try {
            var mapType = map.getMapTypeId();
            EDR.WEBGEOCODER.log('tax map checked: ' + mapType);

            // check if the PARCEL data needs to be displayed
            if (EDR.WEBGEOCODER.dmpMapLayers != null) {
                // update the wms layer to the correct map type
                var layers = EDR.WEBGEOCODER.dmpMapLayers
                for (var i = 0; i < layers.length; i++) {
                    if (layers[i].mapType === mapType) {
                        EDR.WEBGEOCODER.setOverlayMapType(layers[i].wmsURL, 1);
                        //EDR.WEBGEOCODER.parcelOverlayMapName.refresh();                       
                        return;
                    }
                }
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('onTaxMapChecked(): ' + e.message);
        }
    },

    onMapOverlayEnabled: function (data) {
        /// <summary> Event handler for when map overlay is enabled </summary>
        try {
            var startTime = new Date();
            EDR.WEBGEOCODER.log('map overlay enabled: ' + data.layer);

            // set the correct layer type
            EDR.WEBGEOCODER.onTaxMapChecked(data.map);

            // show/hide if the PARCEL data needs to be displayed
            EDR.WEBGEOCODER.showHideParcelOverlayMap(data.map);
            EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_ToggleTaxMap, 'ParcelOverlay Map Enabled');

            $('.mapOverlayOption').css('font-weight', 'bold');
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('onMapLoad(): ' + e.message);
        }
    },

    onMapOverlayDisabled: function (data) {
        /// <summary> Event handler for when map overlay is enabled </summary>
        try {
            var startTime = new Date();
            EDR.WEBGEOCODER.log('map overlay disabled: ' + data.layer);

            EDR.WEBGEOCODER.removeOverlayMapType();

            // remove any selectd parcel property boundary
            if (EDR.WEBGEOCODER.parcelPolygonHandler != null) { EDR.WEBGEOCODER.parcelPolygonHandler.removePolygon(); }

            $('.mapOverlayOption').css('font-weight', 'normal');

            // close the parcel info window if open
            if (EDR.WEBGEOCODER.parcelInfoWindow != null) { EDR.WEBGEOCODER.parcelInfoWindow.remove(); }

            EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_ToggleTaxMap, 'ParcelOverlay Map Disabled');
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('onMapLoad(): ' + e.message);
        }
    },

    getMapExtentDistance: function () {
        // returns the map extent distance in meters

        try {
            // get the map bounds
            var bounds = map.getBounds();

            // map bounds coordinates
            var coord1 = bounds.getNorthEast();
            var coord2 = bounds.getSouthWest();

            // convert the coordinates to distance
            return EDR.EDRMapV2.PolygonUtilities.getSphericalDistanceBetweenPoints(coord1, coord2);
        }
        catch (e) {
            EDR.WEBGEOCODER.logError(e.message);
        }
    },

    parcelInfoWindow: null,

    mapParcels: null,

    //Changed 16 to 15
    minParcelZoomLevel: 15,

    tpParcel: null,

    //parcelByExtentDataRecieved: function (data) {
    //    ///<summary> Handles parcel by extent data </summary>
    //    try {
    //        // hide the please wait
    //        __pleaseWait.hide();

    //        EDR.WEBGEOCODER.log('parcelByExtent data recieved');

    //        // validate
    //        if ((typeof (data.parcels) == 'undefined') || (data.parcels == null) || (data.parcels.length === 0)) { throw new Error('No parcels found'); }

    //        // update the current parcels
    //        EDR.WEBGEOCODER.mapParcels = data.parcels;
    //    }
    //    catch (e) {
    //        EDR.WEBGEOCODER.logError('[ERROR] parcelByExtentDataRecieved: ' + e.message);
    //    }
    //},
            
    getParcelByCoordinate: function (data) {
        /// <summary> Get parcel by coordinates </summary>
        try {
            // valdiate
            if ((typeof (data) == 'undefined') || (data == null)) { throw new Error('Missing parameters to get parcel data by extent'); }

            // check if the page is in edit mode.  if so, exit out
            if (EDR.WEBGEOCODER.polygonHandler.isInEditMode) { return; }

            var startTime = new Date();

            // close the tax parcel info window just in case
            if (EDR.WEBGEOCODER.parcelInfoWindow != null) {
                EDR.WEBGEOCODER.parcelInfoWindow.remove();
            }

            var qryStrs = [];
            qryStrs.push({ key: 'latitude', value: data.latitude });
            qryStrs.push({ key: 'longitude', value: data.longitude });
            qryStrs.push({ key: 'distancemeters', value: data.extentInMeteres });
            qryStrs.push({ key: 'detailLevel', value: data.detailLevel });

            //var url = EDR.WEBGEOCODER.buildURL(EDR.WEBGEOCODER.getHost(true), '/edrservices/geospatial/api/dmp/20150323/parcels', qryStrs, true);
            var url = EDR.WEBGEOCODER.buildURL(EDR.WEBGEOCODER.parcelServiceURL, '', qryStrs, true);

            EDR.WEBGEOCODER.mapClickCoordinate = { latitude: data.latitude, longitude: data.longitude };

            //$.support.cors = true;
            $.ajax({
                url: url,
                dataType: 'json',
                headers: { 'Content-Type': 'application/json', 'Authorization': EDR.WEBGEOCODER.geoSpatialServiceAuthToken },
                success: function (data) {
                    EDR.WEBGEOCODER.parcelByCoordinateDataReceived(data);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    EDR.WEBGEOCODER.parcelByCoordinateDataReceived(null);
                }
            });
            EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_ParcelApi, 'Get Parcel by Coordinate');
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('getParcelByCoordinate(): ' + e.message);
        }
    },

    parcelByCoordinateDataReceived: function (data) {
        try {
            // validate
            if ((typeof (data) == 'undefined') || (data == null) || (typeof (data.parcels) == 'undefined') || (data.parcels == null) || (data.parcels.length === 0)) { throw new Error('No parcel data found.'); }

            var curParcel = null;
            var sortedParcels = null;
            //if multiple parcel available, sort it by area and take the smallest parcel
            if (data.parcels.length > 1) {
                sortedParcels = data.parcels;
                sortedParcels.sort(function (a, b) { return a.areaSquareMeters - b.areaSquareMeters });
                curParcel = sortedParcels[0];
                EDR.WEBGEOCODER.parcelsInComplex = sortedParcels;
            }
            else //only one parcel available
            {
                curParcel = data.parcels[0];
                EDR.WEBGEOCODER.parcelsInComplex = curParcel;
            }

            // check if the current parcel data exists
            if ((EDR.WEBGEOCODER.mapParcels == null) || (EDR.WEBGEOCODER.mapParcels.length == 0)) { EDR.WEBGEOCODER.mapParcels = new Array(); }
            if (EDR.WEBGEOCODER.getParcelByParcelID(curParcel.parcelID) == null) {
                EDR.WEBGEOCODER.mapParcels.push(curParcel);
            }

            // get the parcel parcels by apn
            EDR.WEBGEOCODER.getParcelDetailsByAPN(curParcel);
        }
        catch (e) {
            // do nothing
            EDR.WEBGEOCODER.logError('parcelByCoordinateDataReceived(): ' + e.message);
        }
    },

    // Gets Parcel Details by APN and FPPS*
    getParcelDetailsByAPN: function (data) {
        try {

            if ((typeof (data) == 'undefined') || (data == null)) { throw new Error('Unable to get parcel details because no data was passed'); }
            data.apn = EDRV2.trim(data.apn);
            data.fips = EDRV2.trim(data.fips);
            //if (data.apn === '') { throw new Error('Parcel APN is required.'); }
            //if (data.fips === '') { throw new Error('Parcel FIPS is required.'); }
            var thisData = data;

            var startTime = new Date();

            // close any existing parcel window, and highlight the selected property
            if (EDR.WEBGEOCODER.parcelInfoWindow != null) {

                EDR.WEBGEOCODER.log('removing the existing parcel info window');

                EDR.WEBGEOCODER.parcelInfoWindow.remove();
                EDR.WEBGEOCODER.parcelInfoWindow = null;
            }

            if ((typeof (data.shapeWKT) != 'undefined') && (data.shapeWKT != null)) {
                var polyCoords = EDR.WEBGEOCODER.parseParcelPolygonToCoordinates(data.shapeWKT);
                if ((polyCoords == null) || (polyCoords.length == 0)) { return; }

                // check if there are multiple polygons
                var parcelPolygonCoords = null;
                if (polyCoords.length > 1) {
                    var curPoly;
                    var curPolyCoords;

                    var mapLatLng = new google.maps.LatLng(EDR.WEBGEOCODER.mapClickCoordinate.latitude, EDR.WEBGEOCODER.mapClickCoordinate.longitude);

                    // there are multiple polygon coordinates.  figure out which polygon coordinates belong to.
                    for (var i = 0; i < polyCoords.length; i++) {
                        curPolyCoords = polyCoords[i];

                        // convert the current polygon coordinates to google polygon
                        var mapCoords = new Array();
                        for (var j = 0; j < curPolyCoords.length; j++) {
                            mapCoords.push(new google.maps.LatLng(curPolyCoords[j].latitude, curPolyCoords[j].longitude));
                        }
                        curPoly = new google.maps.Polygon({
                            paths: mapCoords
                        });

                        // check if the current map point is within the current polygon
                        if (google.maps.geometry.poly.containsLocation(mapLatLng, curPoly)) {
                            // update the original polygon coordinates to the selected polygon coordinates
                            parcelPolygonCoords = curPolyCoords;

                            // update the "centroid" lat/long
                            data.latitude = mapLatLng.lat();
                            data.longitude = mapLatLng.lng();

                            // update the area of the polygon
                            var polyData = EDR.EDRMapV2GoogleV3.PolygonUtilities.calculatePolygonPerimeterArea(curPoly);

                            // since the tax parcel lot area is in sq meters, convert the polygon area to the same unit
                            data.areaSquareMeters = EDR.EDRMapV2.PolygonUtilities.convertPolygonAreaFromSquareFeet(polyData.areaInSquareFeet, EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREMETERS);

                            // update the tax parcel
                            var parcelIndex = EDR.WEBGEOCODER.getParcelIndexByParcelID(data.parcelID);
                            if (parcelIndex < 0) {
                                EDR.WEBGEOCODER.mapParcels.push(data);
                            }
                            else {
                                EDR.WEBGEOCODER.mapParcels[parcelIndex] = data;
                            }
                            break;
                        }
                    }

                    // check if we found the coordinates
                    if (parcelPolygonCoords == null) { return; }
                }
                else {
                    parcelPolygonCoords = polyCoords[0];
                }

                var dvgCoords = EDR.WEBGEOCODER.parseCoordinatesToDVGCoordinates(parcelPolygonCoords);
                if ((dvgCoords == null) || (dvgCoords === '')) { return; }

                var polyHandler = EDR.WEBGEOCODER.parcelPolygonHandler;
                if (polyHandler == null) {
                    // create a new instance of the polygon
                    EDR.WEBGEOCODER.parcelPolygonHandler = new EDR.EDRMapV2GoogleV3.PolygonHandler(map, null);
                    EDR.WEBGEOCODER.parcelPolygonHandler.onPolygonClicked = EDR.WEBGEOCODER.onPolygonClicked;
                }

                polyHandler = EDR.WEBGEOCODER.parcelPolygonHandler;

                // update the coordinates
                polyHandler.setPolygonDVGCoordinates(dvgCoords);

                // update the styling of the polygon
                EDR.EDRMapV2GoogleV3.PolygonUtilities.changePolygonColors(polyHandler.polygon, polyHandler.getPolygonPoints(), polyHandler.polygonOptions.createTaxParcelPolygonOptions(), null);
            }

            if ((data.apn === '') || (data.fips === '')) {
                // since apn, and fips are required to get the parcel details, treat this as if the details don't exist
                EDR.WEBGEOCODER.parcelDetailsDataReceived({ parceDetails: null, contextData: thisData });
            }
            else {
                // send the request to get the full details
                // build the query
                var qryStrs = [];
                qryStrs.push({ key: 'apn', value: data.apn });
                qryStrs.push({ key: 'fips', value: data.fips });
                qryStrs.push({ key: 'stripapn', value: '1' });

                // get URL
                //var url = EDR.WEBGEOCODER.buildURL(EDR.WEBGEOCODER.getHost(true), '/edrservices/geospatial/api/dmp/20150323/parcelDetails', qryStrs, true);
                var url = EDR.WEBGEOCODER.buildURL(EDR.WEBGEOCODER.parcelDetailServiceURL, '', qryStrs, true);

                $.ajax({
                    url: url,
                    dataType: 'json',
                    headers: { 'Content-Type': 'application/json', 'Authorization': EDR.WEBGEOCODER.geoSpatialServiceAuthToken },
                    success: function (data) {
                        // tagging the coordinates here since the API does not return it
                        // look it up upstream ?
                        data.contextData = thisData;
                        //test: EDR.WEBGEOCODER.getParcelInfoWindowData( data.parcelDetails[0] );
                        EDR.WEBGEOCODER.parcelDetailsDataReceived(data);
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        EDR.WEBGEOCODER.parcelDetailsDataReceived(null);
                    }
                });
                EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_ParcelDetailApi, 'Get Parcel details by apn');
            }
        }
        catch (err) {
            EDR.WEBGEOCODER.logError('getParcelDetailsByAPN(): ' + err.message);
        }
    },

    getParcelIndexByAPN: function (apn) {
        /// returns the parcel index based on apn value
        try {
            // validate
            if ((typeof (apn) == 'undefined') || (apn == null)) { return -1; }
            if ((EDR.WEBGEOCODER.mapParcels == null) || (EDR.WEBGEOCODER.mapParcels.length == 0)) { return -1; }

            // loop through each parcel and match the parcel's apn number
            var taxParcels = EDR.WEBGEOCODER.mapParcels;
            for (var i = 0; i < taxParcels.length; i++) {
                if (EDRV2.trim(taxParcels[i].apn) === apn) { return i; }
            }

            return -1;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('getParcelByAPN(): ' + e.message);
        }
    },

    getParcelByAPN: function (apn) {
        /// returns the parcel based on apn value
        try {
            // validate
            var index = EDR.WEBGEOCODER.getParcelIndexByAPN(apn);
            if (index < 0) { return null; }

            return EDR.WEBGEOCODER.mapParcels[index];
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('getParcelByAPN(): ' + e.message);
        }
    },

    getParcelIndexByParcelID: function (parcelID) {
        /// returns the parcel index based on apn value
        try {
            // validate
            if ((typeof (parcelID) == 'undefined') || (parcelID == null)) { return -1; }
            if ((EDR.WEBGEOCODER.mapParcels == null) || (EDR.WEBGEOCODER.mapParcels.length == 0)) { return -1; }

            // loop through each parcel and match the parcel's apn number
            var taxParcels = EDR.WEBGEOCODER.mapParcels;
            for (var i = 0; i < taxParcels.length; i++) {
                if (taxParcels[i].parcelID === parcelID) { return i; }
            }

            return -1;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('getParcelIndexByParcelID(): ' + e.message);
        }
    },

    getParcelByParcelID: function (parcelID) {
        /// returns the parcel based on parcel ID value
        try {
            // validate
            var index = EDR.WEBGEOCODER.getParcelIndexByParcelID(parcelID);
            if (index < 0) { return null; }

            return EDR.WEBGEOCODER.mapParcels[index];
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('getParcelByParcelID(): ' + e.message);
        }
    },

    getParcelBySelectedParcelID: function (selectedParcelID) {
        /// returns the parcel based on parcel ID value
        try {
            // validate
            var index = -1;
            var parcelAddressID = -1;
            var parcelID = selectedParcelID;
            if ((EDR.WEBGEOCODER.parcelsInComplex == null) || (EDR.WEBGEOCODER.parcelsInComplex.length == 0)) { return null; }

            // loop through each parcel and match the parcel's parcelId
            var taxParcels = EDR.WEBGEOCODER.parcelsInComplex;
            //check whether parcelAddressId available
            if (selectedParcelID.indexOf(EDR.WEBGEOCODER.parcelAddressIDSeperator) > -1) {
                var parcelIDAddressID = selectedParcelID.split(EDR.WEBGEOCODER.parcelAddressIDSeperator);
                if (parcelIDAddressID.length > 1) {
                    parcelID = parcelIDAddressID[0];
                    parcelAddressID = parcelIDAddressID[1];
                }
            }

            if (parcelAddressID > -1) {
                //the selected parcel has multiple address
                for (var i = 0; i < taxParcels.length; i++) {
                    if ((taxParcels[i].parcelID == parcelID) && (taxParcels[i].parcelAddressID == parcelAddressID)) {
                        index = i;
                    }
                }
            }
            else {
                //the selected parcel do not have multiple address
                for (var i = 0; i < taxParcels.length; i++) {
                    if (taxParcels[i].parcelID == parcelID) {
                        index = i;
                    }
                }
            }

            if (index < 0) { return null; }

            return EDR.WEBGEOCODER.parcelsInComplex[index];
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('getParcelBySelectedParcelID(): ' + e.message);
        }
    },

    //AuthenticateDMP: function (data)
    //{
    //    var me=this
    //    var handlerURL = '/ordering/webgeocoderv3/getresourcesparcels.ashx';     
    //    var parceldata = data

    //    //var url = EDR.WEBGEOCODER.buildURL(handlerURL, '', qryStrs, true);            
    //    //$.support.cors = true;

    //    $.ajax({
    //        type: "GET",
    //        url: handlerURL,
    //        async: true,
    //        contentType: "application/x-www-form-urlencoded",
    //        dataType: "json",
    //        data: { 'Action': 'GetDMPAuthentication' },
    //        success: function (data) {
    //            CandyToken = data.candy
    //            me.parcelDetailsDataReceived(parceldata)
    //        },
    //        error: function (xhr, status, error) {
    //            //failed - ignore the failure as this is log tracking  
    //            me.parcelDetailsDataReceived(parceldata)
    //        }
    //    });
    //},

    parcelDetailsDataReceived: function (data) {
        ///<summary> Handles parcel details data </summary>
        try {
            EDR.WEBGEOCODER.log('parcelDetails data recieved');

            // validate
            //if ((typeof (data.parcels) == 'undefined') || (data.parcels == null) || (data.parcels.length === 0)) { throw new Error('No parcels found'); }
            if ((typeof (data.parcelDetails) == 'undefined') || (data.parcelDetails == null) || (data.parcelDetails.length === 0)) {
                // build dummy data so that the the popup displays
                data.parcelDetails = new Array();
                data.parcelDetails.push({
                    ownerHouseNumber: null,
                    ownerStreetName: null,
                    ownerCity: null,
                    ownerState: null,
                    ownerZipCode: null,
                    ownerAddress: null,
                    ownerLastLine: null,
                    owner1: null,
                    owner2: null
                });
            }

            // display the info window
            var curParcel = data.parcelDetails[0]; //AS:Changed data.parcels[0];           

            // pass the context data down
            curParcel.contextData = data.contextData;
            var parcelData = EDR.WEBGEOCODER.getParcelInfoWindowData(curParcel);
            if (parcelData == null) { return; }

            // check if the current parcel is the TP parcel
            var isTPParcel = false;
            if (EDR.WEBGEOCODER.tpParcel != null) {
                if (EDR.WEBGEOCODER.mergedParcelArray.length > 0) {
                    //To check/un-check all parcels in merged polygon
                    for (var i = 0; i < EDR.WEBGEOCODER.mergedParcelArray.length; i++) {
                        var mergedParcelID = EDR.WEBGEOCODER.mergedParcelArray[i].parcelID;
                        var mergedParcelHash = EDR.WEBGEOCODER.mergedParcelArray[i].parcelHash;
                        if ((curParcel.contextData.parcelID === mergedParcelID) && (curParcel.contextData.shapeWKTHash === mergedParcelHash)) {
                            isTPParcel = true;
                        }
                    }
                }
                else {
                    //To check/un-check only the original polygon
                    if ((curParcel.contextData.parcelID === EDR.WEBGEOCODER.tpParcel.parcelID) && (curParcel.contextData.shapeWKTHash === EDR.WEBGEOCODER.tpParcel.shapeWKTHash)) {
                        isTPParcel = true;
                    }
                }
            }
            else //on page refresh and also when user edit and return to this page from product selection page
            {
                if (EDR.WEBGEOCODER.polygonHandler.polygon != null && data.contextData.shapeWKT != null) //check whether there's a parcel selected for target property
                {
                    //lets check whether this parcel is inside polygon
                    if (EDR.WEBGEOCODER.parcelIsInsideThePolygon(EDR.WEBGEOCODER.polygonHandler.polygon, data.contextData.shapeWKT)) {
                        isTPParcel = true;
                    }
                }
            }

            var content = EDR.WEBGEOCODER.getParcelInfoWindow(data, parcelData, curParcel.contextData.parcelID, isTPParcel);

            var title = EDRV2.trim(curParcel.contextData.address);
            if (title === '') { title = 'Address Not Available'; }

            //AS: changed position: new google.maps.LatLng(curParcel.latitude, curParcel.longitude), //
            var infoWindowOptions = {
                title: title,
                content: content,
                position: new google.maps.LatLng(data.contextData.latitude, data.contextData.longitude),
                parentCssClass: 'taxmapInfoWindow',
                pixelOffset: 40,
                arrow: {
                    src: '/global/images/arrow_tooltip_white.png',
                    width: 32,
                    height: 22,
                    offset: 1
                }
            };

            // close any existing parcel window, and highlight the selected property
            if (EDR.WEBGEOCODER.parcelInfoWindow != null) {

                EDR.WEBGEOCODER.log('removing the existing parcel info window');

                EDR.WEBGEOCODER.parcelInfoWindow.remove();
                EDR.WEBGEOCODER.parcelInfoWindow = null;
            }

            EDR.WEBGEOCODER.parcelInfoWindow = new EDR.EDRMapV2Google.DraggablePopup(map, infoWindowOptions);
            EDR.WEBGEOCODER.parcelInfoWindow.onPopupClosed = EDR.WEBGEOCODER.onParcelInfoWindowClosed;

            //zoom based on property area if info window is displayed on page load
            if (EDR.WEBGEOCODERPAGE.zoomParcelOnPageLoad) {
                EDR.WEBGEOCODERPAGE.zoomParcelOnPageLoad = false;
                EDR.WEBGEOCODER.zoomPolygonBasedOnArea();
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('[ERROR] parcelDetailsDataReceived(): ' + e.message);
        }
    },

    plotSelectedPolygon: function (polyCoords, includeTPinZoom, executeSave) {
        //Convert/Parse the uploaded polygon to DVGCoordinates and draw it on google maps using existing webgeocoder functions.
        var dvgCoords = EDR.WEBGEOCODER.parseGeoJsonToDVGCoordinates(polyCoords);

        if (dvgCoords != null && dvgCoords != '') {
            //Draw the polygon on google maps using existing webgeocoder functions.
            //EDR.WEBGEOCODER.polygonHandler.polygonOptions.autoEditPolygon = EDR.WEBGEOCODER.autoEditPolygon;
            EDR.WEBGEOCODER.polygonHandler.setPolygonDVGCoordinates(dvgCoords);

            // Matomo Event Tracker
            EDR.WEBGEOCODER.trackEventMatomoPlotUploadedPolygonOnMap();

            ////In future, if the user is allowed to upload the TP (center of the polygon), use below code to set that as the new TP
            //EDR.WEBGEOCODER.polygonHandler.tpMarker = tpMarker;

            EDR.WEBGEOCODER.zoomToDisplayPolyAndTPonTheMap(includeTPinZoom);

            //Clear any previous errors
            //EDR.WEBGEOCODER.clearErrorMessages();

            if (executeSave) {
                //Save the polygon and update the UI so the map would zoom out and show the polygon in the edit mode.
                if (EDR.WEBGEOCODER.executePolygonSave('')) {
                    EDR.WEBGEOCODER.updateAreaUI();
                    EDR.WEBGEOCODER.saveTrackingInformation(new Date(), EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_LoadPolygonFromAPI, 'Plotted the uploaded polygon on the map');
                    // Matomo Event Tracker
                    EDR.WEBGEOCODER.trackEventMatomoSavedUploadedPolygon();
                }
                else {
                    //Unale to save, unable to plot the coordinates on the google map
                    EDR.WEBGEOCODER.logError('plotUploadedPolygon().executePolygonSave(): Attempt to save polygon after plotting it on the map failed. Polygon is not valid. ' + document.getElementById('lblKmlErrorMessage').innerHTML);
                    EDR.WEBGEOCODER.saveTrackingInformation(new Date(), EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_LoadPolygonFromAPI, 'plotUploadedPolygon().executePolygonSave(): Attempt to save polygon after plotting it on the map failed. Polygon is not valid. ' + document.getElementById('lblKmlErrorMessage').innerHTML);
                }
            }
        }
        else {
            EDR.WEBGEOCODER.saveTrackingInformation(new Date(), EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_LoadPolygonFromAPI, 'Could not plot the polygon on the map. Invalid polygon data.');
            EDR.WEBGEOCODER.setErrorMessages("Uploaded file may be invalid", "Could not plot the polygon on the map. Invalid polygon data. Try uploading your file again.");
            throw new Error('Could not plot the polygon on the map. Invalid polygon data. Try uploading your file again.');
        }

    },
    zoomToDisplayPolyAndTPonTheMap: function (includeTP) {
        ///<summary>Zoom to display both polygon and TP star in the map view   </summary>
        /// <returns> </returns>
        try {
            var poly = EDR.WEBGEOCODER.polygonHandler.polygon;

            if (poly != null) {

                var bounds = new google.maps.LatLngBounds();
                //Add coordinates of the polygon to the bounds so the entire polygon would be visible in the map
                ////bounds.extend(new google.maps.LatLng(polyCoords[0][1], polyCoords[0][0]));
                var paths = poly.getPaths();
                var path;
                for (var p = 0; p < paths.getLength(); p++) {
                    path = paths.getAt(p);
                    for (var i = 0; i < path.getLength(); i++) {
                        bounds.extend(path.getAt(i));
                    }
                }
                //Add TP to bounds so the TP star would be visible in the map
                if (includeTP && tpMarker != null) { bounds.extend(new google.maps.LatLng(tpMarker.position.lat(), tpMarker.position.lng())); }

                //set the bounds for the map so the map will zom in/out to display all coordinates in the bounds
                map.fitBounds(bounds);
            }
        }
        catch (e) {
            // ignore this exception
        }
    },

    saveTrackingInformation: function (startTime, envTrackingActionType, strErrorMessage) {
        /// <summary> Save tracking information Actiontype and Message </summary>
        try {

            //Prep and variable declarations
            var handlerURL = EDR.WEBGEOCODER.handlerURL;
            var geoGUID = EDR.WEBGEOCODER.webGeocoderSessionGUID;
            var sourcePropGUID = EDR.WEBGEOCODER.sourcePropertyGUID;
            var envSource = EDR.WEBGEOCODER.envSource;
            var stTime = startTime.toLocaleString();

            //var url = EDR.WEBGEOCODER.buildURL(handlerURL, '', qryStrs, true);            
            //$.support.cors = true;
            $.ajax({
                type: "POST",
                url: handlerURL,
                async: true,
                contentType: "application/x-www-form-urlencoded",
                dataType: "text/xml",
                data: { 'TYPE': 'SAVETRACKINGINFO', 'geoGuid': encodeURIComponent(geoGUID), 'propGuid': encodeURIComponent(sourcePropGUID), 'eSource': encodeURIComponent(envSource), 'actionType': encodeURIComponent(envTrackingActionType), 'startTime': stTime, 'sMessage': strErrorMessage },
                success: function (data) {
                    //successfully posted
                },
                error: function (xhr, status, error) {
                    //failed - ignore the failure as this is log tracking                    
                }
            });
        }
        catch (err) {
            EDR.WEBGEOCODER.logError('[ERROR] saveTrackingInformation() Failed ' + err.message);
        }
    },

    getMultiParcelDropDownHtml: function (data) {
        /// <summary> Generate dropdown for multi-parcel </summary>
        var multiParcelDropdownHtml = '';
        try {
            //multi-parcel dropdown
            var taxParcels = EDR.WEBGEOCODER.parcelsInComplex;
            if (taxParcels.length > 1) {
                multiParcelDropdownHtml += '<div class="multiParcelSelectContainer">';
                multiParcelDropdownHtml += '<select  id="selectMultiParcel" name="selectMultiParcel" class="multiParcelSelect" onchange="EDR.WEBGEOCODER.multiParcelSelectChange(this);">';
                var multiParceltData;
                var multiParcelAddress;
                multiParcelDropdownHtml += '<option selected="selected" value="0">Additional Tax Parcels Located Here</option>';
                for (var i = 0; i < taxParcels.length; i++) {
                    var optParcelIdentifier;
                    isParcelSelected = false;
                    multiParcelData = taxParcels[i];
                    multiParcelAddress = multiParcelData.address;
                    optParcelIdentifier = multiParcelData.parcelID;
                    if ((multiParcelData.parcelAddressID != null) && (multiParcelData.parcelAddressID != '')) {
                        //parcel has address id
                        optParcelIdentifier = multiParcelData.parcelID + EDR.WEBGEOCODER.parcelAddressIDSeperator + multiParcelData.parcelAddressID;
                    }

                    if ((multiParcelAddress == null) || (multiParcelAddress == '')) { multiParcelAddress = 'N/R'; }
                    multiParcelDropdownHtml += '<option value="' + optParcelIdentifier + '" >' + multiParcelAddress + ' (' + multiParcelData.apn + ')</option>';
                }
                multiParcelDropdownHtml += '</select>';
                multiParcelDropdownHtml += '</div>';
                multiParcelDropdownHtml += '<div style="line-height:7px;">&nbsp;</div>';
            }

            return multiParcelDropdownHtml;
        }
        catch (e) {
            // do nothing
            EDR.WEBGEOCODER.logError('getMultiParcelDropDownHtml(): ' + e.message);
            return multiParcelDropdownHtml;
        }
    },

    onParcelInfoWindowClosed: function () {
        /// <summary> Event handler for when the parcel info window closes </summary>

        try {
            // remove any selectd parcel property boundary
            if (EDR.WEBGEOCODER.parcelPolygonHandler != null) { EDR.WEBGEOCODER.parcelPolygonHandler.removePolygon(); }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('[ERROR] onParcelInfoWindowClosed: ' + e.message);
        }
    },

    defaultMissingText: 'Not reported',

    getParcelInfoWindowData: function (parcel) {
        /// <summary> 
        ///           Generate Parcel info window data
        ///</summary>
        /// <returns> data array with fields to display</returns>
        try {
            var apn, ownAddress, ownCity, ownState, ownZipCode, ownStreetNo, ownStType, owner1, owner2;
            var ownAddressLine, ownLastLine;

            // format address
            var ownDisplayAddress = '';

            // keep separate pieces in case the API's last line and formatter address are out of sync
            apn = parcel.contextData.apn;
            if ((apn == null) || (apn === '')) { apn = EDR.WEBGEOCODER.defaultMissingText; }
            ownStreetNo = parcel.ownerHouseNumber || '';
            ownAddress = parcel.ownerStreetName || EDR.WEBGEOCODER.defaultMissingText;
            ownCity = parcel.ownerCity || EDR.WEBGEOCODER.defaultMissingText;
            ownState = parcel.ownerState || EDR.WEBGEOCODER.defaultMissingText;
            ownZipCode = parcel.ownerZipCode || EDR.WEBGEOCODER.defaultMissingText;
            // the API provides this two use them
            ownAddressLine = parcel.ownerAddress || EDR.WEBGEOCODER.defaultMissingText;
            ownLastLine = parcel.ownerLastLine || EDR.WEBGEOCODER.defaultMissingText;
            owner1 = parcel.owner1 || EDR.WEBGEOCODER.defaultMissingText;
            owner2 = parcel.owner2 || EDR.WEBGEOCODER.defaultMissingText;
            // other info
            var zoning, landUseDesc, lotArea;
            zoning = parcel.zoning || EDR.WEBGEOCODER.defaultMissingText;
            landUseDesc = parcel.useCode || EDR.WEBGEOCODER.defaultMissingText;

            if ((typeof (parcel.contextData.areaSquareMeters) == 'undefined') || (parcel.contextData.areaSquareMeters == null)) {
                lotArea = EDR.WEBGEOCODER.defaultMissingText;
            }
            else {
                // convert the lot area into acres
                lotArea = parcel.contextData.areaSquareMeters / 4046.86;	// 1 acre = 4046.86 sq meter

                // since we only want the hundredth, round off the value
                lotArea = Math.round(100 * lotArea) / 100;

                // add the units
                lotArea += ' ACRES';
            }

            if ((ownAddressLine === EDR.WEBGEOCODER.defaultMissingText) && (ownLastLine === EDR.WEBGEOCODER.defaultMissingText)) {
                ownDisplayAddress = EDR.WEBGEOCODER.defaultMissingText;
            }
            else {
                ownDisplayAddress = ownAddressLine + '<br>' + ownLastLine;
            }

            // build the address value
            var displayAddress = EDR.WEBGEOCODER.defaultMissingText;
            var addr = EDRV2.trim(parcel.contextData.address);
            var city = EDRV2.trim(parcel.contextData.city);
            var state = EDRV2.trim(parcel.contextData.state);
            var zip = EDRV2.trim(parcel.contextData.zip);
            if ((addr != '') && (city != '') && (state != '') && (zip != '')) {
                displayAddress = addr + '<br/>' + city + ' ' + state + ', ' + zip;
            }

            // append second owner : 
            var data = new Array();

            data.push({ label: 'Tax ID', value: apn });
            data.push({ label: 'Address', value: displayAddress });
            data.push({ label: 'Owner', value: owner1 });
            //data.push({ label: 'Owner Addr', value: EDRV2.trim(ownDisplayAddress) });
            data.push({ label: 'Land Use', value: zoning });
            data.push({ label: 'Descr', value: landUseDesc }); // not available in the parcelDetails API ?
            data.push({ label: 'Lot Area', value: lotArea }); // not available in the parcelDetailsAPI ?		    

            return data;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('getParcelInfoWindowData(): ' + e.message);
        }
    },

    switchParcelsData: null,
    currentParcelIndex: 0,

    getParcelInfoWindow: function (data, newParcelData, parcelID, isTP) {
        /// <summary> 
        ///           Generate Parcel info window
        ///</summary>
        /// <returns> info window html</returns>
        try {
            //validate
            if ((typeof (newParcelData) == 'undefined') || (newParcelData == null) || (newParcelData.length == 0)) { return ''; }
            //parcelID = EDRV2.trim(parcelID);
            if (typeof (isTP) != 'boolean') { isTP = false; }

            var html = '';
            html += EDR.WEBGEOCODER.getMultiParcelDropDownHtml(data)

            html += '<div class="container-fluid">';

            // var handlerParcelsURL = EDR.WEBGEOCODER.handlerParcelsURL;


            ////Set data to post to server
            //var qryData = [];
            //qryData.push({ name: "ACTION", value: 'GETDMPAUTHENTICATION' });
            //var qryInputString = EDRV2.HTTP.createDataString(qryData);

            //Create and make the call
            //var candyToken;
            //var resp = EDRV2.HTTP.requestPost(handlerParcelsURL, qryInputString, null);
            //if (resp != null || resp.contentLength > "0")
            //    var TokenData = eval('(' + resp.data + ')');
            //    candyToken = TokenData.candy


            //var dmpUrl = "http://dc1.parcelstream.com/GetQuery.aspx?dataSource=SS.Prop.PropertyDetail/PropertyDetail&query=fips_code='" + data.contextData.fips + "'and PARCEL_APN='" + data.contextData.apn + "'&output=custom&transformer=http%3A%2F%2Fmaps.digitalmapcentral.com%2Fproduction%2Faspx%2FAppUtils%2FPropertyDetailTransformer%2FParcelFullDetail.xsl&maxrecords=1&SS_CANDY=" + candyToken;


            var rowClass = 'oddRow';
            for (var i = 0; i < newParcelData.length; i++) {
                rowClass = 'oddRow';
                if ((i % 2) == 0) { rowClass = 'evenRow'; }

                html += '<div class="row ' + rowClass + '">';
                html += '<div class="col-md-3 col-sm-3 col-xs-3 infoWindowLabel">' + newParcelData[i].label + ':</div>';
                html += '<div class="col-md-9 col-sm-9 col-xs-9 infoWindowValue">' + newParcelData[i].value + '</div>';
                html += '</div>';
            }
            //if (data.contextData.fips != '' && data.contextData.apn != '') {
            //    html += '<div class="row ' + rowClass + '">';
            //    html += '<div class="col-md-3 col-sm-3 col-xs-3 infoWindowLabel">Detail Report</div>';
            //    html += '<div class="col-md-9 col-sm-9 col-xs-9 infoWindowValue"><a href="' + dmpUrl + '" target="_blank">Click Here</a></div>';
            //    html += '</div>';
            //}

            html += '</div><div style="line-height: 5px;">&nbsp;</div>';
            //html += '<div class="taxmapInfoWindowSource">Source: Digital Map Products, 2014</div>';
            html += '<div class="container-fluid">';
            html += '<div class="row evenRow" style="display: inline-block; border-spacing: 2px; width: 270px;">';
            html += '<table border="0" cellpadding="0">';
            html += '<tr>';
            html += '<td>';
            //html += '<select><option>0</option><option>2</option></select>'
            html += '&nbsp;<input type="image" id="imgPolyStart" src="/global/SharedResources/EDRMapping/images/drawtool_faq9.png" width="20" />&nbsp;&nbsp;';
            html += '</td>';
            html += '<td>';
            html += '<div class="checkbox">';

            // if the selected property has the same parcelID, and fips as the tp parcel, display it as selected
            //if (isTP || (!parcelOutsidePolygon)) {
            if (isTP) {
                html += '<label style="font-weight: bold; font-size: 13px; text-valign: middle;">';
                html += '<input type="checkbox" id="cbUpdateTP" onclick="EDR.WEBGEOCODER.confirmTPBoundaryChange(this, ' + isTP.toString() + ', ' + parcelID + ', false);" checked >';
                html += 'Select for Property Boundary';
            }
            else {

                //There's a polygon selected for target property and the new parcel is adjacent to the current target property polygon
                if (EDR.WEBGEOCODER.polygonHandler.polygon != null) {
                    if (EDR.WEBGEOCODER.checkForContiguousPolygons(data.contextData.shapeWKT)) {
                        html += '<label style="font-weight: bold; font-size: 13px; text-valign: middle;">';
                        html += '<input type="checkbox" id="cbAddToTP" onclick="EDR.WEBGEOCODER.confirmTPBoundaryChange(this, ' + isTP.toString() + ', ' + parcelID + ', true);" >';
                        html += 'Add to Property Boundary';
                    }
                    else {
                        //html += '<input type="checkbox" id="cbUpdateTP" onclick="EDR.WEBGEOCODER.confirmTPBoundaryChange(this, ' + isTP.toString() + ', ' + parcelID + ', false);" >';
                        //html += 'Select for Property Boundary';
                        //html += '</label><br/>';
                        html += '<label style="font-weight: bold; color: gray; font-size: 13px; text-valign: middle;" data-container="body" name="pop_contiguous_prop_info" id="pop_contiguous_prop_info" onmouseenter="javascript: EDR.WEBGEOCODER.showContiguousPropertyHint(true);" onmouseleave="javascript: EDR.WEBGEOCODER.showContiguousPropertyHint(false);">';
                        html += '<input type="checkbox" disabled id="cbAddToTP">';
                        html += 'Add to Property Boundary&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
                    }
                }
                else {
                    html += '<label style="font-weight: bold; font-size: 13px; text-valign: middle;">';
                    html += '<input type="checkbox" id="cbUpdateTP" onclick="EDR.WEBGEOCODER.confirmTPBoundaryChange(this, ' + isTP.toString() + ', ' + parcelID + ', false);" >';
                    html += 'Select for Property Boundary';
                }
            }
            html += '</label>';
            html += '</div>';
            html += '</td>';
            html += '</tr>';
            html += '</table>';
            //html += '<div style="margin: 3px; font-size: 8px;">';
            //html += 'The boundary determines the shape of the search area and will be displayed on your final reports.';
            //html += '</div>';
            html += '</div>';
            html += '</div>';
            html += '<div style="line-height: 5px;">&nbsp;</div>';
            html += '<div>';
            html += '<b>Note</b>: If you want any of this text and/or Tax ID# to be included with your order, enter it in the fields on the following pages.';
            html += '</div>';

            return html;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('[ERROR] getParcelInfoWindow(): ' + e.message);
        }
    },

    multiParcelSelectChange: function (src) {
        /// <summary> 
        ///           parcel dropdown changed by user
        ///</summary>
        try {
            // validate
            if ((typeof (src) == 'undefined') || (src == null)) { return; }
            var startTime = new Date();
            var selectedParcelId = src.value;
            //select change to default item
            if (src.selectedIndexId == 0) {
                return;
            };
            //Step1: get the parcel information
            var curParcel = EDR.WEBGEOCODER.getParcelBySelectedParcelID(selectedParcelId);

            if (curParcel == null) {
                EDR.WEBGEOCODER.log('multiParcelCboChange(): Unable to find the selected parcel with parcelID: ' + selectedParcelId);
                return;
            }

            //EDR.WEBGEOCODER.removeCustomExpandedCombo();

            // check if the current parcel data exists            
            if (EDR.WEBGEOCODER.parcelInfoWindow != null) { // close the tax parcel info window just in case
                EDR.WEBGEOCODER.parcelInfoWindow.remove();
            }
            //EDR.WEBGEOCODER.mapParcels = null;
            if ((EDR.WEBGEOCODER.mapParcels == null) || (EDR.WEBGEOCODER.mapParcels.length == 0)) { EDR.WEBGEOCODER.mapParcels = new Array(); }
            if (EDR.WEBGEOCODER.getParcelByParcelID(curParcel.parcelID) == null) {
                EDR.WEBGEOCODER.mapParcels.push(curParcel);
            }
            // get the parcel parcels by apn
            EDR.WEBGEOCODER.getParcelDetailsByAPN(curParcel);
            EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_MultiParcelChanged, 'selected a parcel from multi parcel list');
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('[ERROR] multiParcelSelectChange(): ' + e.message);
        }
    },

    confirmTPBoundaryChange: function (src, isTP, parcelID, bAddToBoundary) {
        /// <summary> 
        ///           Confirm TP boundary change by user
        ///</summary>
        /// <returns> </returns>
        try {
            // validate
            if ((typeof (src) == 'undefined') || (src == null)) { return; }
            if (typeof (isTP) != 'boolean') { isTP = false; }

            var startTime = new Date();

            EDR.WEBGEOCODER.trackEventMatomoPropertyBoundarySelection(isTP, bAddToBoundary);

            // update the current the tp boundary checked state
            EDR.WEBGEOCODER.originalTaxParcelBoundaryCheckedState = isTP;

            // figure out if the request is to remove, or change the TP boundary
            var remove = false;
            if (isTP) {
                // if the current dialog is TP, the request is to remove the boundary
                remove = true;
            }
            else {
                //To save the tracking log if the user selected the initial parcel
                //check whether this parcel is the first selection and whether it is the default lat/log geocoded
                if (EDR.WEBGEOCODER.polygonHandler.polygon == null && EDR.WEBGEOCODER.tpParcel != null && !bAddToBoundary) {
                    //no polygon exists
                    // is this parcel the same initial parcel based on geocoded lat/long
                    if (parcelID = EDR.WEBGEOCODER.tpParcel.parcelID) {
                        EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_SelectGeocodedParcel, 'User selected the parcel based on the initial geocoded lat/long as TP');
                    }
                }
            }

            // check if an existing tp parcel polygon exists
            if (EDR.WEBGEOCODER.polygonHandler.polygon != null) {
                var title = EDR.WEBGEOCODER.parcelChangeModal.title;
                var content = EDR.WEBGEOCODER.parcelChangeModal.content;
                //if (bAddToBoundary) {
                //    content = EDR.WEBGEOCODER.parcelChangeModal.content.replace("You have selected to use a different property boundary.", "You have selected an adjacent property to extend the current boundary.");
                //}			    

                if (remove) {
                    // check if the client has modified the polygon.  if not, no need to prompt the user.
                    if (!EDR.WEBGEOCODER.parcelPolygonModified) {
                        EDR.WEBGEOCODER.updateTPBoundary(src, parcelID, bAddToBoundary);
                        return;
                    }

                    title = EDR.WEBGEOCODER.parcelRemoveModal.title;
                    content = EDR.WEBGEOCODER.parcelRemoveModal.content;
                }

                if (!bAddToBoundary) {

                    // update the modal content
                    $('#confirmTPChange .modal-title').html(title);
                    $('#confirmTPChange .modal-body').html(content);

                    // update the click event
                    $('#btnContinueTPChange').unbind('click');
                    $('#btnContinueTPChange').click(function () {
                        EDR.WEBGEOCODER.updateTPBoundary(src, parcelID, bAddToBoundary);
                    });
                    $('#confirmTPChange').modal('show');
                }
                else {
                    EDR.WEBGEOCODER.updateTPBoundary(src, parcelID, bAddToBoundary);
                }
            }
            else {
                EDR.WEBGEOCODER.updateTPBoundary(src, parcelID, bAddToBoundary);
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('[ERROR] confirmTPBoundaryChange(): ' + e.message);
        }
    },

    zoomPolygonBasedOnArea: function () {
        console.log("Zoom zoomPolygonBasedOnArea ");
        /// <summary> 
        ///           Zoom the Map based on the selected polygon area in sq feet.
        ///           (1). Use EDR.EDRMapV2GoogleV3.PolygonUtilities.calculatePolygonPerimeterArea to get area in sq feet
        ///           (2). Set map zoom level based on area and the default zoom level
        ///</summary>
        /// <returns> </returns>
        try {
            // check if the tax map option is included
            if (EDR.WEBGEOCODER.showTaxMapControl) {

                if (EDR.WEBGEOCODER.parcelPolygonHandler != null) {
                    //Get the current polygon	           
                    var poly = EDR.WEBGEOCODER.parcelPolygonHandler.polygon;

                    //Test if we have a polygon or not
                    if (poly != null) {
                        //We have a polygon, so update the UI
                        var polyUtilResult = EDR.EDRMapV2GoogleV3.PolygonUtilities.calculatePolygonPerimeterArea(poly, 10, 1); ////Calculates the area 
                        //Fit the selected polygon to the maps extend. If the parcel area/perimeter is too large, reduce zoom. If it is too small increase zoom		
                        var addressInfo = EDR.WEBGEOCODER.getAddress();
                        var newZoom = map.zoom;
                        var optimumZoomLevel = EDR.WEBGEOCODER.minParcelZoomLevel + 3 //15 + 3 = 18
                        if (addressInfo != null) {
                            var def = EDR.WEBGEOCODER.stateDefaultMappingOptions[addressInfo.State.toUpperCase()];
                            //var polyPeriMeter = polyUtilResult.perimeterInFeet;
                            //var newZoom = Math.round(polyUtilResult.perimeterInFeet / 10000);
                            var polyAreaInSqFeet = polyUtilResult.areaInSquareFeet;
                            if (def != null && polyAreaInSqFeet != null) {
                                switch (true) {
                                    case polyAreaInSqFeet > 40000000: //reduce zoom for large polygon	
                                        newZoom = optimumZoomLevel - 5;
                                        break;
                                    case (polyAreaInSqFeet >= 30000000 && polyAreaInSqFeet <= 40000000):
                                        newZoom = optimumZoomLevel - 4;
                                        break;
                                    case (polyAreaInSqFeet >= 10000000 && polyAreaInSqFeet <= 30000000):
                                        newZoom = optimumZoomLevel - 3;
                                        break;
                                    case (polyAreaInSqFeet >= 2000000 && polyAreaInSqFeet < 10000000):
                                        newZoom = optimumZoomLevel - 2;
                                        break;
                                    case (polyAreaInSqFeet >= 300000 && polyAreaInSqFeet < 2000000):
                                        newZoom = optimumZoomLevel - 1;
                                        break;
                                    //case (polyAreaInSqFeet >= 40000 && polyAreaInSqFeet < 300000):
                                    //    newZoom = optimumZoomLevel;
                                    //    break;
                                    //case (polyAreaInSqFeet >= 20000 && polyAreaInSqFeet < 40000):
                                    //    newZoom = optimumZoomLevel + 1;
                                    //    break;
                                    //case polyAreaInSqFeet < 20000:
                                    //    newZoom = optimumZoomLevel + 2;
                                    //    break;
                                    default:
                                        newZoom = map.zoom;
                                        break;
                                }
                                if (newZoom != map.zoom) {
                                    //Get the TPMarker coordinates to center the map - if we are changing the zoom level
                                    var latLongControlIDs = EDR.WEBGEOCODER.latitudeLongitudeControl;
                                    //Get the coordinates and validate
                                    var coords = EDR.CONTROLS.LATITUDELONGITUDE.GetCoordinates(latLongControlIDs)
                                    //if target property coordinates are available
                                    if ((coords.Latitude != 0.0) && (coords.Longitude != 0.0)) {
                                        map.setCenter(new google.maps.LatLng(coords.Latitude, coords.Longitude)); //map.setCenter(position);
                                        //set the new zoom level
                                        map.setZoom(newZoom);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        catch (err) {
            EDR.WEBGEOCODER.setErrorMessages("Unable to zoom based on polygon area - zoomPolygonBasedOnArea", [err.message, 'Please try again']);
        }
    },

    originalTaxParcelBoundaryCheckedState: false,

    resetTaxParcelPopup: function () {
        /// <summary> 
        ///           Reset the tax parcel info popup
        ///</summary>
        /// <returns> </returns>
        try {
            // close the modal
            $('#confirmTPChange').modal('hide');
            //To set the selected parcel as TP polygon
            $('#cbUpdateTP').prop('checked', EDR.WEBGEOCODER.originalTaxParcelBoundaryCheckedState);
            //To add the adjacent polygon to TP polygon
            $('#cbAddToTP').prop('checked', false);
        }
        catch (e) {
            // do nothing
        }
    },

    getGooglePlygonFromShapeWKT: function (stringShapeWKT) {
        /// <summary> 
        ///           Create a google polygon from ShapeWKT coordinates	        
        ///</summary>
        /// <returns> google polygon </returns>
        try {
            var polyCoords = EDR.WEBGEOCODER.parseParcelPolygonToCoordinates(stringShapeWKT);
            if ((polyCoords == null) || (polyCoords.length == 0)) { return; }
            var curPolyCoords;
            var curPoly;

            if (polyCoords.length > 1) {

                var mapLatLng = new google.maps.LatLng(EDR.WEBGEOCODER.mapClickCoordinate.latitude, EDR.WEBGEOCODER.mapClickCoordinate.longitude);

                // there are multiple polygon coordinates.  figure out which polygon coordinates belong to.
                for (var i = 0; i < polyCoords.length; i++) {
                    curPolyCoords = polyCoords[i];

                    // convert the current polygon coordinates to google polygon
                    var mapCoords = new Array();
                    for (var j = 0; j < curPolyCoords.length; j++) {
                        mapCoords.push(new google.maps.LatLng(curPolyCoords[j].latitude, curPolyCoords[j].longitude));
                    }
                    var cPoly = new google.maps.Polygon({
                        paths: mapCoords
                    });

                    // check if the current map point is within the current polygon
                    if (google.maps.geometry.poly.containsLocation(mapLatLng, cPoly)) {
                        curPoly = cPoly;
                        break;
                    }
                }
            }
            else {
                // there is only one set of coordinates.  set these coordinates to be converted
                curPolyCoords = polyCoords[0];
                var mapCoords = new Array();
                for (var j = 0; j < curPolyCoords.length; j++) {
                    mapCoords.push(new google.maps.LatLng(curPolyCoords[j].latitude, curPolyCoords[j].longitude));
                }
                curPoly = new google.maps.Polygon({
                    paths: mapCoords
                });
            }

            //if there are multiple parcel, take the first

            return curPoly;
        }
        catch (err) {
            EDR.WEBGEOCODER.logError('getGooglePlygonFromShapeWKT(): ' + err.message);
            return;
        }
    },

    updateTPBoundary: function (src, parcelID, bAddToBoundary) {
        /// <summary> 
        ///           Update the Target Property Boundary
        ///           (1). If bAddToBoundary is false, Select the new parcel as the new TP 
        ///           (2). If bAddToBoundary is true, Add the new parcel to the existing boundary
        ///           (3). If src.checked is false, Remove the current TP
        ///</summary>
        /// <returns> </returns>
        try {
            // close the modal
            $('#confirmTPChange').modal('hide');
            var startTime = new Date();
            // validate
            //parcelID = EDRV2.trim(parcelID);
            //if ((typeof (parcelID) == 'undefined') || (parcelID == null) || (parcelID === '')) { throw new Error('Unable to get parcel data by parcelID because missing valid parcelID number'); }
            EDR.WEBGEOCODER.log('Updating TP to parcelID: ' + parcelID);

            // check if the request is to update the new TP boundary, or to remove the TP boundary
            if (src.checked) {
                //Step1: get the parcel information
                var curParcel = EDR.WEBGEOCODER.getParcelByParcelID(parcelID);

                if (curParcel == null) {
                    EDR.WEBGEOCODER.log('updateTPBoundary(): Unable to find parcel with parcelID: ' + parcelID);
                    return;
                }

                if (bAddToBoundary) {

                    /**********************************************************
                    * Add adjacent polygon to the TP polygon                 *
                    * Merge the polygons and update the merged polygon as TP *
                    **********************************************************/
                    //Step2 - Merge the existing polygon to the selected parcel
                    var dissolvedGeometry = EDR.WEBGEOCODER.tempMergedGeometry;
                    if (dissolvedGeometry == null) {
                        dissolvedGeometry = EDR.WEBGEOCODER.mergeAndGetDissovedGeometry(curParcel.shapeWKT);
                    }

                    //Step3 - check whether the merge was valid
                    if (dissolvedGeometry.geometries != undefined && dissolvedGeometry.geometries.length > 1) {
                        EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_PolygonMerged, 'Geometries are not contiguous - could not merge parcel polygons');
                        EDR.WEBGEOCODER.log('updateTPBoundary() mergeAndGetDissovedGeometry() : Unable to merge the existing parcel/polygon with new parcel with parcelID: ' + parcelID);
                        throw new Error('Geometries are not contiguous, cannot merge parcel property boundary polygon.');
                    }
                    else {
                        EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_PolygonMerged, 'parcel polygons merged successfully');
                        /*
                            ////if we should reset the TPMarker to the centroid of the new merged polygon			            
                            ////find central of new merged polygon to set as target property
                            //var centroid = mergedPoly.getBounds().getCenter();	                
                            //// Move the tp marker to center of new polygon
                            //var tpMarker = EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(centroid.A, centroid.F), base.TPMarker, false);
                            ////Update the TPMarker			            
                            //EDR.WEBGEOCODER.polygonHandler.tpMarker = tpMarker;			            		            
                            //// "trigger" the tp marker on move event
                            //EDR.WEBGEOCODER.onTPMarkerMoved(tpMarker);
                        */

                        //Step4. Convert JSTS merged geometry to google polygon coordinates
                        var googleCoords = EDR.WEBGEOCODER.jsts2googleMapCoords(dissolvedGeometry);

                        //Step5. Convert google polygon coordinates to dvg coordinates
                        var dvgCoords = EDR.WEBGEOCODER.parseGoogleCoordinatesToDVGCoordinates(googleCoords);

                        ////Step6 - remove the current TP polygon for setting new parcel/property as TP polygon
                        //EDR.WEBGEOCODER.removePolygon();                     	            

                        //Step7. Add the new parcel to the TP polygon global variable
                        EDR.WEBGEOCODER.mergedParcelArray.push({ parcelID: parcelID, parcelHash: curParcel.shapeWKTHash });
                    }
                }
                else {
                    /* Change the TP polygon global variable to store the selected property/parcel */
                    //Step4. Reset the TP polygon global variable
                    EDR.WEBGEOCODER.mergedParcelArray = [];

                    //Step5. Add the new polygon to the TP polygon global variable
                    EDR.WEBGEOCODER.mergedParcelArray.push({ parcelID: parcelID, parcelHash: curParcel.shapeWKTHash });

                    ////Step6. Remove the current TP polygon for setting new parcel/property as TP polygon
                    //EDR.WEBGEOCODER.removePolygon();

                    //Step7. Move the tp marker to the parcel's lat/long			        
                    var tpMarker = EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(curParcel.latitude, curParcel.longitude), base.TPMarker, false);

                    //Step8. Update the TPMarker
                    EDR.WEBGEOCODER.polygonHandler.tpMarker = tpMarker;

                    //Step9. Update new polygon as TP
                    EDR.WEBGEOCODER.tpParcel = curParcel;

                    //Step10. "trigger" the tp marker on move event
                    EDR.WEBGEOCODER.onTPMarkerMoved(tpMarker);

                    // Step11. Get dvg coordinates for the new polygon/parcel 
                    var dvgCoords = EDR.WEBGEOCODER.parseParcelPolygonToDVGCoordinates(curParcel);
                }

                //Set the new coordinates for the target property polygon
                EDR.WEBGEOCODER.polygonHandler.setPolygonDVGCoordinates(dvgCoords);

                //Clear any previous errors
                EDR.WEBGEOCODER.clearErrorMessages();

                //Save the polygon
                if (EDR.WEBGEOCODER.executePolygonSave('')) {
                    EDR.WEBGEOCODER.updateAreaUI();
                }
                else {
                    throw new Error('Unable to save parcel property boundary polygon');
                };
            }
            else {
                // remove the current TP polygon
                EDR.WEBGEOCODER.removePolygon();
                // the request is to remove the TP boundary.
                EDR.WEBGEOCODER.tpParcel = null;
                EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_TPParcelRemoved, 'Target property parcel removed');
            }
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('[ERROR] updateTPBoundary(): ' + e.message);
        }
        finally {
            //Remove the current parcel polygon
            EDR.WEBGEOCODER.parcelPolygonHandler.removePolygon(false);

            //Close the popup
            EDR.WEBGEOCODER.parcelInfoWindow.remove();
        }
    },

    jsts2googleMapCoords: function (geometry) {
        var coordArray = geometry.getCoordinates();
        GMcoords = [];
        for (var i = 0; i < coordArray.length; i++) {
            GMcoords.push(new google.maps.LatLng(coordArray[i].y, coordArray[i].x));
        }
        return GMcoords;
    },

    checkForContiguousPolygons: function (shapeWktPolygon) {
        /// <summary> (1). Call mergeAndGetDissovedGeometry to get the dissolved geomtry after merge
        ///           (2). checks whether geometries are adjacent (have common boundary/edge) and properly dissoved 
        ///</summary>
        /// <returns> true/false </returns>
        try {

            var dissolvedGeometry = EDR.WEBGEOCODER.mergeAndGetDissovedGeometry(shapeWktPolygon)
            if (dissolvedGeometry.geometries != undefined && dissolvedGeometry.geometries.length > 1) {
                //alert('Geometries are not contiguous, cannot merge'); 
                EDR.WEBGEOCODER.tempMergedGeometry = null;
                return false;
            }
            else {
                EDR.WEBGEOCODER.tempMergedGeometry = dissolvedGeometry;
            }

            return true;

        }
        catch (e) {
            EDR.WEBGEOCODER.logError('checkForContiguousPolygons(): ' + e.message);
            return false;
        }
    },

    mergeAndGetDissovedGeometry: function (shapeWktPolygon) {
        /// <summary> (1). Parses the shapeWKT polygon to a list of polygon coordinates 
        ///           (2). merges with 1st/old polygon 
        ///</summary>
        /// <returns> dissolved geometry </returns>
        try {
            /**********************************************************
             * Add adjacent polygon to the TP polygon                 *
             * Merge the polygons and return merged dissolved geometry*
             **********************************************************/
            var oldPoly = EDR.WEBGEOCODER.polygonHandler.polygon;
            // check if an existing TP polygon exists
            if (oldPoly == null) {
                EDR.WEBGEOCODER.log('mergeAndGetDissovedGeometry(): Unable to find old poly for merging to adjacent poly');
                return;
            }
            // get polygon handler
            var curPoly = EDR.WEBGEOCODER.getGooglePlygonFromShapeWKT(shapeWktPolygon);
            if (curPoly == null) {
                EDR.WEBGEOCODER.log('mergeAndGetDissovedGeometry(): Unable to find new poly for merging');
                return;
            }

            /* ***Lets merge**** */
            // step1. Instantiate Wicket
            var wicket = new Wkt.Wkt();
            wicket.fromObject(oldPoly);  //get the old
            var wktOld = wicket.write();    //read the old polygon into a WKT object
            wicket.fromObject(curPoly);  // repeat with new poly, creating a second WKT object
            var wktNew = wicket.write();

            // Step2. Instantiate JSTS WKTReader and get two JSTS geometry objects
            var wktReader = new jsts.io.WKTReader();
            var geomOld = wktReader.read(wktOld);
            var geomNew = wktReader.read(wktNew);

            /**************** Buffer the 2nd polygon before merging ****************************************/
            /*//{Geometry}.buffer(distance, quadrantSegments, endCapStyle)                                 */
            /*//Parameters:                                                                                */
            /*//  distance {number} - the width of the buffer (may be positive, negative or 0).            */
            /*//        The distance unit is the same unit as your coordinates                             */
            /*//  quadrantSegments {number} optional - The quadrantSegments argument allows controlling    */
            /*//      the accuracy of the approximation by specifying the number of line segments          */
            /*//      used to represent a quadrant of a circle.                                            */
            /*//  endCapStyle {number} optional - the end cap style to use. The end cap style specifies    */
            /*//      the buffer geometry that will be created at the ends of line strings.                */
            /*//      BufferOp.CAP_ROUND - (default) a semi-circle                                         */
            /*//Example: var bufferGeomNew = geomNew.buffer(0.000005);                                     */
            /***********************************************************************************************/
            //alert(jsts.operation.distance.DistanceOp.distance(geomOld, geomNew));
            //endCapStyle 1-cap_round, 2-cap_flat, 3-cap_square
            //var bufferGeomNew = geomNew.buffer(EDR.WEBGEOCODER.bufferPolygonByDistance, 1, 0); //(distance, quadrantSegments, endCapStyle) - buffer by distance in unit width (same unit as your coordinates)
            var bufferGeomNew = geomNew.buffer(EDR.WEBGEOCODER.bufferPolygonByDistance, -1, 1); //(distance, quadrantSegments, endCapStyle) - buffer by distance in unit width (same unit as your coordinates)
            //var bufferParams = new jsts.operation.buffer.BufferParameters(18, jsts.operation.buffer.BufferParameters.CAP_ROUND, jsts.operation.buffer.BufferParameters.JOIN_ROUND, jsts.operation.buffer.BufferParameters.DEFAULT_MITRE_LIMIT);

            //Buffer the original TP polygon while merging it the first time.            
            if (EDR.WEBGEOCODER.tpParcel != null) {
                if ((EDR.WEBGEOCODER.mergedParcelArray.length <= 1) && (EDR.WEBGEOCODER.tpParcel.parcelID > 0)) {
                    geomOld = geomOld.buffer(EDR.WEBGEOCODER.bufferPolygonByDistance, -1, 1); //(distance, quadrantSegments, endCapStyle) - buffer by distance in unit width (same unit as your coordinates)               
                }
            }

            var dissolvedGeometry = geomOld.union(bufferGeomNew); //dissolvedGeometry.normalize();  
            dissolvedGeometry.holes = [];
            //simplify the geometry - jsts.simplify.DouglasPeuckerSimplifier.simplify(dissolvedGeometry, ToleranceDistance);
            dissolvedGeometry = jsts.simplify.DouglasPeuckerSimplifier.simplify(dissolvedGeometry, EDR.WEBGEOCODER.simplifyPolygonToleranceDistance);

            return dissolvedGeometry;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('mergeAndGetDissovedGeometry(): ' + e.message);
            return null;
        }
    },

    parcelIsInsideThePolygon: function (polygonOne, shapeWktPolygon) {
        /// <summary> (1). Parses the shapeWKT polygon to a list of polygon coordinates 
        ///           (2). checks each of the coordinates whether its within the polygonOne 
        ///</summary>
        /// <returns> true/false </returns>
        try {
            // validate
            polygonTwo = EDRV2.trim(shapeWktPolygon);
            if (polygonTwo === '') { return ''; }

            // step 1: get individual polygons
            EDR.WEBGEOCODER.log('SHAPEWKT: ' + polygonTwo);
            var wktPattern = /\(([^()]+)\)/g;
            var wktPolygons = new Array();
            var matchVal;
            while (matchVal = wktPattern.exec(polygonTwo)) {
                wktPolygons.push(matchVal[1]);
            }

            //EDR.WEBGEOCODER.log('SHAPEWKT Polygon Count: ' + wktPolygons.length);

            // step 2: loop through each, and parse the coordinates
            var rawCoords;
            var coords;
            var curCoord = null;
            var lat, lng;
            var rawCoord;
            var polygonCoords = new Array();
            for (var j = 0; j < wktPolygons.length; j++) {
                // get current polygon coordinates
                var rawCoords = wktPolygons[j].split(',');
                coords = new Array();

                for (var i = 0; i < rawCoords.length; i++) {
                    curCoord = EDRV2.trim(rawCoords[i]);

                    // split the coordinate by ' ' to get the lat long

                    rawCoord = curCoord.split(' ');
                    lng = EDRV2.trim(rawCoord[0]);
                    lat = EDRV2.trim(rawCoord[1]);

                    if ((lat === '') || (lng === '')) {
                        throw new Error('Found an invalid coordinate');
                        return false;
                    }
                    /*
                        containsLocation(point:LatLng, polygon:Polygon)	retruns boolean	- Computes whether the given point lies inside the specified polygon.
                        isLocationOnEdge(point:LatLng, poly:Polygon|Polyline, tolerance?:number)	returns boolean	- Computes whether the given point lies on or near to a polyline, or the edge of a polygon, within a specified tolerance. Returns true when the difference between the latitude and longitude of the supplied point, and the closest point on the edge, is less than the tolerance. The tolerance defaults to 10-9 degrees.
                    */
                    //Find whether all coordinates of the polygonTwo is within the polygonOne
                    var coordInsidePolygon = google.maps.geometry.poly.containsLocation(new google.maps.LatLng(parseFloat(lat), parseFloat(lng)), polygonOne);
                    //var coordOnEdgeOfPolygon = google.maps.geometry.poly.isLocationOnEdge(new google.maps.LatLng(parseFloat(lat), parseFloat(lng)), polygonOne, EDR.WEBGEOCODER.bufferPolygonByDistance); //tolerance 0.00005 degrees
                    //if (coordInsidePolygon == false && coordOnEdgeOfPolygon == false) {	

                    if (coordInsidePolygon == false) {
                        return false;
                    }
                }
            }
            return true;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('parcelIsInsideThePolygon(): ' + e.message);
            return false;
        }
    },

    parseParcelPolygonToCoordinates: function (strPolygon) {
        /// <summary> 
        ///     Parses the shapeWKT polygon to a list of polygon coordinates 
        /// </summary>
        /// <returns> Returns a list of polygon coordinates.  The coordinates are an array of JSON { latitude, longitude } object </returns>
        try {
            // validate
            strPolygon = EDRV2.trim(strPolygon);
            if (strPolygon === '') { return ''; }

            // step 1: get individual polygons
            EDR.WEBGEOCODER.log('SHAPEWKT: ' + strPolygon);
            var wktPattern = /\(([^()]+)\)/g;
            var wktPolygons = new Array();
            var matchVal;
            while (matchVal = wktPattern.exec(strPolygon)) {
                wktPolygons.push(matchVal[1]);
            }

            EDR.WEBGEOCODER.log('SHAPEWKT Polygon Count: ' + wktPolygons.length);

            // step 2: loop through each polygon, and parse the coordinates
            var rawCoords;
            var coords;
            var curCoord = null;
            var lat, lng;
            var rawCoord;
            var polygonCoords = new Array();
            for (var j = 0; j < wktPolygons.length; j++) {
                // get current polygon coordinates
                var rawCoords = wktPolygons[j].split(',');
                coords = new Array();

                for (var i = 0; i < rawCoords.length; i++) {
                    curCoord = EDRV2.trim(rawCoords[i]);

                    // split the currect coordinate by ' ' to get the lat long
                    rawCoord = curCoord.split(' ');
                    lng = EDRV2.trim(rawCoord[0]);
                    lat = EDRV2.trim(rawCoord[1]);

                    if ((lat === '') || (lng === '')) {
                        throw new Error('Found an invalid coordinate');
                    }

                    coords.push({ latitude: parseFloat(lat), longitude: parseFloat(lng) });
                }

                // add the coordinates to the polygon
                polygonCoords.push(coords);
            }

            EDR.WEBGEOCODER.log('DVG COORDS: ' + JSON.stringify(coords));

            return polygonCoords;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('parseParcelPolygonToCoordinates(): ' + e.message);
        }
    },

    parseParcelPolygonToDVGCoordinates: function (parcelData) {
        /// <summary> Parses the shapeWKT polygon to DVG string coordinates </summary>
        try {
            // validate
            if ((typeof (parcelData) == 'undefined') || (parcelData == null)) { throw new Error('Missing parcel data'); }
            if ((typeof (parcelData.shapeWKT) == 'undefined') || (EDRV2.trim(parcelData.shapeWKT) == '')) { return ''; }

            var strPolygon = EDRV2.trim(parcelData.shapeWKT);
            if (strPolygon === '') { return ''; }

            // parse the polygon to lat/long coordinates
            var polyCoords = EDR.WEBGEOCODER.parseParcelPolygonToCoordinates(strPolygon);
            if ((polyCoords == null) || (polyCoords.length == 0)) { return ''; }

            // check which polygon coordinates need to be converted to dvg coordinates
            var coords = null;
            if (polyCoords.length > 1) {
                var curPoly;
                var curPolyCoords;

                var mapLatLng = new google.maps.LatLng(EDR.WEBGEOCODER.mapClickCoordinate.latitude, EDR.WEBGEOCODER.mapClickCoordinate.longitude);

                // there are multiple polygon coordinates.  figure out which polygon coordinates belong to.
                for (var i = 0; i < polyCoords.length; i++) {
                    curPolyCoords = polyCoords[i];

                    // convert the current polygon coordinates to google polygon
                    var mapCoords = new Array();
                    for (var j = 0; j < curPolyCoords.length; j++) {
                        mapCoords.push(new google.maps.LatLng(curPolyCoords[j].latitude, curPolyCoords[j].longitude));
                    }
                    curPoly = new google.maps.Polygon({
                        paths: mapCoords
                    });

                    // check if the current map point is within the current polygon
                    if (google.maps.geometry.poly.containsLocation(mapLatLng, curPoly)) {
                        coords = curPolyCoords;
                        break;
                    }
                }

                // check if we found the coordinates
                if (coords == null) { return; }
            }
            else {
                // there is only one set of coordinates.  set these coordinates to be converted
                coords = polyCoords[0];
            }

            return EDR.WEBGEOCODER.parseCoordinatesToDVGCoordinates(coords);
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('parseParcelPolygonToDVGCoordinates(): ' + e.message);
            return '';
        }
    },

    parseCoordinatesToDVGCoordinates: function (coords) {
        /// <summary> 
        ///           PARSE POLY COORDINATES TO DVG COORDINATES
        ///</summary>
        /// <returns> </returns>
        try {
            // validate
            if ((typeof (coords) == 'undefined') || (coords == null) || (coords.length === 0)) { return ''; }

            // loop through the coordinates to convert it into dvg coordiantes string
            var strDVGCoords = '';
            var curCoord;
            for (var i = 0; i < coords.length; i++) {
                curCoord = coords[i];
                strDVGCoords += curCoord.longitude + ',' + curCoord.latitude + '|';
            }

            // trim the last '|'
            strDVGCoords = strDVGCoords.replace(/\|$/, '');

            EDR.WEBGEOCODER.log('DVG COORDS: ' + strDVGCoords);

            return strDVGCoords;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('parseCoordinatesToDVGCoordinates(): ' + e.message);
            return '';
        }
    },

    parseGeoJsonToDVGCoordinates: function (coords) {
        /// <summary> 
        ///           PARSE GEOJSON POLY COORDINATES TO DVG COORDINATES
        ///</summary>
        /// <returns> DVG Polygon Coordinates</returns>
        try {
            // validate
            if ((typeof (coords) == 'undefined') || (coords == null) || (coords.length === 0)) { return ''; }

            // loop through the coordinates to convert it into dvg coordiantes string
            var strDVGCoords = '';
            var curCoord;
            for (var i = 0; i < coords.length; i++) {
                curCoord = coords[i];
                strDVGCoords += curCoord[0] + ',' + curCoord[1] + '|';
            }

            // trim the last '|'
            strDVGCoords = strDVGCoords.replace(/\|$/, '');

            EDR.WEBGEOCODER.log('DVG COORDS: ' + strDVGCoords);

            return strDVGCoords;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('parseGeoJsonToDVGCoordinates(): ' + e.message);
            return '';
        }
    },

    parseGoogleCoordinatesToDVGCoordinates: function (coords) {
        /// <summary> 
        ///           PARSE GOOGLE POLY COORDINATES TO DVG COORDINATES
        ///</summary>
        /// <returns> DVG Polygon Coordinates</returns>
        try {
            // validate
            if ((typeof (coords) == 'undefined') || (coords == null) || (coords.length === 0)) { return ''; }

            // loop through the coordinates to convert it into dvg coordiantes string
            var strDVGCoords = '';
            var curCoord;
            for (var i = 0; i < coords.length; i++) {
                curCoord = coords[i];
                //strDVGCoords += curCoord.F + ',' + curCoord.A + '|';
                strDVGCoords += curCoord.lng() + ',' + curCoord.lat() + '|';
            }

            // trim the last '|'
            strDVGCoords = strDVGCoords.replace(/\|$/, '');

            EDR.WEBGEOCODER.log('DVG COORDS: ' + strDVGCoords);

            return strDVGCoords;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('parseGoogleCoordinatesToDVGCoordinates(): ' + e.message);
            return '';
        }
    },

    buildURL: function (host, path, qryStrs, useDocProtocol) {
        ///<summary> Returns the url for the current environment </summary>
        try {
            // use current location to determine protocol
            //var url = location.protocol + '//' + host + path;
            var url = host + path;

            var lochost = location.host.toLowerCase();
            switch (lochost) {
                case 'www.web.edrnet.com':
                    url = url.replace('ws.edrnet.com', 'www.web.edrnet.com');
                //break;
            }

            var addAmp = true;
            // append ? if needed
            if (url.indexOf('?') === -1) {
                url += '?';
                addAmp = false;
            }


            // build query string
            if (qryStrs instanceof Array) {
                for (var i = 0; i < qryStrs.length; i++) {
                    if (!addAmp) {
                        url += qryStrs[i].key + '=' + encodeURIComponent(qryStrs[i].value);
                        addAmp = true;
                    }
                    else {
                        url += '&' + qryStrs[i].key + '=' + encodeURIComponent(qryStrs[i].value);
                    }
                }

            }

            // done
            return url;
        }
        catch (e) {
            logService.logError(logService.SERVERITIES.ERROR, 'EDR.WEBGEOCODER.buildURL()', e.message);
            throw e;
        }
    },
        
    onPolygonUpdated: function () {
        /// <summary>
        ///           Handles polygon updated event.
        ///</summary>
    
        //Clear any previous errors
        EDR.WEBGEOCODER.clearErrorMessages();

        EDR.WEBGEOCODER.updateAreaUI();

        // validate polygon if exists
        var polyPoints = EDR.WEBGEOCODER.polygonHandler.getPolygonPoints();
        if ((polyPoints != null) && (polyPoints.length > 0)) {
            if (!EDR.WEBGEOCODER.validatePolygonDisplayError(true).isValid) return false;
            // update the polygon end button to edit
            $('#imgStartTool').attr('src', '/global/images/btn_edit_v3.png');
        }
        else {
            // update the polygon start button to draw
            $('#imgStartTool').attr('src', '/global/images/btn_draw_v3.png');
        }
    },
    /***************************************************************************************
    END: Google Map Specific Handlers
    ***************************************************************************************/

    /***************************************************************************************
    START: UI Control Handlers
    ***************************************************************************************/
    showPolygonToolInstructions: function () {
        var elem = $("div#" + 'polyStart');
        if (elem.is(":visible") == true) {
            elem.hide(0, null);
            $("div#" + 'latlong').hide(0, null);
            $("div#" + 'polygon').show(0, null);
            $("div#" + 'latLongButton').css('display', 'none');
        }
    },

    hidePolygonToolInstructions: function () {
        var elem = $("div#" + 'polygon');
        if (elem.is(":visible") == true) {
            elem.hide(0, null);
            $("div#" + 'polyStart').show(0, null);
            $("div#" + 'latlong').show(0, null);
            $("div#" + 'latLongButton').css('display', 'block');
        }
    },

    /*
    Name:	EDR.WEBGEOCODER.setContinueState()
    Desc:	Sets the enabled state of the continue option
    Output:	Adjusts UI controls
    Sample: EDR.WEBGEOCODER.clearErrorMessages();	
    */
    setContinueState: function (enable) {
        try {
            //Get the continue button
            var uiContinueBtn = $("#ibtContinue");

            //Check if we found it
            if (!uiContinueBtn || uiContinueBtn == null) { throw new Error("Continue button could not be referenced"); }

            //Get the image to display
            var imgSrc = "/global/SharedResources/WebOrdering/images/largebutton_continue.png";
            if (!enable) { imgSrc = "/global/SharedResources/WebOrdering/images/largebutton_continue_gray.png"; }
            if (uiContinueBtn.attr('src') != imgSrc) { uiContinueBtn.attr('src', imgSrc); }

            //Adjust the enable state
            //if (enable) { uiContinueBtn.attr('disabled', ''); }
            if (enable) {
                uiContinueBtn.removeAttr('disabled');
            }
            else {
                uiContinueBtn.attr('disabled', 'disabled');
            }
        }
        catch (err) {
            throw new Error("Error setting continue state - " + err.message);
        }
    },
    /*
        Name:	EDR.WEBGEOCODER.setPreviewDataState()
        Desc:	Sets the enabled state of the PreviewData option
        Output:	Adjusts UI controls
        Sample: EDR.WEBGEOCODER.clearErrorMessages();	
        */
    setPreviewDataState: function (enable) {
        try {
            //Get the FlashLight PreviewData button
            var uiPreviewDataState = $("#ibtFlashLightPreviewData");

            //Check if we found it
            if (!uiPreviewDataState || uiPreviewDataState == null) { return }

            //Get the image to display
            var imgSrc = "/global/SharedResources/WebOrdering/images/button_open_report_v3.png";
            if (!enable) { imgSrc = "/global/SharedResources/WebOrdering/images/button_open_report_gray_v3.png"; }
            if (uiPreviewDataState.attr('src') != imgSrc) { uiPreviewDataState.attr('src', imgSrc); }

            //Adjust the enable state
            //if (enable) { uiContinueBtn.attr('disabled', ''); }
            if (enable) {
                uiPreviewDataState.removeAttr('disabled');
            }
            else {
                uiPreviewDataState.attr('disabled', 'disabled');
            }
        }
        catch (err) {
            throw new Error("Error setting Preview Data Button state - " + err.message);
        }
    },
    /*
    Name:	EDR.WEBGEOCODER.isTPWithinMaxMoveDistance()
    Desc:	Function to check tp max move distance
    Output:	Will show error if TP is moved beyond allowed distance from original location
    Sample: EDR.WEBGEOCODER.isTPWithinMaxMoveDistance();	
    */
    isTPWithinMaxMoveDistance: function (currentLatLng) //google maps ll object
    {
        if (EDR.WEBGEOCODER.maxTPMoveDistanceInFeet > 0 && EDR.WEBGEOCODER.originalSourcePropertyLatitude != 0 && EDR.WEBGEOCODER.originalSourcePropertyLongitude != 0) {
            //maxTPMoveDistance has a value, so we need to check it before we wreck it
            var originalLL = new google.maps.LatLng(EDR.WEBGEOCODER.originalSourcePropertyLatitude, EDR.WEBGEOCODER.originalSourcePropertyLongitude);
            var distanceBetweenOriginalAndCurrentInFeet = (Math.abs(google.maps.geometry.spherical.computeDistanceBetween(originalLL, currentLatLng)) * 3.2808399); //converted to feet from meters

            //Perform the comparison
            if (distanceBetweenOriginalAndCurrentInFeet > EDR.WEBGEOCODER.maxTPMoveDistanceInFeet) {
                EDR.WEBGEOCODER.setErrorMessages("Invalid operation", "Cannot move property more than " + EDR.WEBGEOCODER.maxTPMoveDistanceInFeet + "ft from current location");
                return false;
            }
        }
        return true;
    },

    /*
    Name:	EDR.WEBGEOCODER.clearErrorMessages()
    Desc:	Function to clear error messages
    Output:	Will clear error UI 
    Sample: EDR.WEBGEOCODER.clearErrorMessages();	
    */
    clearErrorMessages: function () {
        //Forward the call
        EDR.WEBGEOCODER.setErrorMessages();

        // also clear error code
        var uiErrLblCode = $("#_EDRErrCode");
        uiErrLblCode.text(''); //Always clear the code since we will never have a code from javascript
        uiErrLblCode.hide(0, null);
    },

    /*
    Name:	EDR.WEBGEOCODER.setErrorMessages()
    Desc:	Function to set or clear error messages
    Output:	Will adjust error UI based on the input error message data 
    Sample: EDR.WEBGEOCODER.setErrorMessages("", "");
    Sample: var error = ["Error number 1", "Error number 2", "Error number 3"];
    EDR.WEBGEOCODER.setErrorMessages("Error Detected", error);
    Sample: var error = "Error string - not an array";
    EDR.WEBGEOCODER.setErrorMessages("Error Detected", error);
    */
    setErrorMessages: function (errorHeadingMessage, errorMessages) {
        try {
            //Preconditions
            if (!errorHeadingMessage || errorHeadingMessage == null) { errorHeadingMessage = ""; } //No error heading, so set it to empty string
            if (!errorMessages || errorMessages == null) { errorMessages = []; } //No error message passed in so just declare an empty array
            if ((errorMessages instanceof Array) == false) { errorMessages = new Array(errorMessages); } //Test for the variable being an array, if not then it is just a simple single string - so let's accept that as valid

            //Set the error message string
            var errorMsgDisplay = "";
            if (errorHeadingMessage != "") { errorMsgDisplay = errorHeadingMessage; }

            if (errorMessages.length > 0) {
                errorMsgDisplay += '<ul style=\'color: black; margin-left: -20px;\'>';

                for (var i = 0; i < errorMessages.length; i++) {
                    if (errorMessages[i] != "") { errorMsgDisplay += "<li>" + errorMessages[i] + '</li>'; }
                }

                errorMsgDisplay += '</ul>';
            }

            //Get our UI controls
            var uiErrDiv = $("div#" + "_ErrorMessagePanel");
            var uiErrLbl = $("#lblErrorMessage");

            //Check to make sure our elements are found
            var errElementsFound = true;
            if (!uiErrDiv || uiErrDiv == null) { errElementsFound = false; }
            if (!uiErrLbl || uiErrLbl == null) { errElementsFound = false; }

            //Adjust the continue button
            EDR.WEBGEOCODER.setContinueState((errorMsgDisplay == ""));
            EDR.WEBGEOCODER.setPreviewDataState((errorMsgDisplay == ""));

            //If elements are not found, then we cannot display the error message, so just alert it instead
            if (errElementsFound == false) {
                if (errorMsgDisplay != "") { alert(errorMsgDisplay); }
                return;
            }

            //Adjust UI elements based on the error data passed in
            if (errorMsgDisplay != "") {
                uiErrLbl.html(errorMsgDisplay);
                uiErrDiv.show(0, null);
            }
            else {
                uiErrLbl.html('');
                uiErrDiv.hide(0, null);
            }
        }
        catch (err) {
            //Could not display the error so alert it out
            alert('Unable to show error: ' + err.message);
            EDR.WEBGEOCODER.setContinueState(false); //Adjust the continue button to be disabled
            EDR.WEBGEOCODER.setPreviewDataState(false); // Change PreviewData button to be disabled
        }
    },

    //Sets the current address shown in the UI
    setAddress: function (addressInfo) {
        //If we don't have addressInfo then create an empty one
        if (!addressInfo) { addressInfo = { "SiteName": "", "Address": "", "City": "", "State": "", "ZipCode": "" }; }

        //Set address values in the UI
        $("#SiteName_TXT").val(addressInfo.SiteName);
        $("#Address_TXT").val(addressInfo.Address);
        $("#City_TXT").val(addressInfo.City);
        if (addressInfo.State == "") { $("#State_DDL").attr('selectedIndex', 0); } //Set to the first item in the list (since there is no clear)
        else { $("#State_DDL").val(addressInfo.State); }
        $("#ZipCode_TXT").val(addressInfo.ZipCode);
    },

    //Retrieves the current address as it is shown in the UI
    getAddress: function () {
        //Pull all the address values
        var addressInfo = {
            "SiteName": EDR.Trim($("#SiteName_TXT").val()),
            "Address": EDR.Trim($("#Address_TXT").val()),
            "City": EDR.Trim($("#City_TXT").val()),
            "State": EDR.Trim($("#State_DDL").val()),
            "ZipCode": EDR.Trim($("#ZipCode_TXT").val())
        };

        //Now return the info
        return addressInfo;
    },

    /***************************************************************************************
    END: UI Control Handlers
    ***************************************************************************************/

    /***************************************************************************************
    START: Address Geocoding Handlers
    ***************************************************************************************/
    /*
    geocodeAddress()
 
    Handles background geocode process when SEARCH button is clicked on.
    */
    executeGeocodeAddress: function (reZoomTPToCenter) {
        try {
            //Clear any previous errors
            EDR.WEBGEOCODER.clearErrorMessages();

            // close the parcel info window if open
            if (EDR.WEBGEOCODER.parcelInfoWindow != null) {
                EDR.WEBGEOCODER.parcelInfoWindow.remove();
            }

            // hide candidates list
            EDR.DOM.ShowHide('_CandidatesListFrame', false);

            // remove current marker and reset tpMarker for polygon handler
            EDR.EDRMapV2Google.RemoveTPMarker();
            EDR.WEBGEOCODER.polygonHandler.tpMarker = null;

            // get data
            var handlerURL = EDR.WEBGEOCODER.handlerURL;
            var geoGUID = EDR.WEBGEOCODER.webGeocoderSessionGUID;
            var sourcePropGUID = EDR.WEBGEOCODER.sourcePropertyGUID;
            var latlonCtrlInfo = EDR.WEBGEOCODER.latitudeLongitudeControl;

            // determine action type
            var actionType = 'SPGEOCODE';

            // get address information
            var addressInfo = EDR.WEBGEOCODER.getAddress();
            if (addressInfo != null) {
                actionType = 'SPGEOCODEADDRESS';

                // enforce known validation here
                addressInfo.SiteName = EDR.Trim(addressInfo.SiteName);
                addressInfo.Address = EDR.Trim(addressInfo.Address);
                addressInfo.City = EDR.Trim(addressInfo.City);
                addressInfo.State = EDR.Trim(addressInfo.State);
                addressInfo.ZipCode = EDR.Trim(addressInfo.ZipCode);

                if (addressInfo.Address == '') throw new Error('Address is required.');
                if ((addressInfo.City == '') && (addressInfo.State == '') && (addressInfo.ZipCode == '')) throw new Error('Either City, State, or ZipCode is required.');
            }

            // build request data
            var data = 'TYPE=' + actionType;

            data += '&geoguid=' + encodeURIComponent(geoGUID);
            data += '&wgspguid=' + encodeURIComponent(sourcePropGUID);

            if (addressInfo != null) {
                data += '&sitename=' + encodeURIComponent(addressInfo.SiteName);
                data += '&address=' + encodeURIComponent(addressInfo.Address);
                data += '&city=' + encodeURIComponent(addressInfo.City);
                data += '&state=' + encodeURIComponent(addressInfo.State);
                data += '&zipcode=' + encodeURIComponent(addressInfo.ZipCode);
            }

            // post data
            var xmlDoc = EDR.XML.XMLDocumentFromHTTPPost(handlerURL, data, 'application/x-www-form-urlencoded');
            if (xmlDoc == null) return false;

            // parse data
            var result = new EDR.EDRMapV2.GeocodeResult();
            result.LoadFromXML($(xmlDoc));

            // delegate to process this data
            EDR.WEBGEOCODER.processGeocodeResult(result, addressInfo, reZoomTPToCenter);
        }
        catch (err) {
            //alert('Unable to geocode address: ' + err.message);
            EDR.WEBGEOCODER.setErrorMessages("Unable to locate your property", [err.message, 'Please try again']);
        }

        // hide please wait window
        __pleaseWait.hide();

        return false;
    },

    /*
    Name:	EDR.WEBGEOCODER.executeReverseGeocode()
    Desc:	Function to reverse geocode a lat / long
    Output:	Reverse geocodes and adjusts the UI with the returned values
    */
    executeReverseGeocode: function (reZoomTPToCenter, dontRePositionTPMarker, triggerParcelByCoordinate) {
        try {
            //Clear any previous errors
            EDR.WEBGEOCODER.clearErrorMessages();

            // close the parcel info window if open
            if (EDR.WEBGEOCODER.parcelInfoWindow != null) {
                EDR.WEBGEOCODER.parcelInfoWindow.remove();
            }

            // hide candidates list
            EDR.DOM.ShowHide('_CandidatesListFrame', false);

            // get data
            var handlerURL = EDR.WEBGEOCODER.handlerURL;
            var wgSessGUID = EDR.WEBGEOCODER.webGeocoderSessionGUID;
            var sourcePropGUID = EDR.WEBGEOCODER.sourcePropertyGUID;
            var latLongControlIDs = EDR.WEBGEOCODER.latitudeLongitudeControl;

            //Preconditions
            if (!latLongControlIDs) { throw new Error("Latitude and Longitude information is required"); }

            //Get the coordinates and validate
            var coords = EDR.CONTROLS.LATITUDELONGITUDE.GetCoordinates(latLongControlIDs)
            //var coords = {Latitude: 41.24579, Longitude: -73.074984}
            if (coords.Latitude == 0.0) { throw new Error("Latitude was not specified but is required"); }
            if (coords.Longitude == 0.0) { throw new Error("Longitude was not specified but is required"); }

            //Check for max move distance compliance
            if (EDR.WEBGEOCODER.isTPWithinMaxMoveDistance(new google.maps.LatLng(coords.Latitude, coords.Longitude)) == false) {
                //Reset lat and lng UI to original, hide the please wait message, and exit
                var resCoorInfo = { LatitudeHiddenID: latLongControlIDs.LatitudeHiddenID, LongitudeHiddenID: latLongControlIDs.LongitudeHiddenID, Latitude: EDR.WEBGEOCODER.originalSourcePropertyLatitude, Longitude: EDR.WEBGEOCODER.originalSourcePropertyLongitude };
                EDR.CONTROLS.LATITUDELONGITUDE.SetCoordinates(resCoorInfo);
                __pleaseWait.hide();
                return false; //Exit immediately
            }

            // remove current marker and reset tpMarker for polygon handler
            //EDR.EDRMapV2Google.RemoveTPMarker();
            EDR.WEBGEOCODER.polygonHandler.tpMarker = null;

            //Declare and set our work variables
            var postData = 'TYPE=SPREVGEOCODE';
            postData += '&geoguid=' + encodeURIComponent(wgSessGUID);
            postData += '&wgspguid=' + encodeURIComponent(sourcePropGUID);
            postData += '&lat=' + encodeURIComponent(coords.Latitude);
            postData += '&lng=' + encodeURIComponent(coords.Longitude);

            // check if the PARCEL data needs to be displayed
            if (typeof (triggerParcelByCoordinate) != 'boolean') { triggerParcelByCoordinate = true; }
            if ((triggerParcelByCoordinate) && (EDR.EDRMapV2Google.hasOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName))) {
                // check if the current zoom level
                if (map.zoom >= EDR.WEBGEOCODER.minParcelZoomLevel) {
                    var data = { extentInMeteres: 1, latitude: coords.Latitude, longitude: coords.Longitude, detailLevel: 15 };

                    // get the parcel details
                    EDR.WEBGEOCODER.getParcelByCoordinate(data);
                }
            }

            //Post the data
            var xmlDoc = EDR.XML.XMLDocumentFromHTTPPost(handlerURL, postData, 'application/x-www-form-urlencoded');
            if (xmlDoc == null) { return false; } //Exit since we have no results

            //Load up the result
            var objRevGeoResult = new EDR.EDRMapV2.ReverseGeocodeResult();
            objRevGeoResult.LoadFromXML($(xmlDoc));

            //Check the status of the reverse geocode execution
            if (objRevGeoResult.ReverseGeocodeStatus != objRevGeoResult.EnumReverseGeocodeStatus.SUCCESSFULL) { throw new Error("Reverse geocode operation was not successful: " + objRevGeoResult.ErrorMessage); }

            //Get the current address, update the city, state, zip, and then update the UI with the new values 
            var currentAddressInfo = EDR.WEBGEOCODER.getAddress();
            currentAddressInfo.City = objRevGeoResult.City;
            currentAddressInfo.State = objRevGeoResult.State;
            currentAddressInfo.ZipCode = objRevGeoResult.ZipCode;
            EDR.WEBGEOCODER.setAddress(currentAddressInfo);

            // determine if we need to re-position tp marker 
            // default behavior is False (TP marker will be repositioned) except when called by onTPMarkerMoved
            if ((typeof (dontRePositionTPMarker) == 'undefined') || (dontRePositionTPMarker == null)) dontRePositionTPMarker = false;

            // default to rezoom TP and auto-center
            if (!dontRePositionTPMarker) {
                if ((typeof (reZoomTPToCenter) != 'undefined') && (reZoomTPToCenter != null)) {
                    EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(coords.Latitude, coords.Longitude), base.TPMarker, reZoomTPToCenter);
                }
                else {
                    EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(coords.Latitude, coords.Longitude), base.TPMarker, true);
                }
            }

            //Now update the map
            EDR.WEBGEOCODER.polygonHandler.tpMarker = tpMarker;

            // error if location is out of boundary
            if ((objRevGeoResult.City == '') || (objRevGeoResult.ZipCode == '')) {
                throw new Error('Property is outside of EDR coverage area.');
            }

            // check if TP in polygon
            EDR.WEBGEOCODER.validatePolygonDisplayError(true);

        }
        catch (err) {
            //alert('Unable to reverse geocode address: ' + err.message);
            EDR.WEBGEOCODER.setErrorMessages("Unable to locate your property", [err.message, 'Please try again']);
        }

        __pleaseWait.hide();
        return false;
    },

    /*
    executeGeocodeCandidate()
 
    Set source property to the selected candidate.
    */
    executeGeocodeCandidate: function (candidateInfo, reZoomTPToCenter) {
        if (candidateInfo == null) return false;

        try {
            //Clear any previous errors
            EDR.WEBGEOCODER.clearErrorMessages()

            // get data
            var handlerURL = EDR.WEBGEOCODER.handlerURL;
            var geoGUID = EDR.WEBGEOCODER.webGeocoderSessionGUID;
            var sourcePropGUID = EDR.WEBGEOCODER.sourcePropertyGUID;
            var latlonCtrlInfo = EDR.WEBGEOCODER.latitudeLongitudeControl;

            // hide candidates list
            EDR.DOM.ShowHide('_CandidatesListFrame', false);

            // remove current marker and reset tpMarker for polygon handler
            EDR.EDRMapV2Google.RemoveTPMarker();
            EDR.WEBGEOCODER.polygonHandler.tpMarker = null;

            // get the address information and replace data
            var addressInfo = EDR.WEBGEOCODER.getAddress();
            if ((candidateInfo.Address) && (candidateInfo.Address != '')) addressInfo.Address = candidateInfo.Address;
            addressInfo.City = candidateInfo.City;
            addressInfo.State = candidateInfo.State;
            addressInfo.ZipCode = candidateInfo.ZipCode;

            if (!addressInfo.SiteName) addressInfo.SiteName = '';
            if (!addressInfo.Address) addressInfo.Address = '';
            if (!addressInfo.City) addressInfo.City = '';
            if (!addressInfo.State) addressInfo.State = '';
            if (!addressInfo.ZipCode) addressInfo.ZipCode = '';

            // get coordinates
            var coorInfo = { LatitudeHiddenID: latlonCtrlInfo.LatitudeHiddenID, LongitudeHiddenID: latlonCtrlInfo.LongitudeHiddenID, Latitude: candidateInfo.Latitude, Longitude: candidateInfo.Longitude };

            // set address and coordinate information
            EDR.WEBGEOCODER.setAddress(addressInfo);
            EDR.CONTROLS.LATITUDELONGITUDE.SetCoordinates(coorInfo);

            // determine action type
            var actionType = 'SPGEOCODECANDIDATE';

            // build request data
            var data = 'TYPE=' + actionType;

            data += '&geoguid=' + encodeURIComponent(geoGUID);
            data += '&wgspguid=' + encodeURIComponent(sourcePropGUID);
            data += '&sitename=' + encodeURIComponent(addressInfo.SiteName);
            data += '&address=' + encodeURIComponent(addressInfo.Address);
            data += '&city=' + encodeURIComponent(addressInfo.City);
            data += '&state=' + encodeURIComponent(addressInfo.State);
            data += '&zipcode=' + encodeURIComponent(addressInfo.ZipCode);
            data += '&lat=' + candidateInfo.Latitude;
            data += '&lon=' + candidateInfo.Longitude;

            // post data
            var xmlDoc = EDR.XML.XMLDocumentFromHTTPPost(handlerURL, data, 'application/x-www-form-urlencoded');
            if (xmlDoc == null) return false;

            // parse data
            var result = new EDR.EDRMapV2.GeocodeResult();
            result.LoadFromXML($(xmlDoc));

            // delegate to process this data
            EDR.WEBGEOCODER.processGeocodeResult(result, addressInfo, reZoomTPToCenter);
        }
        catch (err) {
            //alert('Unable to geocode selected candidate: ' + err.message);
            EDR.WEBGEOCODER.setErrorMessages("Unable to locate your property", [err.message, 'Please try again']);
        }

        return false;
    },

    /*
    processGeocodeResult()
 
    Process the geocode result and update the UI as neccessary.
    */
    processGeocodeResult: function (result, addressInfo, reZoomTPToCenter) {
        console.log("Zoom processGeocodeResult ");
        try {
            // lat/lon control info
            var latlonCtrlInfo = EDR.WEBGEOCODER.latitudeLongitudeControl;
            var addZoomLevel = 0;

            // json for address and coordinate information
            var resAddressInfo = { SiteName: '', Address: '', City: '', State: '', ZipCode: '' };
            var resCoorInfo = { LatitudeHiddenID: latlonCtrlInfo.LatitudeHiddenID, LongitudeHiddenID: latlonCtrlInfo.LongitudeHiddenID, Latitude: 0.0, Longitude: 0.0 };

            // use address information from UI to ensure data integrity
            if (addressInfo != null) resAddressInfo = addressInfo;

            var startTime = new Date();

            // check status
            var hasCandidate = false;
            switch (result.GeocodeStatus) {
                case result.EnumGeocodeStatus.EXACTMATCH:
                    if (resAddressInfo.City == '') resAddressInfo.City = result.ExactMatch.City;
                    resAddressInfo.State = result.ExactMatch.State;
                    if (resAddressInfo.ZipCode == '') resAddressInfo.ZipCode = result.ExactMatch.ZipCode;

                    resCoorInfo.Latitude = result.ExactMatch.Latitude;
                    resCoorInfo.Longitude = result.ExactMatch.Longitude;

                    // check if the PARCEL data needs to be displayed
                    if (EDR.EDRMapV2Google.hasOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName)) {
                        // check if the current zoom level
                        if (map.zoom >= EDR.WEBGEOCODER.minParcelZoomLevel) {
                            var data = { extentInMeteres: 1, latitude: resCoorInfo.Latitude, longitude: resCoorInfo.Longitude, detailLevel: 15 };

                            // get the parcel details
                            EDR.WEBGEOCODER.getParcelByCoordinate(data);
                        }
                    }

                    break;

                case result.EnumGeocodeStatus.ADDRESSCANDIDATES:
                    // for now don't do anything since we need to display this on a DIV
                    resAddressInfo = null;

                    // because of candidate - reset coordinates
                    resCoorInfo.Latitude = 0.0;
                    resCoorInfo.Longitude = 0.0;

                    // display candidates list
                    if (result.CandidatesListHTML != '') hasCandidate = true;
                    document.getElementById('_CandidatesListContainer').innerHTML = result.CandidatesListHTML;
                    EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_UIException, 'WebGeocoderV3 UI Unable to locate property returned address candidates');
                    break;

                case result.EnumGeocodeStatus.LASTLINECANDIDATES:
                    // for now don't do anythign since we need to display this on a DIV
                    resAddressInfo = null;

                    // because of candidate - reset coordinates
                    resCoorInfo.Latitude = 0.0;
                    resCoorInfo.Longitude = 0.0;
                    //add 5 more zoom level to the default zoom level for lastline
                    addZoomLevel = 3;
                    // display candidates list
                    if (result.CandidatesListHTML != '') hasCandidate = true;
                    document.getElementById('_CandidatesListContainer').innerHTML = result.CandidatesListHTML;
                    EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_UIException, 'WebGeocoderV3 UI Unable to locate property returned last line candidates');
                    break;

                case result.EnumGeocodeStatus.ERROR:
                    resAddressInfo = null;
                    resCoorInfo = null;

                    throw new Error('WebGecoder service handler returned error: ' + result.ErrorMessage);
                    break;

                case result.EnumGeocodeStatus.NONE:
                    resAddressInfo = null;
                    resCoorInfo = null;

                    throw new Error('WebGecoder service handler did not return any data');
                    break;
            }

            //Check for max move distance compliance
            if (resCoorInfo != null && resCoorInfo.Latitude != 0.0 && resCoorInfo.Longitude != 0.0 && EDR.WEBGEOCODER.isTPWithinMaxMoveDistance(new google.maps.LatLng(resCoorInfo.Latitude, resCoorInfo.Longitude)) == false) {
                //Reset lat and lng UI to original
                var resCoorInfo = { LatitudeHiddenID: latlonCtrlInfo.LatitudeHiddenID, LongitudeHiddenID: latlonCtrlInfo.LongitudeHiddenID, Latitude: EDR.WEBGEOCODER.originalSourcePropertyLatitude, Longitude: EDR.WEBGEOCODER.originalSourcePropertyLongitude };
                EDR.CONTROLS.LATITUDELONGITUDE.SetCoordinates(resCoorInfo);

                //Reset the tp marker and reset the polygon handler
                EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(resCoorInfo.Latitude, resCoorInfo.Longitude), base.TPMarker, true);
                EDR.WEBGEOCODER.polygonHandler.tpMarker = tpMarker;

                // check if TP in polygon
                EDR.WEBGEOCODER.validatePolygonDisplayError(false);

                //Hide the wait message and exit immediately
                __pleaseWait.hide();
                return false; //Exit immediately
            }

            // upate the UI if the result objects is not null
            if (resAddressInfo != null) EDR.WEBGEOCODER.setAddress(resAddressInfo);

            // if coordinate is not null but not set to lat/lon use the default state mapping
            if ((hasCandidate == false) && ((resCoorInfo == null) || (resCoorInfo.Latitude == 0.0) || (resCoorInfo.Longitude == 0.0))) {
                // use state default map settings since it is not exactmatch and candidate list is not available
                var addressInfo = EDR.WEBGEOCODER.getAddress();
                var def = EDR.WEBGEOCODER.stateDefaultMappingOptions[addressInfo.State.toUpperCase()];

                EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(def.centerLatitude, def.centerLongitude), base.TPMarker, true);
                map.setZoom(def.zoomLevel + addZoomLevel);
                // check if TP in polygon
                EDR.WEBGEOCODER.validatePolygonDisplayError(false);

                // dsplay message
                EDR.WEBGEOCODER.setErrorMessages('Unable to locate your property', 'Please verify your property location');
            }
            else if ((resCoorInfo != null) && (resCoorInfo.Latitude != 0.0) && (resCoorInfo.Longitude != 0.0)) {
                // default to rezoom TP and auto-center
                if ((typeof (reZoomTPToCenter) != 'undefined') && (reZoomTPToCenter != null)) {
                    EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(resCoorInfo.Latitude, resCoorInfo.Longitude), base.TPMarker, reZoomTPToCenter);
                }
                else {
                    EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(resCoorInfo.Latitude, resCoorInfo.Longitude), base.TPMarker, true);
                }

                // set polygon tp marker
                EDR.CONTROLS.LATITUDELONGITUDE.SetCoordinates(resCoorInfo);
                EDR.WEBGEOCODER.polygonHandler.tpMarker = tpMarker;

                // check if TP in polygon
                EDR.WEBGEOCODER.validatePolygonDisplayError(false);
            }

            // hide please wait
            __pleaseWait.hide();
        }
        catch (err) {
            throw err;
        }
    },

    /*
    closeCandidatesListWithOutSelection()
 
    Closes candidates list window without selecting an item.
 
    centerMapCoors: { Latitude: 0.0, Longitude: 0.0 }
    */
    closeCandidatesListWithOutSelection: function (centerMapCoors) {
        //Clear any previous errors
        EDR.WEBGEOCODER.clearErrorMessages()

        // close candidates window
        EDR.DOM.ShowHide('_CandidatesListFrame', false);

        // set tp marker
        EDR.EDRMapV2Google.RemoveTPMarker();
        EDR.WEBGEOCODER.polygonHandler.tpMarker = null;

        // display message
        var errHeader = 'Unable to locate your property';
        var errMessage = '';

        var zoomLevel = 0;

        // default to PT zoom level
        if ((centerMapCoors.Latitude == 0.0) || (centerMapCoors.Latitude == 0.0)) {
            // use state default map settings
            var addressInfo = EDR.WEBGEOCODER.getAddress();
            var def = EDR.WEBGEOCODER.stateDefaultMappingOptions[addressInfo.State.toUpperCase()];

            if (def != null) {
                centerMapCoors.Latitude = def.centerLatitude;
                centerMapCoors.Longitude = def.centerLongitude;
                zoomLevel = def.zoomLevel;
            }

            errMessage = 'Please verify your property location';
        }
        else {
            errMessage = 'Please verify your property location';
        }

        // sets polygon tp marker
        var newTPMarker = EDR.EDRMapV2Google.SetTPMarker(map, new google.maps.LatLng(centerMapCoors.Latitude, centerMapCoors.Longitude), base.TPMarker, true);
        if (zoomLevel != 0) map.setZoom(zoomLevel);

        EDR.WEBGEOCODER.polygonHandler.tpMarker = newTPMarker;

        // trigger marker moved
        EDR.WEBGEOCODER.onTPMarkerMoved(newTPMarker, false, errHeader, errMessage);
    },
    /***************************************************************************************
    END: Address Geocoding Handlers
    ***************************************************************************************/

    /***************************************************************************************
    START: Polygon Handlers
    ***************************************************************************************/
    /*
    Name:	EDR.WEBGEOCODER.initializePolygon()
    Desc:	Initializes (draws) a polygon with points on the map
    Output:	Shows the polygon on the map if a valid poly coordinate string is supplied
    */
    initializePolygon: function (polyCoordString) {
        try {
            EDR.WEBGEOCODER.clearErrorMessages() //Clear any previous errors

            // check if the tp polygon exists
            if (polyCoordString != '') {
                EDR.WEBGEOCODER.polygonHandler.polygonOptions.autoEditPolygon = EDR.WEBGEOCODER.autoEditPolygon;
                EDR.WEBGEOCODER.polygonHandler.setPolygonDVGCoordinates(polyCoordString);
            }

            // check if the tax map option is included
            if (EDR.WEBGEOCODER.showTaxMapControl) {
                // treat it as if it were a normal map click
                // check if the current zoom level
                if (map.zoom < EDR.WEBGEOCODER.minParcelZoomLevel) { return; }

                // get the center of map
                var tpMarker = EDR.WEBGEOCODER.polygonHandler.tpMarker;
                var data = { extentInMeteres: 1, latitude: tpMarker.position.lat(), longitude: tpMarker.position.lng(), detailLevel: 15 };

                // get the parcel details
                EDR.WEBGEOCODER.getParcelByCoordinate(data);
            }
        }
        catch (err) {
            //alert('Unable to initialize polygon: ' + err.message);
            EDR.WEBGEOCODER.setErrorMessages("Unable to initialize property polygon", [err.message, 'Please try again']);
        }
        return false;
    },

    startPolygonTool: function (fromButton) {
        var startTime = new Date();

        // start polygon if not yet started
        if (!EDR.WEBGEOCODER.polygonHandler.isInEditMode) EDR.WEBGEOCODER.polygonHandler.polygonEditStart();
        //EDR.WEBGEOCODER.polygonHandler.polygon.setOptions({
        //    editable: true
        //});
        EDR.WEBGEOCODER.showPolygonToolInstructions();

        // check if an existing polygon exists
        if (EDR.WEBGEOCODER.polygonHandler.polygon != null) {
            // assume that the polygon has been modified
            EDR.WEBGEOCODER.parcelPolygonModified = true;
        }
        else {
            EDR.WEBGEOCODER.parcelPolygonModified = false;
        }

        // close the parcel info window if open
        if (EDR.WEBGEOCODER.parcelInfoWindow != null) {
            EDR.WEBGEOCODER.parcelInfoWindow.remove();
        }

        if (fromButton) {
            EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_DrawPolygon, 'WebGeocoderV3 UI user clicked on draw polygon');
        }

        // Matomo Tracker
        EDR.WEBGEOCODER.trackEventMatomoPropertyBoundaryDraw();
    },

    endPolygonTool: function (maxArea, maxPerimeter) 
    {
        try {
            //Clear any previous errors
            EDR.WEBGEOCODER.clearErrorMessages()

            //Show the poly instructions (default), complete the map polygon, and save
            if (EDR.WEBGEOCODER.executePolygonSave('')) {
                // polygon successfully saved
                EDR.WEBGEOCODER.polygonHandler.polygonEditStop();
                EDR.WEBGEOCODER.hidePolygonToolInstructions();
                EDR.WEBGEOCODER.updateAreaUI();
            }

            // Matomo Tracker
            EDR.WEBGEOCODER.trackEventMatomoPropertyBoundaryDone();
        }
        catch (err) {
            //alert('Unable to complete the polygon: ' + err.message);
            EDR.WEBGEOCODER.setErrorMessages("Invalid property polygon", [err.message, 'Please try again']);
        }

        __pleaseWait.hide();
        return false;
    },

    confirmRemoveTPPolygon: function () {
        ///<summary>Confirms if the user wants to remove the tp polygon</summary>
        ///<remarks>Called by the 'Remove' button on the sidebar.</remarks>
        try {
            var title = EDR.WEBGEOCODER.parcelRemoveModal.title;
            var content = EDR.WEBGEOCODER.parcelRemoveModal.content;

            // update the modal content
            $('#confirmTPChange .modal-title').html(title);
            $('#confirmTPChange .modal-body').html(content);

            // update the click event
            $('#btnContinueTPChange').unbind('click');
            $('#btnContinueTPChange').click(function () {
                // close the modal
                $('#confirmTPChange').modal('hide');

                // remove the polygon
                EDR.WEBGEOCODER.removePolygon();
                EDR.WEBGEOCODER.tpParcel = null;

                // Matomo Tracker
                EDR.WEBGEOCODER.trackEventMatomoPropertyBoundaryRemove();
            });
            $('#confirmTPChange').modal('show');
        }
        catch (e) {

        }
    },

    removePolygon: function () {
        var savePoly = '';

        try {
            //Clear any previous errors
            EDR.WEBGEOCODER.clearErrorMessages()

            // save polygon
            savePoly = EDR.WEBGEOCODER.polygonHandler.getPolygonDVGCoordinates();

            // remove polygon
            EDR.WEBGEOCODER.polygonHandler.removePolygon();
            EDR.WEBGEOCODER.removeFile();

            if (EDR.WEBGEOCODER.executePolygonSave('')) {
                // polygon successfully saved
                EDR.WEBGEOCODER.polygonHandler.polygonEditStop();
                EDR.WEBGEOCODER.hidePolygonToolInstructions();
                EDR.WEBGEOCODER.updateAreaUI();
                EDR.WEBGEOCODER.parcelPolygonModified = false;	// no polygon to modify
            }
            else {
                // restore polygon
                EDR.WEBGEOCODER.polygonHandler.setPolygonDVGCoordinates(savePoly);
                EDR.WEBGEOCODER.polygonHandler.polygonEditStart();
            }
        }
        catch (err) {
            // restore polygon
            EDR.WEBGEOCODER.polygonHandler.setPolygonDVGCoordinates(savePoly);
            EDR.WEBGEOCODER.polygonHandler.polygonEditStart();

            //alert('Unable to remove the polygon: ' + err.message);
            EDR.WEBGEOCODER.setErrorMessages("Unable to remove property polygon", [err.message, 'Please try again']);
        }

        __pleaseWait.hide();
        return false;
    },

    /*
    EDR.WEBGEOCODER.onPolygonClicked()
 
    Handles polygon onclicked event.
    */
    onPolygonClicked: function (mouseEvt, isLeftClicked) {
        try {
            EDR.WEBGEOCODER.log('onPolygonClicked()')
            // does not handle right click
            if (!isLeftClicked) return true;
            //return true;
            // start polygon if not yet started

            // disabling the start polygon tool based on the new prototype - PBahl 1/21/2015
            //EDR.WEBGEOCODER.startPolygonTool(false);

            // check if tax parcel option is enabled
            if (EDR.EDRMapV2Google.hasOverlayMapType(EDR.WEBGEOCODER.parcelOverlayMapName)) {
                // get the lat/long from the click event
                var evtLatLng = mouseEvt.latLng;

                var data = { extentInMeteres: 1, latitude: evtLatLng.lat(), longitude: evtLatLng.lng(), detailLevel: 15 };

                // start a new timer to get the parcel details
                EDR.WEBGEOCODER.onMapClickTimeDelegate = setTimeout(function () {
                    EDR.WEBGEOCODER.log('Executing mapClickEventDelegateID: ' + EDR.WEBGEOCODER.onMapClickTimeDelegate);
                    // get the parcel details
                    EDR.WEBGEOCODER.getParcelByCoordinate(data);

                    // reset the time delegate
                    EDR.WEBGEOCODER.onMapClickTimeDelegate = null;
                }, 300);

            }
            return true;
        }
        catch (e) {
            EDR.WEBGEOCODER.logError('[ERROR] onPolygonClicked: ' + e.message);
        }
    },

    /*
    EDR.WEBGEOCODER.validatePolygonDisplayError()
 
    Runs polygon validation and display error.
    */
    validatePolygonDisplayError: function (changeFillColor) {
        //Clear any previous errors
        EDR.WEBGEOCODER.clearErrorMessages()

        var retValue = EDR.WEBGEOCODER.validatePolygon(changeFillColor);
        if (!retValue.isValid) {
            if (retValue.errorMessages == null) retValue.errorMessages = [];
            retValue.errorMessages.push('Verify or fix your property polygon');

            EDR.WEBGEOCODER.setErrorMessages('Invalid property polygon', retValue.errorMessages);
        }

        return retValue;
    },

    /*
    EDR.WEBGEOCODER.validatePolygon()
 
    Runs polygon validation rules and updates polygon accordingly based on the result.
    Returns EDR.EDRMapV2.PolygonValidationResult.
    */
    validatePolygon: function (changeFillColor) {
        var retVal = new EDR.EDRMapV2.PolygonValidationResult(null);
        retVal.isValid = false;

        try {
            // get polygon handler
            var polyHandler = EDR.WEBGEOCODER.polygonHandler;
            var poly = polyHandler.polygon;

            // validate polygon
            if (polyHandler.tpMarker == null) {
                retVal.errorMessage = 'Missing property location.';
            }
            else {
                // validatePolygon() returns EDR.EDRMapV2.PolygonValidationResult
                // polyValidateRes.maxDistanceInFeet = 0;
                // polyValidateRes.areaInSquareFeet = 0;
                // polyValidateRes.perimeterInFeet = 0;
                // polyValidateRes.perimeterFactoredInFeet = 0;
                retVal = polyHandler.validatePolygon(EDR.WEBGEOCODER.maxPolygonArea, EDR.WEBGEOCODER.maxPolygonPerimeter, EDR.WEBGEOCODER.polygonMaxVertexDistance);
            }

            // change polygon color if invalid
            if (poly != null) {
                if (retVal.isValid) {
                    //check whether the polygon was marked invalid
                    if (changeFillColor) {
                        EDR.EDRMapV2GoogleV3.PolygonUtilities.changePolygonColors(poly, polyHandler.getPolygonPoints(), polyHandler.polygonOptions.createValidPolygonOptions(), polyHandler.polygonOptions.validMarkerImage);
                    }
                }
                else {
                    EDR.EDRMapV2GoogleV3.PolygonUtilities.changePolygonColors(poly, polyHandler.getPolygonPoints(), polyHandler.polygonOptions.createInValidPolygonOptions(), polyHandler.polygonOptions.inValidMarkerImage);
                }
            }

            return retVal;
        }
        catch (err) {
            retVal.errorMessage = 'Unable to validate polygon: ' + err.message;
            return retVal;
        }
    },

   

    /*
    Name:	EDR.WEBGEOCODER.executePolygonSave()
    Desc:	Function to validate and save polygon data
    Output:	Will adjust UI (turn red) if polygon is not valid, otherwise will save the polygon data
    */
     executePolygonSave: function (fromButton) {
        try {
            var startTime = new Date();
            if (fromButton == 'continue') {
                EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_ContinueClicked, 'WebGeocoderV3 UI user clicked on continue button');
            }
            else {
                EDR.WEBGEOCODER.saveTrackingInformation(startTime, EDR.WEBGEOCODER.webGeocoderActionTypes.WEBGEOV3_PolygonSaved, 'polygon saved');
            }

            //Clear any previous errors
            EDR.WEBGEOCODER.clearErrorMessages()

            //Prep and variable declarations
            var handlerURL = EDR.WEBGEOCODER.handlerURL;
            var geoGUID = EDR.WEBGEOCODER.webGeocoderSessionGUID;
            var sourcePropGUID = EDR.WEBGEOCODER.sourcePropertyGUID;

            // validate polygon
            var polyValidateRes = EDR.WEBGEOCODER.validatePolygonDisplayError(false);
            if (!polyValidateRes.isValid) {
                __pleaseWait.hide();
                //set boundary tool to edit mode (if not in edit mode)
                EDR.WEBGEOCODER.startPolygonTool(false);
                return false;
            }

            var polyData = EDR.WEBGEOCODER.polygonHandler.getPolygonDVGCoordinates();
            var polyDistance = 0;
            var polyProjection = "prjNone";

            //Override our values if we have a polygon
            var polyHandler = EDR.WEBGEOCODER.polygonHandler;
            var poly = polyHandler.polygon;
            if (poly != null) {
                //Polygon present
                polyProjection = "prjGeographic";
                polyDistance = EDR.EDRMapV2GoogleV3.PolygonUtilities.calculateLongestPolygonPointDistance(poly, EDR.WEBGEOCODER.polygonHandler.tpMarker);
            }

            //Declare and set our work variables
            var postData = 'TYPE=SPSAVEPOLYINFO';
            postData += '&geoguid=' + encodeURIComponent(geoGUID);
            postData += '&wgspguid=' + encodeURIComponent(sourcePropGUID);
            postData += '&pdata=' + encodeURIComponent(polyData);  //String
            postData += '&parea=' + encodeURIComponent(polyValidateRes.areaInSquareFeet);
            postData += '&pdist=' + encodeURIComponent(polyDistance);
            postData += '&pperm=' + encodeURIComponent(polyValidateRes.perimeterInFeet); //sq ft
            postData += '&pproj=' + encodeURIComponent(polyProjection);

            //Post the data
            var xmlDoc = EDR.XML.XMLDocumentFromHTTPPost(handlerURL, postData, 'application/x-www-form-urlencoded');
            if (xmlDoc == null) throw new Error('WebGeocoder HTTP handler did not return any data.'); //Exit since we have no results

            //Load up the result
            var objHTTPPostResult = new EDR.EDRMapV2.SavePolygonInfoResult();
            objHTTPPostResult.LoadFromXML($(xmlDoc));

            //Check the status of the reverse geocode execution
            if (objHTTPPostResult.SavePolygonInfoStatus != objHTTPPostResult.EnumSavePolygonInfoStatus.SUCCESSFULL) { throw new Error("Polygon information save operation was not successful: " + objHTTPPostResult.ErrorMessage); }

            //// set polygon color to valid
            //if (poly != null) EDR.EDRMapV2GoogleV3.PolygonUtilities.changePolygonColors(poly, polyHandler.getPolygonPoints(), polyHandler.polygonOptions.createValidPolygonOptions(), polyHandler.polygonOptions.validMarkerImage);

            if (fromButton != 'previewdata') {
                __pleaseWait.hide();
            }

            return true;
        }
        catch (err) {
            //alert('Unable to save the polygon data: ' + err.message);
            EDR.WEBGEOCODER.setErrorMessages("Unable to save property polygon", [err.message, 'Please try again']);

            __pleaseWait.hide();
            return false;
        }
    },

    /*
    Name:	EDR.WEBGEOCODER.updateAreaUI()
    Desc:	Updates the area UI controls to match the currently drawn map polygon
    Output:	Sets the UI elements to current values
    */
    updateAreaUI: function () {
        //Get the current polygon
        var poly = EDR.WEBGEOCODER.polygonHandler.polygon;
        var hasPolygon = (poly != null && (poly.getPath()) && poly.getPath().getArray().length > 0);

        //Test if we have a polygon or not
        if (hasPolygon) {
            //We have a polygon, so update the UI
            var unitOfMeasure;
            var polyUtilResult = EDR.EDRMapV2GoogleV3.PolygonUtilities.calculatePolygonPerimeterArea(poly, 10, 1); ////Calculates the area

            //Set our unit of measure
            switch ($("#ddlPolyAreaMeasurementType").val().toUpperCase()) {
                case 'MILES':
                    unitOfMeasure = EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREMILES;
                    break;
                case 'ACRES':
                    unitOfMeasure = EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.ACRES;
                    break;
                case 'METERS':
                    unitOfMeasure = EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREMETERS;
                    break;
                case 'KM':
                    unitOfMeasure = EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREKILOMETERS;
                    break;
                case 'FEET':
                    unitOfMeasure = "";
                    break;
                default:
                    break;
            }

            //Now make the call and update the UI value
            var area = EDR.EDRMapV2.PolygonUtilities.convertPolygonAreaFromSquareFeet(polyUtilResult.areaInSquareFeet, unitOfMeasure);
            area = area + ' ' + $("#ddlPolyAreaMeasurementType").find(':selected').html();
            $("#lblPolyArea").html(area);
        }
        else {
            //No polygon, so set the value to 0
            $("#lblPolyArea").text("N/A");
        }
    },
    /***************************************************************************************
    END: Polygon Handlers
    ***************************************************************************************/

    showContiguousPropertyHint: function (show) {
        /// <summary> 
        ///     Display the Contiguous property lookup hint 
        /// </summary>
        /// <returns> html to display </returns>

        try {
            // initialize the popover
            $('#pop_contiguous_prop_info').popover({
                placement: 'bottom',
                html: true,
                content: 'This checkbox merges tax parcels that are contiguous. To add this tax parcel, click the "Edit" button and modify your Property Boundary so that it overlaps a portion of this tax parcel. Once they are overlapping, click "Done", select this tax parcel again, and click "Add to Property Boundary".',
                //trigger: 'manual'
                trigger: 'hover'
            });

            if (show) {
                if (EDR.WEBGEOCODER.parcelInfoWindow == null) {
                    show = false;
                };
            };

            if (show) {
                $('#pop_contiguous_prop_info').popover('show');
            }
            else {
                $('#pop_contiguous_prop_info').popover('hide');
            };

        }
        catch (e) {
            alert(e.message);
        }
    },

    displayProcessingUploadAnimation: function (sMessage) {
        try {
            document.getElementById('uploadControl2').style.display = "block";
            $("#uploadControl1").hide();
        } catch (e) {
            // do nothing                
        }
    },

    hideProcessingUploadAnimation: function (sMessage) {
        try {
            document.getElementById('uploadControl2').style.display = "none";
        } catch (e) {
            // do nothing                
        }
    },

    displayFileBrowseAnimation: function () {
        try {
            $("#drop-sub2-zone").hide();
            $("#drop-sub3-zone").show();
        } catch (e) {
            // do nothing                
        }
    },

    hideFileBrowseAnimation: function () {
        try {
            $("#drop-sub3-zone").hide();
            $("#drop-sub2-zone").show();
        } catch (e) {
            // do nothing                
        }
    },

    displayKMLErrorMessage: function (sMessage) {
        try {
            $("#uploadControl1").show();
            $("#divKMLErrorMessage").show();
            document.getElementById('lblKmlErrorMessage').innerHTML = sMessage;
            $("#labelQuestion").hide();
        } catch (e) {
            // do nothing                
        }
    },

    displayKMLLabelQuestion: function () {
        try {
            $("#labelQuestion").show();
            $("#divKMLErrorMessage").hide();
        } catch (e) {
            // do nothing                
        }
    },

    trackEventMatomoSearchByAddress: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('GEOCODER_SEARCH', 'GEOCODER_SEARCH_BY_ADDRESS');
        } catch (e) {
            // do nothing                
        }
    },

    trackEventMatomoSearchByCoordinates: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('GEOCODER_SEARCH', 'GEOCODER_SEARCH_BY_COORDINATES');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoSearchByTaxID: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('GEOCODER_SEARCH', 'GEOCODER_SEARCH_BY_TAXID');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoSearchByTaxIDContinue: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('GEOCODER_SEARCH', 'GEOCODER_SEARCH_BY_TAXID_CONTINUE');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoSearchByTaxIDFind: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('GEOCODER_SEARCH', 'GEOCODER_SEARCH_BY_TAXID_FIND');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoSearchByTaxIDCancel: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('GEOCODER_SEARCH', 'GEOCODER_SEARCH_BY_TAXID_CANCEL');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoPropertyBoundaryDraw: function () {
        try {
            // validate polygon if exists
            var polyPoints = EDR.WEBGEOCODER.polygonHandler.getPolygonPoints();
            if ((polyPoints != null) && (polyPoints.length > 0)) {
                EDR.WEBGEOCODER.trackEventMatomo('DRAW_PROPERTY_BOUNDARY', 'PROPERTY_BOUNDARY_EDIT');
            }
            else {
                EDR.WEBGEOCODER.trackEventMatomo('DRAW_PROPERTY_BOUNDARY', 'PROPERTY_BOUNDARY_DRAW');
            }
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoPropertyBoundaryRemove: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('DRAW_PROPERTY_BOUNDARY', 'PROPERTY_BOUNDARY_REMOVE');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoPropertyBoundaryDone: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('DRAW_PROPERTY_BOUNDARY', 'PROPERTY_BOUNDARY_DONE');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoPropertyBoundarySelection: function (isTP, addBoundary) {
        try {
            if (isTP == false && addBoundary == false) {
                EDR.WEBGEOCODER.trackEventMatomo('PROPERTY_BOUNDARY_SELECTION', 'PROPERTY_BOUNDARY_SELECT');
            } else if (isTP == false && addBoundary == true) {
                EDR.WEBGEOCODER.trackEventMatomo('PROPERTY_BOUNDARY_SELECTION', 'PROPERTY_BOUNDARY_ADD');
            }
            else if (isTP == true && addBoundary == false) {
                EDR.WEBGEOCODER.trackEventMatomo('PROPERTY_BOUNDARY_SELECTION', 'PROPERTY_BOUNDARY_REMOVE');
            }
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoPreProjectOpenReport: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('PRE-PROJECT', 'GEOCODER_OPEN_REPORT');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoFileUploadStarted: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('SHAPEFILE-UPLOAD', 'FILE-UPLOAD-STARTED');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoRetrievedShapeFileFromS3: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('SHAPEFILE-UPLOAD', 'RETRIEVED-SHAPEFILE-FROM-S3');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoPlotUploadedPolygonOnMap: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('SHAPEFILE-UPLOAD', 'PLOTTED-UPLOADED-POLYGON-ON-MAP');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoSavedUploadedPolygon: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('SHAPEFILE-UPLOAD', 'SAVE-UPLOADED-POLYGON-COMPLETED');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomoContinue: function () {
        try {
            EDR.WEBGEOCODER.trackEventMatomo('GEOCODER_SEARCH', 'GEOCODER_CONTINUE');
        } catch (e) {
            // do nothing
        }
    },

    trackEventMatomo: function (actionName, eventName) {
        try {
            if (EDR.WEBGEOCODER.matomoEventTrackingEnable == true) {
                _paq.push(['trackEvent', this.customerAccountNumber, actionName, eventName]);
            }
        } catch (e) {
            // do nothing
        }
    },

    //<summary> Show the copy icon when dragging file over - for KML Upload feature.</summary>
    handleFileSelect: function (evt) {
        try {
            evt.stopPropagation();
            evt.preventDefault();
            //reset or hide error messages if any
            EDR.WEBGEOCODER.displayKMLLabelQuestion();

            //display processing animation in drag-sub-zone     
            EDR.WEBGEOCODER.displayFileBrowseAnimation();

            //get all dropped files
            var files = evt.dataTransfer.files; // FileList object.
            
            //read the file
            EDR.POLYFROMFILE.filesToGeoJson(files);

        } catch (e) {
            // do nothing
        }
    },

    //<summary> Show the copy icon when dragging file over - for KML Upload feature.</summary>
    handleDragOver: function (evt) {
        try {
            evt.stopPropagation();
            evt.preventDefault();
            evt.dataTransfer.dropEffect = 'copymove'; // Explicitly show this is a copy.
        } catch (e) {
            // do nothing
        }
    },

    //<summary> Hide the file Div</summary>
    removeFile: function () {
        document.getElementById('lblFileName').innerHTML = "";
        $("#divFilePreview").hide();
        $("#divFileUpload").show();

        //reset or hide the error message if any
        EDR.WEBGEOCODER.displayKMLLabelQuestion();
        document.getElementById('btnProcessFile').setAttribute("disabled", "disabled");
        $("#inputFile").val('');
    },

    /// <summary>Saves the uploaded file in S3 by calling the Handler Function</summary>
    fileUploadClick: function () {
        //reset or hide the error message if any
        EDR.WEBGEOCODER.displayKMLLabelQuestion();

        //get all selected files
        var fileUpload = $("#inputFile").get(0);
        var files = fileUpload.files;
        files = document.getElementById("inputFile").files;
        //display the spinner on file selection
        EDR.WEBGEOCODER.displayFileBrowseAnimation();

        //read the file
        EDR.POLYFROMFILE.filesToGeoJson(files);

        return true;
    },
    
    cancelFileUpload: function () {
        EDR.POLYFROMFILE.handleCancel();
        $('#uploadControl1').hide();
    },

    acceptFeature: function () {
        EDR.WEBGEOCODER.displayProcessingUploadAnimation();
        EDR.POLYFROMFILE.acceptFeature();
        EDR.WEBGEOCODER.hideProcessingUploadAnimation();
    },
    getGeometryFromPolygon: function (dvgCoordinates) {
        var coordinates = [];
        dvgCoordinates.split("|").forEach(pointStr => {
            coordinates.push([parseFloat(pointStr.split(",")[0]), parseFloat(pointStr.split(",")[1]), 100]);
        });

        var geometry = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature", "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                }, "properties": {}
            }]
        };
        return geometry;
    },

    downloadGeoJson: function () {
        var polyData = EDR.WEBGEOCODER.polygonHandler.getPolygonDVGCoordinates();
        var geometry = EDR.WEBGEOCODER.getGeometryFromPolygon(polyData);
        //EDR.WEBGEOCODER.getPolygonDVGCoordinates
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(geometry)));
        element.setAttribute('download', "EDR_Polygon.geojson");

        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);
    },

}

