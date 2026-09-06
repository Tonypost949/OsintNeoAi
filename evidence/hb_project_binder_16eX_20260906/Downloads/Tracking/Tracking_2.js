// Script File contains 
if ( typeof ( EDRV2 ) == 'undefined' ) { EDRV2 = {}; }
if ( typeof ( EDRV2.TRACKING ) == 'undefined' ) { EDRV2.TRACKING = {}; }
if ( typeof ( EDRV2.TRACKING.DATAMANAGER ) == 'undefined' ) { EDRV2.TRACKING.DATAMANAGER = {}; }

//enumerators 
EDRV2.TRACKING.ActionTypes = {
    WOS_APNSEARCH_START: 65, WOS_APNSEARCH_CPLT: 70,
    WOS_GETCOUNTIES_START: 75, WOS_GETCOUNTIES_CPLT: 80
}

// APPLICATION STATE
EDRV2.TRACKING.ApplicationState = function () {
	var m_Store = {};

	// private func
	function store( key, value ) {
		/// <summary>Accessor to get and set data into private store.</summary>
		/// <param name="key">Key of the item.</param>
		/// <param name="value">If specified - will set and return the value of the item, else will just return the current value.</param>
		try {
			// key is required
			if ( ( typeof ( key ) == 'undefined' ) || ( key == null ) ) throw new Error( 'Unable to get data store because of missing key.' );

			// if value is specified - set operation
			if ( typeof ( value ) != 'undefined' ) {
				m_Store[key] = value;
			}

			// return data - if not defined we'll return null
			return m_Store[key] || null;
		}
		catch ( e ) {
			throw e;
		}
	};

	var singleton = {

		eTrackData: function ( value ) {
			/// <summary>Gets/Sets the elapsed track data</summary>
			try {
				if ( ( typeof ( value ) != 'undefined' ) )
					return store( 'WOS_eTrackData', value );
				else
					return store( 'WOS_eTrackData' );
			}
			catch ( e ) {
				throw e;
			}
		},
		instGUID: function ( value ) {
			/// <summary>Gets/Sets the Instance GUID for tracking elapsed time</summary>
			try {
				if ( ( typeof ( value ) != 'undefined' ) )
					return store( 'WOS_instGUID', value );
				else
					return store( 'WOS_instGUID' );
			}
			catch ( e ) {
				throw e;
			}
		}

	}

	return singleton;

}();

EDRV2.TRACKING.saveElapsedTimeAppState = function ( actionTypeID, serverTypeID, trackGUID, briefMessage ) {
	/// <summary>
	/// Save elapsed time tracking in app state
	/// </summary>
	/// <param name="actionTypeID"></param>
	/// <param name="serverEventID"></param>
	/// <param name="trackGUID"></param>
	try {
		var trackData;
		var startTime = moment( new Date() ).format( 'YYYY/MM/DD HH:mm:ss:SSS' );
		//var trackGUID = EDRV2.DRAWINGTOOLS.UI.generateUUID();
		var actionID = actionTypeID;
		var serverID = serverTypeID;
		var trackData = EDRV2.TRACKING.ApplicationState.eTrackData();

		//Creating JSON object to include all details for log
		if ( trackData == null ) {
			trackData = [];
		};
		trackData.push( {
			"trackGUID": trackGUID,
			"actionID": actionID,
			"serverID": serverID,
			"startTime": startTime,
			"briefMsg": briefMessage
		} );
		EDRV2.TRACKING.ApplicationState.eTrackData(trackData);
		//return trackGUID;
	}
	catch ( err ) {
		throw err;
	}
};

