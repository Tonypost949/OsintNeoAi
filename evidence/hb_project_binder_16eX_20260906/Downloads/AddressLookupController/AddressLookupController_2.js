// JavaScript source code
'use strict';

(function () {
    var app = angular.module('app', ['EDR.Logging', 'EDR.HTTP.Utilities']);

    app.config(function ($httpProvider) {
        $httpProvider.defaults.useXDomain = true;
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
    });

    app.controller('AddressLookupController', function ($scope, $http, $location, logService, urlService) {
        //initialize 
        $scope.searchAPN = '';

        // initialize with state in
        $scope.searchState = '';
        $scope.searchCounty = 0;
        $scope.parcelSearchResultLimit = EDR.WEBGEOCODER.parcelSearchResultLimit;
        $scope.parcelMoreDataAvailableMessage = '';
        $scope.parcelCounties = [{ county: "All Counties", fips: "0", disabled: false }];
        $scope.parcels = [];

        $scope.callingAPI = false;
        $scope.showErrorMsg = false;
        $scope.showNoResultsMsg = false;
        $scope.showTimeoutMsg = false;

        $scope.apnInputErrorMessage = '';

        $scope.defaultMissingText = '(not reported)';

        // holds current APN search instance guid
        $scope.searchTrackingGUID = '';

        // for logging search input
        var logAPNInput = '';

        var toggleCopyButton = function (enable) {
            try {
                logService.log(logService.SEVERITIES.INFO, 'toggleCopyButton()', 'Attempting to change COPY button image');

                if (enable) {
                    $('#imgCopy').attr('src', '/Global/images/Tax_Search_Find.png');
                    $('#imgCopy').css('cursor', 'pointer');
                    $('#imgCopy').attr('title', 'Use selected address as your property');
                }
                else {
                    $('#imgCopy').attr('src', '/Global/images/Tax_Search_Find_Gray.png');
                    $('#imgCopy').css('cursor', 'default');
                    $('#imgCopy').attr('title', '');
                }
            }
            catch (err) {
                logService.log(logService.SEVERITIES.ERROR, 'toggleCopyButton()', e.message);
            }
        };

        var buildURL = function (host, path, qryStrs, useDocProtocol) {
            ///<summary> Returns the url for the current environment </summary>
            try {
                // use current location to determine protocol
                //var url = location.protocol + '//' + host + path;
                var url = host + path;

                var lochost = location.host.toLowerCase();
                switch (lochost) {
                    case 'web.edrnet.com':
                        url = url.replace('ws.edrnet.com', 'www.web.edrnet.com');
                        break;
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
                logService.log(logService.SERVERITIES.ERROR, 'AddressLookupController.buildURL()', e.message);
                throw e;
            }
        };

        // look for the address selected
        var findAddressSelected = function (parcels) {
            // $scope out of scope | beyond controlled def - passed as argument ...
            if ((angular.isUndefined(parcels)) || (parcels == null)) {
                logService.log(logService.SEVERITIES.WARNING, 'findAddressSelected()', 'parcels is undefined or null');
                return null;
            };

            try {

                var selectedRowId = $("#gdPropSearched").jqGrid('getGridParam', "selrow");
                var parcelID = $("#gdPropSearched").jqGrid('getCell', selectedRowId, 'parcelID');
                //var parcelID = $( "#selAddress option:selected" ).val();			   

                // search for it
                for (var i = 0; i < parcels.length; i++) {
                    if (parcelID == parcels[i].parcelID) {
                        logService.log(logService.SEVERITIES.INFO, 'findAddressSelected()', parcelID + ' found at i=' + i);
                        return parcels[i];
                    }
                }

                logService.log(logService.SEVERITIES.WARNING, 'findAddressSelected()', parcelID + ' was not found');
                return null;
            }
            catch (err) {
                logService.log(logService.SEVERITIES.ERROR, 'findAddressSelected()', e.message);
            }
        };

        // fill the Property Location controls
        var populateTargetPropertyControls = function (addressLocation) {
            if ((angular.isUndefined(addressLocation)) || (addressLocation == null)) {
                logService.log(logService.SEVERITIES.INFO, 'populateTargetPropertyControls()', 'addressLocation is undefined or null');
                return null;
            }

            try {
                logService.log(logService.SEVERITIES.INFO, 'populateTargetPropertyControls()', 'Setting address information on UI');
                EDR.WEBGEOCODERPAGE.setAddressInput(addressLocation);
            }
            catch (err) {
                logService.log(logService.SEVERITIES.ERROR, 'populateTargetPropertyControls()', e.message);
            }
        };

        // invoke elapsed time tracking
        var setElapsedTimeTracking = function (actionTypeID, serverTypeID, trackGUID, briefMessage) {
            /// <summary>
            /// Save elapsed time tracking in app state
            /// </summary>
            /// <param name="actionTypeID">TrackingActionType</param>
            /// <param name="serverEventID">TrackingActionType (SUB CAT)</param>
            /// <param name="trackGUID">tracking GUID</param>
            if ((angular.isUndefined(actionTypeID)) || (actionTypeID == null)) {
                logService.log(logService.SEVERITIES.INFO, 'setElapsedTimeTracking()', 'actionTypeID is undefined or null');
                return null;
            }
            if ((angular.isUndefined(trackGUID)) || (trackGUID == null)) {
                logService.log(logService.SEVERITIES.INFO, 'setElapsedTimeTracking()', 'trackGUID is undefined or null');
                return null;
            }
            //
            try {
                EDRV2.TRACKING.saveElapsedTimeAppState(actionTypeID, serverTypeID, trackGUID, briefMessage);
            }
            catch (e) {
                logService.log(logService.SEVERITIES.ERROR, 'populateTargetPropertyControls()', e.message);
            }
        };

        // wraps the call to calculate elapsed tracking distance
        var invokeCalculateElapsedTime = function (trackingGUID) {
            if ((angular.isUndefined(trackingGUID)) || (trackingGUID == null)) {
                logService.log(logService.SEVERITIES.INFO, 'setElapsedTimeTracking()', 'actionTypeID is undefined or null');
                return null;
            }
            //
            try {
                EDRV2.TRACKING.CalculateElapsedTrack(trackingGUID);
            }
            catch (err) {
                logService.log(logService.SEVERITIES.ERROR, 'populateTargetPropertyControls()', err.message);
            }

        };

        $scope.getParcelCounties = function () {
            ///<summary> 
            ///     function to retrieve counties for a selected state 
            ///</summary>
            // API call sample 'http://wsdev.edrnet.com/edrservices/geospatial/api/dmp/20150323/parcelCounties/CT?filter=0'

            $scope.searchCounty = 0;
            $scope.parcelCounties = [{ county: "All Counties", fips: "0", disabled: false }];

            var stateKey = $scope.searchState;
            if (stateKey == '')
                stateKey = 'CT';

            stateKey = '/' + stateKey;

            var qryStrs = [];
            qryStrs.push({ key: 'filter', value: '0' });		//filter:0 - returns all counties with the hasParcelData flag showing true or false, 1-returns only counties with hasParcelData = true.    
            //ws.edrnet.com
            var url = urlService.buildURL(urlService.translateHost('www.web.edrnet.com'), '/edrservices/geospatial/api/dmp/20150323/parcelCounties' + stateKey, qryStrs, true);
            //var url = buildURL(EDRWOS.parcelCountiesServiceURL + stateKey, '', qryStrs, true);
            //$scope.callingAPI = true;

            // track 
            $scope.searchTrackingGUID = EDR.WEBGEOCODERPAGE.getNewGUID();
            setElapsedTimeTracking(EDRV2.TRACKING.ActionTypes.WOS_GETCOUNTIES_START, EDRV2.TRACKING.ActionTypes.WOS_GETCOUNTIES_CPLT, $scope.searchTrackingGUID, stateKey);

            // send the request
            $http({
                method: 'GET',
                url: url,
                timeout: 20000,
                headers: { 'Content-Type': 'application/json', 'Authorization': EDR.WEBGEOCODER.geoSpatialServiceAuthToken }
            })
                .error(function (data, status, headers, config, statusText) {
                    // hide the crop loading
                    logService.log(logService.SEVERITIES.ERROR, 'getParcelCounties()', url);
                    logService.log(logService.SEVERITIES.ERROR, 'getParcelCounties()', data);

                    if (status === 0) {
                        //$scope.showErrorMsg = true;
                        //$scope.showTimeoutMsg = true;
                        logService.log(logService.SEVERITIES.ERROR, 'getParcelCounties()', 'Request timed out.')
                    }

                    $scope.callingAPI = false;
                })
                .success(function (data, status) {
                    // Get the cropped image path
                    //alert('For the love of God it works');
                    logService.log(logService.SEVERITIES.INFO, 'getParcelCounties()', url);
                    logService.log(logService.SEVERITIES.INFO, 'getParcelCounties()', data);
                    //$scope.callingAPI = false;
                    // log elapsed time
                    invokeCalculateElapsedTime($scope.searchTrackingGUID);

                    if ((data.parcelCounties != null) && (data.parcelCounties.length > 0)) {
                        logService.log(logService.SEVERITIES.INFO, 'getParcelCounties()', 'data.parcelCounties.length: ' + data.parcelCounties.length);
                        //$scope.showErrorMsg = false;
                        //$scope.showNoResultsMsg = false;
                        //$scope.showTimeoutMsg = false;

                        //$scope.parcelCounties = data.parcelCounties;
                        var tempCountyName = "";
                        var tempDisabled = false;
                        for (var i = 0; i < data.parcelCounties.length; i++) {
                            if (data.parcelCounties[i].hasParcelData) {
                                tempCountyName = data.parcelCounties[i].county;
                                tempDisabled = false;
                            }
                            else {
                                tempCountyName = data.parcelCounties[i].county + ' - No Tax Data';
                                tempDisabled = true;
                            }
                            $scope.parcelCounties.push({ county: tempCountyName, fips: data.parcelCounties[i].fips, disabled: tempDisabled });
                        };

                        ////remove counties which have no parcel data - this is not needed as the api allows to do the same filter				        
                        //$scope.parcelCounties = $.grep(data.parcelCounties, function(e){ 
                        //    return e.HasParcelData != false; 
                        //});
                    }
                    else {
                        // set it as an empty string - no addresses
                        logService.log(logService.SEVERITIES.INFO, 'getParcelCounties()', 'data.parcelCounties == null');
                        //$scope.parcelCounties = [{ county: "All Counties", fips: "0", disabled: false }];
                        //$scope.showErrorMsg = true;
                        //$scope.showNoResultsMsg = true;
                        //$scope.showTimeoutMsg = false;
                    }

                });
        };


        $scope.onSearchAPNKeyDown = function (e) {
            try {
                if (e.keyCode === 13) {
                    // execute the search
                    $scope.searchAddressByAPN();

                    // cancel the post-back
                    e.preventDefault();
                    return false;
                }
                else {
                    return true;
                }
            }
            catch (er) {
                // do nothing
                return true;
            }
        };

        // search addresses ...
        $scope.searchAddressByAPN = function () {
            ///<summary> 
            ///     Search property by apn and load the grid 
            ///</summary>

            // API call sample 'http://wsdev.edrnet.com/edrservices/geospatial/api/dmp/20150323/parcels?state=CT&apn=018%20E04%2F018'

            try {
                // Matomo Track Event
                EDR.WEBGEOCODER.trackEventMatomoSearchByTaxIDContinue();
            } catch (e) {
                logService.log(logService.SEVERITIES.ERROR, 'trackEventMatomoSearchByTaxIDContinue()', e.message);
            }

            $scope.parcels = [];

            if ($("#gdPropSearched")[0].grid) {
                //grid is available
                //reset grid
                jQuery("#gdPropSearched").jqGrid("GridUnload");
                //disable the ok button
                toggleCopyButton(false);
                //create the grid with no data
                $scope.populateApnGrid();
            };

            $scope.apnInputErrorMessage = '';
            $scope.parcelMoreDataAvailableMessage = '';
            $scope.showErrorMsg = false;
            $scope.showNoResultsMsg = false;
            $scope.showTimeoutMsg = false;

            // validate input remove punctuations and must be >= 5
            var apnInput = $scope.searchAPN.replace(/\W/g, '');

            // remove the leading zeros
            apnInput = apnInput.replace(/^0+|0+$/g, '');

            // log the search param, original || parsed
            logAPNInput = $scope.searchAPN + '||' + apnInput;


            if (apnInput.length < 4) {
                $scope.apnInputErrorMessage = 'Search requires minimum of 4 alphanumeric characters';
                //disable the ok button
                toggleCopyButton(false);
                return true;
            }

            var qryStrs = [];
            //add state to query filter if fips(county) is not available
            //if ($scope.searchCounty == '0')
            if ($scope.searchCounty == 0)
                qryStrs.push({ key: 'state', value: $scope.searchState });
            else
                qryStrs.push({ key: 'fips', value: $scope.searchCounty });

            qryStrs.push({ key: 'apn', value: apnInput });
            qryStrs.push({ key: 'stripapn', value: '1' });
            qryStrs.push({ key: 'limit', value: $scope.parcelSearchResultLimit });

            var url = urlService.buildURL(urlService.translateHost('www.web.edrnet.com'), '/edrservices/geospatial/api/dmp/20150323/parcels', qryStrs, true);
            //var url = buildURL(EDRWOS.parcelServiceURL, '', qryStrs, true);

            $scope.callingAPI = true;

            // track 
            $scope.searchTrackingGUID = EDR.WEBGEOCODERPAGE.getNewGUID();
            setElapsedTimeTracking(EDRV2.TRACKING.ActionTypes.WOS_APNSEARCH_START, EDRV2.TRACKING.ActionTypes.WOS_APNSEARCH_CPLT, $scope.searchTrackingGUID, logAPNInput);

            // send the request
            $http({
                method: 'GET',
                url: url,
                timeout: 20000,
                headers: { 'Content-Type': 'application/json', 'Authorization': EDR.WEBGEOCODER.geoSpatialServiceAuthToken }
            })
                .error(function (data, status, headers, config, statusText) {
                    // hide the crop loading
                    logService.log(logService.SEVERITIES.ERROR, 'searchAddressByAPN()', url);
                    logService.log(logService.SEVERITIES.ERROR, 'searchAddressByAPN()', data);

                    if (status === 0) {
                        $scope.showErrorMsg = true;
                        $scope.showTimeoutMsg = true;
                        logService.log(logService.SEVERITIES.ERROR, 'searchAddressByAPN()', 'Request timed out.')
                    }

                    $scope.callingAPI = false;
                    toggleCopyButton(false);

                    //reset grid if needed.			    
                })
                .success(function (data, status) {
                    // Get the cropped image path
                    //alert('For the love of God it works');
                    logService.log(logService.SEVERITIES.INFO, 'searchAddressByAPN()', url);
                    logService.log(logService.SEVERITIES.INFO, 'searchAddressByAPN()', data);
                    $scope.callingAPI = false;
                    // log elapsed time
                    invokeCalculateElapsedTime($scope.searchTrackingGUID);

                    if ((data.parcels != null) && (data.parcels.length > 0)) {
                        logService.log(logService.SEVERITIES.INFO, 'searchAddressByAPN()', 'data.parcels.length: ' + data.parcels.length);
                        $scope.showErrorMsg = false;
                        $scope.showNoResultsMsg = false;
                        $scope.showTimeoutMsg = false;

                        if (data.metadata != null) {
                            if (data.metadata.totalCount > $scope.parcelSearchResultLimit) {
                                $scope.parcelMoreDataAvailableMessage = "The search returned more than " + $scope.parcelSearchResultLimit + " records. Please refine your search."
                            }
                        }

                        // fix the missing information
                        var curParcel = null, curAddress, curCity, curState, curZipCode;
                        for (var i = 0; i < data.parcels.length; i++) {
                            data.parcels[i].streetLine = $scope.defaultMissingText; // create new property for address line
                            data.parcels[i].lastLine = ''; // create new property for last line
                            curParcel = data.parcels[i];

                            curAddress = curParcel.address || $scope.defaultMissingText;
                            curCity = curParcel.city || $scope.defaultMissingText;
                            curState = curParcel.state || $scope.defaultMissingText;
                            curZipCode = curParcel.zip || $scope.defaultMissingText;

                            // change display text if none of the values are available to us
                            if (!(curAddress === $scope.defaultMissingText)) {
                                data.parcels[i].streetLine = curParcel.address;
                            }
                            if (!((curCity === $scope.defaultMissingText) && (curState === $scope.defaultMissingText) && (curZipCode === $scope.defaultMissingText))) {
                                data.parcels[i].lastLine = '' + curParcel.city + ', ' + curParcel.state + '  ' + curParcel.zip;
                            }
                        }

                        $scope.parcels = data.parcels;
                    }
                    else {
                        // set it as an empty string - no addresses
                        logService.log(logService.SEVERITIES.INFO, 'searchAddressByAPN()', 'data.parcels == null');
                        $scope.parcels = [];
                        $scope.showErrorMsg = true;
                        $scope.showNoResultsMsg = true;
                        $scope.showTimeoutMsg = false;
                    }

                    //reset grid
                    jQuery("#gdPropSearched").jqGrid("GridUnload");
                    toggleCopyButton(false);
                    //create the grid with the parcel data
                    $scope.populateApnGrid();

                });
        };

        $scope.populateApnGrid = function () {
            ///<summary> 
            ///     function to populate the grid 
            ///</summary>
            try {
                //Declare DOM elements
                //var dvLoading = null;
                var dvGrid = null;
                var dvGridNoData = null;
                //var uiHeaderRowCount = null;		        
                var numberOfGridRows = 200; //default
                var heightOfGrid = '250'; //default 403
                //hide scrollbar when number of records is less than 12
                var bDisplayScrollbar = true;
                if ($scope.parcels.length < 12) {
                    bDisplayScrollbar = false;
                };

                //hook in grids here dependent on categoryID
                jQuery("#gdPropSearched").jqGrid({
                    datatype: "local",
                    data: $scope.parcels,
                    loadonce: true,
                    rowNum: numberOfGridRows,
                    height: heightOfGrid,
                    autowidth: true,
                    //caption: '<div class="row" style="margin-top: 1px;"><div class="col-md-12"><span class="modal-title" style="font-weight: bold; font-size:14px;">Search Results</span><span class="modal-title" style="font-size:10px;"> - Select from the list and click OK.</span><br /><span class="modal-title" style="font-size:8px;">(The Latitude and longitude from the selected record will be used to locate your property)</span></div></div>',
                    colNames: ['ID', 'Address', 'City/State/Zip', 'Tax ID'],
                    colModel: [
                        { name: 'parcelID', index: 'parcelID', hidden: true, sorttype: "int", align: "center" },
                        { name: 'streetLine', index: 'streetLine', width: '30%', sorttype: "text", align: "center" },
                        { name: 'lastLine', index: 'lastLine', width: '30%', sorttype: "text", align: "center" },
                        { name: 'apn', index: 'apn', width: '30%', sorttype: "text", align: "center" }
                    ],
                    multiselect: false,
                    viewrecords: true,
                    ignoreCase: true,
                    //width: 450,
                    scrollerbar: bDisplayScrollbar,	//whether scrollbar column to be added or not      
                    shrinktofit: true, //shrink when scrollbar is false
                    scrollOffset: 0, //hide scrollbar column when scrollbar is false		            
                    hidegrid: false,//hide the expand/collapse icon
                    emptyrecords: "No records to view",
                    loadtext: "Loading...",
                    //loadComplete: function(){   
                    //    //select the exact match apn as default
                    //    var grid_ids=grid.jqGrid('getDataIDs');
                    //    for(var i=0; i<grid_ids.length; i++){
                    //        var rowid = grid_ids[i];
                    //        var aRow = grid.jqGrid('getRowData',rowid);
                    //        var apn_id = aRow['apn'];
                    //        //if($.inArray(apn_id,apnInput)!=-1){
                    //        if(apn_id == apnInput){
                    //            //select this row as default
                    //            grid.jqGrid('setSelection',rowid,true);
                    //            //enable the ok button of row selection
                    //            toggleCopyButton( true );
                    //        }
                    //    }		                
                    //},	            
                    onSelectRow: function (rowid, selected) {
                        if (rowid != null) {
                            //$scope.onSelectedAddressKeyDown(selected);
                            //enable the ok button of row selection
                            toggleCopyButton(true);
                        }
                    },
                    ondblClickRow: function (rowid, iRow, iCol) {
                        // set the selected address as Target property and close the popup
                        $scope.setTargetProperty();
                    },
                    sortname: "apn",
                    sortorder: "asc",
                    pager: '#prSearched'
                });
                //The below is if we need to display refresh and other icons on the bottom bar left corner of the grid.
                //jQuery("#gdPropSearched").jqGrid('navGrid', '#prSearched', { del: false, add: false, edit: false });

            }
            catch (err) {
                logService.log(logService.SEVERITIES.ERROR, 'populateApnGrid()', e.message);
            }
        };

        $scope.onCancelClick = function () {

            try {
                try {
                    // Matomo Track Event
                    EDR.WEBGEOCODER.trackEventMatomoSearchByTaxIDCancel();
                } catch (e) {
                    logService.log(logService.SEVERITIES.ERROR, 'trackEventMatomoSearchByTaxIDCancel()', e.message);
                }

                // reset state of search
                $scope.searchAPN = '';
                $scope.searchState = '';
                $scope.searchCounty = 0;
                $scope.parcels = [];
                $scope.parcelCounties = [{ county: "All Counties", fips: "0", disabled: false }];
                $scope.callingAPI = false;
                $scope.showErrorMsg = false;
                $scope.showNoResultsMsg = false;
                $scope.showTimeoutMsg = false;
                $scope.apnInputErrorMessage = '';
                $scope.parcelMoreDataAvailableMessage = '';

                if ($("#gdPropSearched")[0].grid) {
                    //if grid is available reset/unload it
                    jQuery("#gdPropSearched").jqGrid("GridUnload");
                    // disable ok button
                    toggleCopyButton(false);
                };

                // hide the pop-up form
                $('#divAddressLookupMain').modal('hide');
                
            }
            catch (err) {
                logService.log(logService.SEVERITIES.ERROR, 'onCancelClick()', e.message);
            }

        };

        //$scope.addressSelected = function ( item )
        //{
        //	try
        //	{
        //		// get the selected item
        //		var sel = $( "#selAddress option:selected" ).val() || '';
        //		//alert( sel );

        //		// toggle button if an item was selected
        //		if ( sel != '' ) toggleCopyButton( true );
        //	}
        //	catch ( err )
        //	{
        //		logService.log( logService.SEVERITIES.ERROR, 'addressSelected()', e.message );
        //	}
        //};

        //$scope.onSelectedAddressKeyDown = function (e) {
        //	try {
        //		if (e.keyCode === 13) {
        //			// set the target property
        //			$scope.setTargetProperty();

        //			// cancel the postback
        //			e.preventDefault();
        //			return false;
        //		}
        //		else {
        //			return true;
        //		}
        //	}
        //	catch (er) {
        //		// do nothing
        //		return true;
        //	}
        //};

        $scope.setTargetProperty = function () {
            ///<summary> 
            ///     function to set target property 
            ///</summary>
            try {

                try {
                    // Matomo Track Event
                    EDR.WEBGEOCODER.trackEventMatomoSearchByTaxIDFind();
                } catch (e) {
                    logService.log(logService.SEVERITIES.ERROR, 'trackEventMatomoSearchByTaxIDFind()', e.message);

                }

                // get the selected address
                var selectedParcel = findAddressSelected($scope.parcels);
                if (selectedParcel != null) {
                    // modify model since there is change the Address and State can be null from API
                    selectedParcel.address = selectedParcel.address || $scope.defaultMissingText;
                    selectedParcel.city = selectedParcel.city || '';
                    selectedParcel.state = selectedParcel.state || $scope.searchState;
                    selectedParcel.zip = selectedParcel.zip || '';

                    populateTargetPropertyControls(selectedParcel);

                    // hide the llokup form
                    $('#divAddressLookupMain').modal('hide');

                    // uncomment this to auto submit enter location page to go to geocoder
                    //$( '#ctl00_ctl00_cphBody_cphMainContent_ibtContinue' ).click();
                }
            }
            catch (e) {
                logService.log(logService.SEVERITIES.ERROR, 'setTargetProperty()', e.message);
            }
        };

        $scope.initApnGrid = function () {
            ///<summary> 
            ///     function to initiate the grid with no data 
            ///</summary>
            //$scope.showErrorMsg = false;
            //$scope.showNoResultsMsg = false;
            //$scope.showTimeoutMsg = false;
            if ($("#gdPropSearched")[0].grid) {
                //grid is available
                //unload it
                jQuery("#gdPropSearched").jqGrid("GridUnload");
                //create the grid with no data
                $scope.populateApnGrid();
            }
            else {
                //grid is not available
                //create the grid with no data
                $scope.populateApnGrid();
            }
            //disable the ok button
            toggleCopyButton(false);
        };

        //$scope.initApnGrid();

    }); // End Of AddressLookupController def
})();