EDRV2.TRACKING.CalculateElapsedTrack = function ( elapsedTrackGUID ) {
	/// <summary>
	/// Calculated elapsed time for the event 
	/// </summary>
	/// <param name="elapsedTrackArray"></param>
	try {
		if ( elapsedTrackGUID == undefined ) return;
		var instanceGUID = EDRV2.TRACKING.ApplicationState.instGUID();
		var eTrackDataArray = EDRV2.TRACKING.ApplicationState.eTrackData();
		if ( eTrackDataArray.length == 0 ) return;
		//Loop through arra
		var eventLogArray;
		for ( var i = 0; i < eTrackDataArray.length; i++ ) {
			if ( eTrackDataArray[i].trackGUID == elapsedTrackGUID ) {
				eventLogArray = eTrackDataArray;
				break;
			}
		}

		if ( eventLogArray[0] != null || eventLogArray[0] != undefined ) {
			//Remove the item with Track GUID from Appstate as it is no longer required for calculations
			var newLoggedData = eTrackDataArray.filter( function ( env ) {
				//If track Guid doesnt match add it to array
				if ( env.trackGUID != elapsedTrackGUID )
					return env;
			} );
			eTrackDataArray = newLoggedData;
			//Save the new logged array in App state for future elapsed time calculations
			EDRV2.TRACKING.ApplicationState.eTrackData( eTrackDataArray );

			//Calculate elapsed time between two given times
			var endTime = moment( new Date() ).format( 'YYYY/MM/DD HH:mm:ss:SSS' );
			var startTime = eventLogArray[0].startTime;
			//Calculate elapsed time in milliseconds
			var msElapsedTime = moment( endTime, "YYYY/MM/DD HH:mm:ss:SSS" ).diff( moment( startTime, "YYYY/MM/DD HH:mm:ss:SSS" ) )
			//Remove the milliseconds so that it can be saved in db
			//startTime = moment(startTime).format('YYYY/MM/DD HH:mm:ss');
			//endTime = moment(endTime).format('YYYY/MM/DD HH:mm:ss');

			//Call Dm to save elapsed time
			EDRV2.TRACKING.DATAMANAGER.saveElapsedTracking( 10, eventLogArray[0].actionID, eventLogArray[0].serverID, true, startTime, endTime, msElapsedTime, eventLogArray[0].briefMsg, null, instanceGUID, eventLogArray[0].trackGUID, null, null, null );

		}

	}
	catch ( err ) {
		throw err;
	}
};

// Data Layer

EDRV2.TRACKING.DATAMANAGER.saveElapsedTracking = function ( srcSystemID, actID, servID, status, startTime, endTime, msElapsedTime, brfMesg, msgPath, instGUID, trackGUID, orderGUID, repoGUID, toxGUID )
{
	/// <summary>
	/// Saves Elapsed time Info
	/// </summary>
	/// <param name="srcSystemID"></param>
	/// <param name="actID"></param>
	/// <param name="servID"></param>
	/// <param name="startTime"></param>
	/// <param name="endTime"></param>
	/// <param name="brfMesg"></param>
	/// <param name="msgPath"></param>
	/// <param name="instGUID"></param>
	/// <param name="trackGUID"></param>
	/// <param name="orderGUID"></param>
	/// <param name="propGUID"></param>
	/// <param name="repoGUID"></param>
	/// <param name="toxGUID"></param>
	/// <param name="sessGUID"></param>

	try {
		// validate
		var url = EDRV2.HTTP.buildURL( EDRV2.HTTP.translateHost( 'www.web.edrnet.com' ), '/ordering/wos/getresourcesv2.ashx', null, true );

		srcSystemID = srcSystemID || null;
		if ( ( srcSystemID == null ) || ( srcSystemID == '' ) ) throw new Error( 'Missing Source System ID.' );
		actID = actID || null;
		if ( ( actID == null ) || ( actID == '' ) ) throw new Error( 'Missing Action ID.' );
		servID = servID || null;
		if ( ( servID == null ) || ( servID == '' ) ) throw new Error( 'Missing Source Server ID.' );
		startTime = startTime || null;
		if ( ( startTime == null ) || ( startTime == '' ) ) throw new Error( 'Missing Start time of event.' );
		endTime = endTime || null;
		if ( ( endTime == null ) || ( endTime == '' ) ) throw new Error( 'Missing End Time of event.' );

		brfMesg = brfMesg || null;
		if ( brfMesg == null ) brfMesg = '';
		msgPath = msgPath || null;
		if ( msgPath == null ) msgPath = '';
		instGUID = instGUID || null;
		if ( instGUID == null ) instGUID = '';
		trackGUID = trackGUID || null;
		if ( trackGUID == null ) trackGUID = '';
		orderGUID = orderGUID || null;
		if ( orderGUID == null ) orderGUID = '';
		toxGUID = toxGUID || null;
		if ( toxGUID == null ) toxGUID = '';

		// GUIDS
		var sessGUID = $( '#_LSessGUID' ).val();
		var propGUID = $( '#__PropGUID' ).val();

		// post to server
		var qryData = [];
		qryData.push( { name: "ACTION", value: 'SAVEELAPSEDTRACKING' } );
		qryData.push( { name: "SYSID", value: encodeURIComponent( srcSystemID ) } );
		qryData.push( { name: "ACTID", value: encodeURIComponent( actID ) } );
		qryData.push( { name: "SEVEID", value: encodeURIComponent( servID ) } );
		qryData.push( { name: "STATUS", value: encodeURIComponent( status ) } );
		qryData.push( { name: "STIME", value: encodeURIComponent( startTime ) } );
		qryData.push( { name: "ETIME", value: encodeURIComponent( endTime ) } );
		qryData.push( { name: "ELAPSEDTIME", value: encodeURIComponent( msElapsedTime ) } );
		qryData.push( { name: "BRFMESG", value: encodeURIComponent( brfMesg ) } );
		qryData.push( { name: "MESPATH", value: encodeURIComponent( msgPath ) } );
		qryData.push( { name: "INSTGUID", value: encodeURIComponent( instGUID ) } );
		qryData.push( { name: "TRACKGUID", value: encodeURIComponent( trackGUID ) } );
		qryData.push( { name: "ORDGUID", value: encodeURIComponent( orderGUID ) } );
		qryData.push( { name: "REPGUID", value: encodeURIComponent( repoGUID ) } );
		qryData.push( { name: "TOXGUID", value: encodeURIComponent( toxGUID ) } );
		qryData.push( { name: "SESGUID", value: encodeURIComponent( sessGUID ) } );
		qryData.push( { name: "PROPGUID", value: encodeURIComponent( propGUID ) } );
		qryData.push( { name: "BRFMESG", value: encodeURIComponent( brfMesg ) } );

		var qryInputString = EDRV2.HTTP.createDataString( qryData );

		EDRV2.HTTP.requestPost( url, qryInputString, null, null, null, false, null ); //function pointer

		return;
	}
	catch ( e ) {
		throw new Error( '(DataManager): Unable to save tracking: ' + e.message );
	}

}

// Utilities
// Elapsed time tracking
EDRV2.TRACKING.generateUUID = function () {
	/// <summary>
	/// Generate GUID in js...This is not orginal GUID but GUID like UUID
	/// </summary>
	/// <returns type="guid"></returns>
	var d = new Date().getTime();
	var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace( /[xy]/g, function ( c ) {
		var r = ( d + Math.random() * 16 ) % 16 | 0;
		d = Math.floor( d / 16 );
		return ( c == 'x' ? r : ( r & 0x7 | 0x8 ) ).toString( 16 );
	} );
	return uuid;
};

// sets the instance GUID this is a APN Search session
EDRV2.TRACKING.setInstanceGUID = function () {
	try
	{
		var iTrackGUID = EDRV2.TRACKING.generateUUID();
		EDRV2.TRACKING.ApplicationState.instGUID( iTrackGUID );
	}
	catch ( e )
	{
		throw new Error( '(setInstanceGUID): Unable to generate instance GUID for  tracking: ' + e.message );
	}
};

