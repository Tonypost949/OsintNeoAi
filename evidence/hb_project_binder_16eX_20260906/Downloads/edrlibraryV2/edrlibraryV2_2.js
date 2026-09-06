// define namespace if not yet defined
if ( typeof ( EDRV2 ) === 'undefined' )
{
	EDRV2 = {};
}

/****************************************************
EDR general utilities (static functions).

Provides bunch of general utility functions.
*****************************************************/
EDRV2 =
{
	addSlashes: function ( rawString )
	{
		/// <summary>Encodes reserved chars with slash.</summary>
		/// <param name="rawString">String to encode.</param>

		rawString = rawString || '';

		if ( rawString == '' ) return '';

		try
		{
			// this is a crude stub to replace ' with \'
			return rawString.replace( /\'/gi, '\\\'' );
		}
		catch ( e )
		{
			throw new Error( 'Unable to escape JS reserved characters: ' + e.message );
		}
	},

	displayObjectProperties: function ( obj, recurse, prefix, propsToIgnore )
	{
		/// <summary>Display object property values.</summary>
		/// <param name="obj">Object to enumerate.</param>
		/// <param name="recurse">True to recurse through properties.</param>
		/// <param name="prefix">Prefix for recursion.</param>
		/// <param name="propsToIgnore">Array of property names to ignore.</param>

		// flag whether to recurse
		var recursive = recurse || false;

		// prefix for the property/function name and it is passed in during the recursion
		// process
		var p = EDRV2.trim( prefix || '' );

		var ignoreList = propsToIgnore || [];
		if ( !( ignoreList instanceof Array ) )
		{
			ignoreList = [ignoreList];
		}

		// build msg
		var msg = '';
		if ( obj != null )
		{
			var typeOfProp = '';
			var skip = false;

			for ( var i in obj )
			{
				// skip this prop?
				skip = false;
				for ( var j = 0; j < ignoreList.length; j++ )
				{
					if ( ignoreList[j] == i )
						skip = true;
					else if ( ( i == 'EDRParent' ) || ( i == 'base' ) )
						skip = true;

					if ( skip ) break;
				}

				typeOfProp = typeof ( obj[i] );
				// EDRParent and base are 2 reserved property names for EDR framework objects
				// so we are not going to recurse through them
				if ( ( !skip ) && ( typeOfProp != 'function' ) )
				{
					try
					{
						if ( typeof obj[i] == 'object' )
						{

							if ( obj[i] != null )
								msg += p + i + '=[object]\n';
							else
								msg += p + i + '=(null)' + '\n';

							// check if we need to do recursive
							if ( recursive == true ) msg += EDRV2.displayObjectProperties( obj[i], recursive, p + i + '.' );
						}
						else
						{
							msg += p + i + '=' + obj[i] + '\n';
						}
					}
					catch ( e )
					{
						// error is thrown if failed to get the value
						msg += i + '--FAILED TO ENUMERATE--\n';
					}
				}
				else if ( typeOfProp != 'function' )
				{
					// EDRParent is specific for EDR JS object to link current object to its parent -- effectively creating circular reference
					if ( obj[i] != null )
						msg += p + i + '=[' + typeOfProp + ']\n';
					else
						msg += p + i + '=(null)' + '\n';
				}
			}
		}

		return msg;
	},

	trim: function ( value )
	{
		/// <summary>Trims leading and trailing whitespaces/</summary>
		/// <param name="value">String to trim.</param>

		// clean value
		var val = value || '';
		if ( val == '' ) return '';

		// use regexp to trim
		try
		{
			/*
			copied from http://blog.stevenlevithan.com/archives/faster-trim-javascript
			*/
			var str = val.replace( /^\s\s*/, '' );
			var ws = /\s/;
			var i = str.length;
			while ( ws.test( str.charAt( --i ) ) );

			return str.slice( 0, i + 1 );
		}
		catch ( e )
		{
			return '';
		}
	},
	
	parseBoolean: function( value, defaultVal ) {
		/// <summary> Converts the value to boolean </summary>
		/// <param name="value"> String to boolean </param>
		/// <param name="value"> Boolean value, in case original value fails to be parsed </param>
		/// <returns> Returns false by default </returns>
		
		try {
			// validate
			var val = EDRV2.trim(value).toLowerCase();			
			if (typeof(defaultVal) != 'boolean') { defaultVal == false; }
			
			switch (val) {
				case 'true':
				case '1':
				case 'yes':
					return true;
					break;
				case 'false':
				case '0':
				case 'no':
					return false;
					break;
				default:
					return defaultVal;
					break;
			}
			
			return defaultVal;
		}
		catch (e){
			return false;
		}
	},

	copyObjectData: function ( src, dest )
	{
		/// <summary>Copies value of properties from src to dest objects.</summary>
		/// <param name="src">Object to copy from.</param>
		/// <param name="dest">Object to copy to.</param>
		/// <remarks>This method will only copy properties with the same name (case sensitive).</remarks>

		// nothing to do
		if ( ( src == null ) || ( dest == null ) ) return dest;

		var propTypeOf = null;
		for ( var destProp in dest )
		{
			propTypeOf = typeof ( src[destProp] );
			if ( ( propTypeOf != 'undefined' ) && ( propTypeOf != 'function' ) ) dest[destProp] = src[destProp];
		}

		return dest;
	},

	bindFunction: function ( fn, context )
	{
		/// <summary>Binds function execution to a specific context.</summary>
		/// <param name="fn">Function (pointer) to be called.</param>
		/// <param name="context">Context to execute function with (null := global context).</param>
		/// <remarks>
		/// Function binding is useful when creating callback function (which is parameterless) with parameter
		/// and also callback function to execute under different context. See unit test page for more
		/// examples.
		/// </remarks>
		if ( fn == null ) return null;

		// remove the first 2 arguments passed in to this function (fn and context)
		// args contains additional parameters to this function
		var args = Array.prototype.slice.call( arguments, 2 );

		// create a closure - this is how function binding works!
		return function ()
		{
			var innerArgs = Array.prototype.slice.call( arguments );
			var finalArgs = args.concat( innerArgs );

			// .apply() executes the function by settings 2 things:
			// 1. the context the function is executed in (null = global)
			// 2. final parameters list
			return fn.apply( context, finalArgs );
		};
	},

	getEnumKeyFromValue: function ( enumTypes, enumValue )
	{
		/// <summary>Gets the key (or text) for the enum value</summary>
		/// <param name="enumTypes">The enumeration that the value is defined in</param>
		/// <param name="enumValue">The enum value to be used to search for the resulting key</param>

		//Loop the enum items to find a match, and then return the matching enumeration item name
		for ( var type in enumTypes )
		{
			if ( enumTypes[type] == enumValue ) { return type.toLowerCase(); } //Hey look, we found a match, so return it!
		}
	}

};
//ENUMERATIONS
EDRV2.EnumEventTypes = { REQUESTPOST: "REQUESTPOST", REQUESTGET: "REQUESTGET" };
EDRV2.EnumEventStatusTypes = { PROCESSING: "PROCESSING", COMPLETE: "COMPLETE", ERROR: "ERROR", TIMEOUT: "TIMEOUT", COMPLETEWITHERROR: "COMPLETEWITHERROR" };
/****************************************************
EDR general utilities (static functions).
*****************************************************/

/****************************************************
EDRV2.LOGGING utilities

Logging facility.
*****************************************************/
EDRV2.LOGGING =
{
	// application information (can be overriden by page)
	appInfo: { appName: '--UNKNOWN--', appVersion: '0.0.00' },
	
	// log severity
	SEVERITIES: { INFO: 'INFO', WARNING: 'WARNING', ERROR: 'ERROR', CRASHED: 'CRASHED' },
	
	log: function ( severity, brief, msg, elapsedInMS )
	{
		///<summary>Log message (will be expanded later to log to back end</summary>
		///<param name="severity">One of EDRV2.LOGGING.SEVERITIES values</param>
		///<param name="brief">Brief message</param>
		///<param name="msg">Detail message</param>
		///<param name="elapsedInMS">How long did the process take in milliseconds</param>

		try
		{
			console.log( EDRV2.LOGGING.appInfo.appName + ':' + severity + ':' + brief + '::' + msg );
		}
		catch ( e )
		{
			// ignore since we're just using console 
		}
	}
};

/****************************************************
EDRV2.LOGGING utilities
*****************************************************/

/****************************************************
EDRV2.HTTP utilities class.

Provides utilities for posting to URL.
*****************************************************/
EDRV2.HTTP =
{
	/* Provides enumerations for HTTP transmit status class. */
	EnumTransmitStatus: { UNKNOWN: 'EV2HTTPXMITUNK', TRANSMITSTART: 'EV2HTTPXMITSTART', TRANSMITCOMPLETE: 'EV2HTTPXMITUNKEND' },

	/*
	userAgent
		
	User agent to use when using HTTP request object.
	*/
	userAgent: 'Mozilla/5.0 (compatible; MSIE 9.0; EDR DVG JSLib;)',

	/*
	htmlReservedCharacters
	
	Reserved HTML chars.
	*/
	htmlReservedCharacters: { '&': '&amp;', '<': '&lt;', '>': '&gt;' },

	/*
	httpReqTimeout

	Request timeout for HTTP in milliseconds.
	*/
	httpReqTimeout: 45000,

	/*
		EDR Web application known hosts
	*/
	knownHosts: 	[
			{
				key: 'www.web.edrnet.com',
				hosts: [
					{ currentHost: 'www.web.edrnet.com', targetHost: 'www.web.edrnet.com' },
					{ currentHost: 'ws.edrnet.com', targetHost: 'www.web.edrnet.com' },
					{ currentHost: 'webdev.edrnet.com', targetHost: 'webdev.edrnet.com' },
					{ currentHost: 'wsdev.edrnet.com', targetHost: 'webdev.edrnet.com' },
					{ currentHost: 'webqa.edrnet.com', targetHost: 'webqa.edrnet.com' },
					{ currentHost: 'wsqa.edrnet.com', targetHost: 'webqa.edrnet.com' },
					{ currentHost: 'webstage.edrnet.com', targetHost: 'webstage.edrnet.com' },
					{ currentHost: 'wsstage.edrnet.com', targetHost: 'webstage.edrnet.com' },
					{ currentHost: 'stage.edrnet.com', targetHost: 'stage.edrnet.com' },
					{ currentHost: 'stagews.edrnet.com', targetHost: 'stage.edrnet.com' },
					{ currentHost: 'localhost', targetHost: 'localhost' }
				]
			},
			{
				key: 'ws.edrnet.com',
				hosts: [
					{ currentHost: 'www.web.edrnet.com', targetHost: 'ws.edrnet.com' },
					{ currentHost: 'ws.edrnet.com', targetHost: 'ws.edrnet.com' },
					{ currentHost: 'webdev.edrnet.com', targetHost: 'wsdev.edrnet.com' },
					{ currentHost: 'wsdev.edrnet.com', targetHost: 'wsdev.edrnet.com' },
					{ currentHost: 'webqa.edrnet.com', targetHost: 'wsqa.edrnet.com' },
					{ currentHost: 'wsqa.edrnet.com', targetHost: 'wsqa.edrnet.com' },
					{ currentHost: 'webstage.edrnet.com', targetHost: 'wsstage.edrnet.com' },
					{ currentHost: 'wsstage.edrnet.com', targetHost: 'wsstage.edrnet.com' },
					{ currentHost: 'stage.edrnet.com', targetHost: 'stagews.edrnet.com' },
					{ currentHost: 'stagews.edrnet.com', targetHost: 'stagews.edrnet.com' },
					{ currentHost: 'localhost', targetHost: 'localhost' }
				]
			}
	],

	translateHost: function ( targetProductionHost )
	{
		try
		{
			// validate
			if ( (typeof( targetProductionHost ) === 'undefined') || (targetProductionHost == null) )
			{
				EDRV2.LOGGING.log( EDRV2.LOGGING.SEVERITIES.WARNING, 'translateHost()', 'targetHost is undefined or null' );
				return null;
			}

			// 
			targetProductionHost = targetProductionHost.toLowerCase();
			var currentHost = window.location.host.toLowerCase();

			// find matching translation
			for ( var i = 0; i < EDRV2.HTTP.knownHosts.length; i++ )
			{
				if ( EDRV2.HTTP.knownHosts[i].key === targetProductionHost )
				{
					for ( var j = 0; j < EDRV2.HTTP.knownHosts[i].hosts.length; j++ )
					{
						if ( EDRV2.HTTP.knownHosts[i].hosts[j].currentHost === currentHost )
						{
							EDRV2.LOGGING.log( EDRV2.LOGGING.SEVERITIES.INFO, 'translateHost()', 'Found ' + targetProductionHost + ' translation for ' + currentHost + ' as ' + EDRV2.HTTP.knownHosts[i].hosts[j].targetHost );
							return EDRV2.HTTP.knownHosts[i].hosts[j].targetHost;
						}
					}
				}
			}

			// default to the passed in host
			EDRV2.LOGGING.log( EDRV2.LOGGING.SEVERITIES.WARNING, 'translateHost()', 'Unable to find translation for ' + targetProductionHost + ' on ' + currentHost );
			return targetProductionHost;
		}
		catch ( e )
		{
			EDRV2.LOGGING.log( EDRV2.LOGGING.SEVERITIES.ERROR, 'translateHost()', e.message );
			throw e;
		}
	},

	encodeHTMLReservedChar: function ( charToEncode )
	{
		/// <summary>Encodes HTML reserved chars.</summary>
		/// <param name="charToEncode">Character to encode.</summary>

		charToEncode = charToEncode || '';
		if ( charToEncode == '' ) return '';

		return EDRV2.HTTP.htmlReservedCharacters[charToEncode] || charToEncode;
	},

	htmlEncode: function ( html )
	{
		/// <summary>Encodes HTML reserved chars.</summary>
		/// <param name="html">HTML string to encode.</summary>

		// set to empty string if not specified
		html = html || '';
		if ( html == '' ) return '';

		return html.replace( /[&<>]/g, EDRV2.HTTP.encodeHTMLReservedChar );
	},

	/*
	IE MS XML types
	Priority is given to the lowest index.
	http://msdn.microsoft.com/en-us/library/windows/desktop/ms757837(v=vs.85).aspx
	*/
	ieMSXMLHTTPTypes: ['Msxml2.XMLHTTP.6.0', 'MSXML2.XMLHTTP.3.0', 'Microsoft.XMLHTTP'],

	/*
	IE MSXML XMLHTTP ProgID used.
	*/
	ieMSXMLHTTPProgID: null,

	/*
	IE MS XML types
	Priority is given to the lowest index.
	http://msdn.microsoft.com/en-us/library/windows/desktop/ms757837(v=vs.85).aspx
	*/
	createHTTPRequest: function ()
	{
		/// <summary>Creates HTTP request object.</summary>
		var httpReq = null;

		if ( window.XMLHttpRequest )
		{
			// new browsers
			httpReq = new XMLHttpRequest();
		}
		else if ( window.ActiveXObject )
		{
			// reset prog id
			EDRV2.HTTP.ieMSXMLHTTPProgID = null;

			// IE
			for ( var i = 0; i < EDRV2.HTTP.ieMSXMLHTTPTypes.length; i++ )
			{
				httpReq = null;

				try { httpReq = new ActiveXObject( EDRV2.HTTP.ieMSXMLHTTPTypes[i] ); } catch ( e ) { }

				if ( httpReq != null )
				{
					EDRV2.HTTP.ieMSXMLHTTPProgID = EDRV2.HTTP.ieMSXMLHTTPTypes[i];
					break;
				}
			}
		}

		return httpReq;
	},

	buildURL: function ( host, path, qryStrs, useDocProtocol )
	{
		try
		{
			// use current location to determine protocol + port
			var url = window.location.protocol + '//' + host;
			
			if ( parseInt(window.location.port) > 0) url += ':' + window.location.port
			
			url += path;

			// build query string
			if ( (qryStrs instanceof Array) && (qryStrs != null) && (qryStrs.length > 0) )
			{
				// append ? if needed
				if ( url.indexOf( '?' ) === -1 ) url += '?';

				for ( var i = 0; i < qryStrs.length; i++ )
				{
					url += '&' + qryStrs[i].name + '=' + encodeURIComponent( qryStrs[i].value );
				}
			}

			// done
			return url;
		}
		catch ( e )
		{
			EDRV2.LOGGING.log( EDRV2.LOGGING.SEVERITIES.ERROR, 'urlService.buildURL()', e.message );
			throw e;
		}
	},
		
	switchURLToHTTPS: function ( httpURL, forceTheSameAsPage )
	{
		/// <summary>Switch URL protocol to HTTPS if neccessary.</summary>
		/// <param name="httpURL">URL (full or relative).</param>
		/// <param name="forceTheSameAsPage">True to force the URL to be the same as the page, False to only switch to HTTPS and not to HTTP.</param>

		try
		{
			// set forceTheSameAsPage to False
			if ( ( typeof ( forceTheSameAsPage ) == 'undefined' ) || ( forceTheSameAsPage == null ) ) forceTheSameAsPage = false;

			// trick to build full path URL
			var aLink = document.createElement( 'A' );
			aLink.href = httpURL;

			// check protocol
			var tgtIsSSL = false;

			if ( aLink.protocol.toLowerCase() == 'https:' ) tgtIsSSL = true;

			delete aLink;

			// check page protocol
			var curIsSSL = false;

			if ( window.location.protocol.toLowerCase() == 'https:' ) curIsSSL = true;

			// only have to handle if protocol is not the same
			if ( tgtIsSSL != curIsSSL )
			{
				if ( curIsSSL )
				{
					// target is not SSL - switch it
					httpURL = httpURL.replace( /http:/gi, 'https:' );
				}
				else if ( forceTheSameAsPage )
				{
					// target is SSL but not the page and we are switching it because it is requested for us to switch
					httpURL = httpURL.replace( /https:/gi, 'http:' );
				}
			}

			return httpURL;
		}
		catch ( e )
		{
			throw new Error( 'Unable to switch URL to HTTPS: ' + e.message );
		}
	},

	isTargetURLCrossDomain: function ( targetURL )
	{
		/// <summary>Returns whether target URL will go cross-domain (relative to edrnet.com).</summary>
		/// <param name="targetURL">URL to post to.</summary>

		var ref = null;

		try
		{
			// validation
			targetURL = EDRV2.trim( targetURL );

			if ( targetURL == '' ) return false;

			// get current location
			var curHost = window.location.hostname.toLowerCase();

			// easy way to parse URL
			ref = document.createElement( "a" );
			ref.href = targetURL;

			var destHost = ref.hostname.toLowerCase();

			return !( ( destHost == '' ) || ( curHost == destHost ) );
		}
		catch ( e )
		{
			throw new Error( 'Unable to determine if target URL is cross-domain: ' + e.message );
		}
		finally
		{
			if ( ref != null )
			{
				delete ref;
				ref = null;
			}
		}
	},

	hasIEXDR: function ()
	{
		/// <summary>Returns whether this browser is IE w/ XDomainRequest object.</summary>
		return ( ( typeof ( window.XDomainRequest ) != 'undefined' ) && ( window.XDomainRequest != null ) );
	},

	loadScript: function ( url, cb, scripTitle )
	{
		/// <summary>Loads JavaScript dynamically.</summary>
		/// <param name="url">Javascript URL.</param>
		/// <param name="cb">Callback when script is loaded.</param>
		/// <param name="scripTitle">Title of the script to display on status.</param>
		try
		{
			// display msg
			scripTitle = scripTitle || 'JS script';

			// setup callback
			if ( typeof ( cb ) == 'undefined' ) cb = null;

			// load up script
			var scp = document.createElement( 'script' );
			scp.type = 'text/javascript';

			// Attach handlers for all browsers 
			// not using scp.onload because IE 8 and below does not support it
			// but all browsers support onreadystatechange().
			if ( cb != null )
			{
				// Handle Script loading 
				var done = false;

				scp.onload = scp.onreadystatechange = function ()
				{
					if ( !done && ( !this.readyState || this.readyState === "loaded" || this.readyState === "complete" ) )
					{
						done = true;

						cb();

						// Handle memory leak in IE 
						scp.onload = scp.onreadystatechange = null;
						if ( scp.parentNode )
						{
							scp.parentNode.removeChild( scp );
						}
					}

				}
			}

			scp.async = true;

			// switch URL to use the correct protocol
			scp.src = url;

			document.body.appendChild( scp );
		}
		catch ( e )
		{
			throw e;
		}

		return true;
	},

	requestGet: function ( url, execOnAsynchComplete, asynchData, suppressEvent, requestID )
	{
		/// <summary>Post to URL using GET method.</summary>
		/// <param name="url">URL to post to.</summary>
		/// <param name="execOnAsynchComplete">Function pointer for callback method (asynch) - params must be (response) Ex. function setData(resp){...}</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			//Set our asynch indicator
			var isAsynchRequested = false;
			if ( ( typeof ( execOnAsynchComplete ) != 'undefined' ) && ( execOnAsynchComplete != null ) ) { isAsynchRequested = true; }

			// delegate to IE8+ XDomainRequest of this will be one
			if ((EDRV2.HTTP.hasIEXDR()) && (EDRV2.HTTP.isTargetURLCrossDomain(url)) && (isAsynchRequested))
			{
				return EDRV2.HTTP.requestGetIEXDR(url, execOnAsynchComplete, asynchData, suppressEvent, requestID)
			}

			//Prep
			if ( ( typeof ( suppressEvent ) == 'undefined' ) || ( suppressEvent == null ) ) { suppressEvent = false; }

			//Notify
			if ( !suppressEvent )
			{
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null } );
			}

			// get HTTP req object
			var httpReq = EDRV2.HTTP.createHTTPRequest();
			if ( httpReq == null ) throw new Error( 'Unable execute HTTP GET: Unable to create HTTP request object.' );

			var usrAgent = navigator.userAgent || EDRV2.HTTP.userAgent;

			//Setup up the ready state change event handler if asynch
			if ( isAsynchRequested )
			{
				httpReq.onreadystatechange = function ()
				{
					try
					{
						/*
							http://www.w3schools.com/ajax/ajax_xmlhttprequest_onreadystatechange.asp
							readyState:
							0: request not initialized 
							1: server connection established
							2: request received 
							3: processing request 
							4: request finished and response is ready
						*/
						if ( httpReq.readyState == 4 )
						{
							if ( httpReq.status >= 200 && httpReq.status < 300 || httpReq.status == 304 )
							{
								// parse content type
								var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

								// retrieve data
								var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText, contextData: asynchData };

								delete httpReq;
								httpReq = null;

								//Notify that the post request is complete                                                       
								if ( !suppressEvent )
								{
									EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp } );
								}

								//Execute the callback function 
								execOnAsynchComplete( resp );
							}
							else
							{
								var msg = 'HTTP Status: ' + httpReq.status + ' (' + httpReq.responseText + ')';

								delete httpReq;
								httpReq = null;

								throw new Error( msg );
							}
						}
						else
						{
							// request being process
							if ( !suppressEvent )
							{
								EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null } );
							}
						}
					}
					catch ( err )
					{
						if ( !suppressEvent )
						{
							EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: err } );
						}
						else
						{
							// since this is an async call - throwing error will break the UI app
							// so lets just alert the error since caller suppressed event
							alert( '[EDRJSLIB-ERR] Unable to process HTTP GET: ' + err.message );
						}
					}
				}
			}

			// post to URL
			httpReq.open( 'GET', url, isAsynchRequested );
			httpReq.setRequestHeader( 'User-Agent', usrAgent );
			httpReq.send( null );

			if ( !isAsynchRequested )
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText };

				delete httpReq;
				httpReq = null;

				if ( !suppressEvent )
				{
					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp } );
				}

				return resp;
			}
			else
			{
				// because this is async call - just return back to caller w/ no information
				return;
			}
		}
		catch ( e )
		{
			if ( !suppressEvent )
			{
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: e } );
			}

			// since this is sync call - throw exception as well
			throw e;
		}
	},

	requestGetIEXDR: function ( url, execOnAsynchComplete, asynchData, suppressEvent, requestID )
	{
		/// <summary>Post to URL using GET method (using XDomainRequest - supports async).</summary>
		/// <param name="url">URL to post to.</param>
		/// <param name="execOnAsynchComplete">Function pointer for callback method (asynch) - params must be (response) Ex. function setData(resp){...}</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			// check if XDomainRequest object exists
			if ( ( typeof ( window.XDomainRequest ) == 'undefined' ) || ( window.XDomainRequest == null ) )
			{
				throw new Error( 'XDomainReqeuest is not available on this browser.' );
			}

			//Set our asynch indicator
			if ( ( typeof ( execOnAsynchComplete ) == 'undefined' ) || ( execOnAsynchComplete == null ) )
			{
				throw new Error( 'XDomainRequest requires callback.' );
			}

			//Prep
			if ( ( typeof ( suppressEvent ) == 'undefined' ) || ( suppressEvent == null ) ) { suppressEvent = false; }

			//Notify
			if ( !suppressEvent )
			{
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null } );
			}

			// get HTTP req object
			var httpReq = new window.XDomainRequest();

			// onload - call as successful
			httpReq.onload = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				delete httpReq;
				httpReq = null;

				//Notify that the post request is complete                                                       
				if ( !suppressEvent )
				{
					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp } );
				}

				//Execute the callback function 
				execOnAsynchComplete( resp );
			};

			// onerror - error calling server
			httpReq.onerror = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is complete                                                       
				if ( !suppressEvent )
				{
					var err = new Error( 'HTTP Status: ' + httpReq.status );

					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: err } );
				}

				delete httpReq;
				httpReq = null;

				//Execute the callback function 
				execOnAsynchComplete( resp );
			};

			// ontimeout - timeout calling server
			httpReq.ontimeout = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is complete                                                       
				if ( !suppressEvent )
				{
					var err = new Error( 'HTTP Status: ' + httpReq.status );

					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.TIMEOUT, requestID: requestID, contextData: asynchData, data: err } );
				}

				delete httpReq;
				httpReq = null;

				//Execute the callback function 
				execOnAsynchComplete( resp );
			};

			// onprogress
			httpReq.onprogress = function ()
			{
				//Notify that the post request is complete                                                       
				if ( !suppressEvent ) { EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData } ); }
			};

			// post to URL
			httpReq.timeout = EDRV2.HTTP.httpReqTimeout;
			httpReq.open( 'GET', url );
			window.setTimeout( function () { httpReq.send(); }, 0 );
		}
		catch ( e )
		{
			if ( !suppressEvent ) { EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: e } ); }
			throw e;
		}
	},

	requestPost: function ( url, data, fullContentType, execOnAsynchComplete, asynchData, suppressEvent, requestID )
	{
		/// <summary>Post to URL using POST method.</summary>
		/// <param name="url">URL to post to.</param>
		/// <param name="data">Data to post.</param>
		/// <param name="fullContentType">Content type (if null application/x-www-form-urlencoded will be used.</param>
		/// <param name="execOnAsynchComplete">Function pointer for callback method (asynch) - params must be (response) Ex. function setData(resp){...}</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			//Set our asynch indicator
			var isAsynchRequested = false;
			if ( ( typeof ( execOnAsynchComplete ) != 'undefined' ) && ( execOnAsynchComplete != null ) ) { isAsynchRequested = true; }

			// delegate to IE8+ XDomainRequest of this will be one
			if ( ( EDRV2.HTTP.hasIEXDR() ) && ( EDRV2.HTTP.isTargetURLCrossDomain( url ) ) && ( isAsynchRequested ) )
			{
				return EDRV2.HTTP.requestPostIEXDR( url, data, fullContentType, execOnAsynchComplete, asynchData, suppressEvent, requestID )
			}

			//Prep
			if ( ( typeof ( suppressEvent ) == 'undefined' ) || ( suppressEvent == null ) ) { suppressEvent = false; }

			//Notify
			if ( !suppressEvent )
			{
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null } );
			}

			// get HTTP req object
			var httpReq = EDRV2.HTTP.createHTTPRequest();
			if ( httpReq == null ) throw new Error( 'Unable to execute HTTP POST: Unable to create HTTP request object.' );

			//Setup up the ready state change event handler if asynch
			if ( isAsynchRequested )
			{
				httpReq.onreadystatechange = function ()
				{
					try
					{
						/*
							http://www.w3schools.com/ajax/ajax_xmlhttprequest_onreadystatechange.asp
							readyState:
							0: request not initialized 
							1: server connection established
							2: request received 
							3: processing request 
							4: request finished and response is ready
						*/
						if ( httpReq.readyState == 4 )
						{
							if ( httpReq.status >= 200 && httpReq.status < 300 || httpReq.status == 304 )
							{
								// parse content type
								var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

								// retrieve data
								var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText, contextData: asynchData };

								delete httpReq;
								httpReq = null;

								//Notify that the post request is complete                                                       
								if ( !suppressEvent )
								{
									EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp } );
								}

								//Execute the callback function 
								execOnAsynchComplete( resp );
							}
							else
							{
								throw new Error( "HTTP Status: " + httpReq.status );
							}
						}
						else
						{
							// processing request
							if ( !suppressEvent )
							{
								EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null } );
							}
						}
					}
					catch ( err )
					{
						if ( !suppressEvent )
						{
							EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: err } );
						}
						else
						{
							// since this is an async call - throwing error will break the UI app
							// so lets just alert the error since caller suppressed event
							alert( '[EDRJSLIB-ERR] Unable to process HTTP POST: ' + err.message );
						}
					}
				}
			}

			// post to URL
			httpReq.open( 'POST', url, isAsynchRequested );

			var usrAgent = navigator.userAgent || EDRV2.HTTP.userAgent;
			//httpReq.setRequestHeader( 'User-Agent', usrAgent );
			//httpReq.setRequestHeader( 'Origin', window.location.host );

			if ( fullContentType )
				httpReq.setRequestHeader( 'Content-Type', fullContentType );
			else
				httpReq.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );

			//if ( data )
			//	httpReq.setRequestHeader( 'Content-Length', data.length );
			//else
			//	httpReq.setRequestHeader( 'Content-Length', 0 );

			httpReq.send( data );

			if ( !isAsynchRequested )
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText };

				delete httpReq;
				httpReq = null;

				if ( !suppressEvent )
				{
					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp } );
				}

				return resp;
			}
			else
			{
				// this is async call - return nothing to caller
				return;
			}
		}
		catch ( e )
		{
			if ( !suppressEvent )
			{
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: e } );
			}

			throw e;
		}
	},

	requestPostIEXDR: function ( url, data, fullContentType, execOnAsynchComplete, asynchData, suppressEvent, requestID )
	{
		/// <summary>Post to URL using POST method (using XDomainRequest - supports async).</summary>
		/// <param name="url">URL to post to.</param>
		/// <param name="data">Data to post.</param>
		/// <param name="fullContentType">Content type (if null application/x-www-form-urlencoded will be used.</param>
		/// <param name="execOnAsynchComplete">Function pointer for callback method (asynch) - params must be (response) Ex. function setData(resp){...}</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			// check if XDomainRequest object exists
			if ( ( typeof ( window.XDomainRequest ) == 'undefined' ) || ( window.XDomainRequest == null ) )
			{
				throw new Error( 'XDomainReqeuest is not available on this browser.' );
			}

			//Set our asynch indicator
			if ( ( typeof ( execOnAsynchComplete ) == 'undefined' ) || ( execOnAsynchComplete == null ) )
			{
				throw new Error( 'XDomainRequest requires callback.' );
			}

			//Prep
			if ( ( typeof ( suppressEvent ) == 'undefined' ) || ( suppressEvent == null ) ) { suppressEvent = false; }

			//Notify
			if ( !suppressEvent )
			{
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null } );
			}

			// get HTTP req object
			var httpReq = new window.XDomainRequest();

			// onload - call as successful
			httpReq.onload = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				delete httpReq;
				httpReq = null;

				//Notify that the post request is complete                                                       
				if ( !suppressEvent )
				{
					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp } );
				}

				//Execute the callback function 
				execOnAsynchComplete( resp );
			};

			// onerror - error calling server
			httpReq.onerror = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				delete httpReq;
				httpReq = null;

				//Notify that the post request is complete                                                       
				if ( !suppressEvent )
				{
					var err = new Error( 'HTTP Status: ' + httpReq.status );

					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: err } );
				}

				//Execute the callback function 
				execOnAsynchComplete( resp );
			};

			// ontimeout - timeout calling server
			httpReq.ontimeout = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is complete                                                       
				if ( !suppressEvent )
				{
					var err = new Error( 'HTTP Status: ' + httpReq.status );

					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.TIMEOUT, requestID: requestID, contextData: asynchData, data: err } );
				}

				delete httpReq;
				httpReq = null;

				//Execute the callback function 
				execOnAsynchComplete( resp );
			};

			// onprogress
			httpReq.onprogress = function ()
			{
				//Notify that the post request is processing                                                       
				if ( !suppressEvent )
				{
					EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null } );
				}
			};

			// post to URL
			httpReq.timeout = EDRV2.HTTP.httpReqTimeout;
			httpReq.open( 'POST', url );

			// this is a workaround because sometimes IE does not work properly
			// if .send() is called right away
			window.setTimeout( function () { httpReq.send( data ); }, 10 );
		}
		catch ( e )
		{
			if ( !suppressEvent ) { EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: e } ); }
			throw e;
		}
	},

	requestGetV2: function ( url, useAsyncCall, asynchData, requestID )
	{
		/// <summary>Post to URL using GET method (responses triggered via EDRV2.EventCollector).</summary>
		/// <param name="url">URL to post to.</summary>
		/// <param name="useAsyncCall">True to make asynscronous request, False otherwise.</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			//Set our asynch indicator
			var isAsynchRequested = false;
			if ( ( typeof ( useAsyncCall ) != 'undefined' ) && ( useAsyncCall != null ) ) { isAsynchRequested = useAsyncCall; }

			// delegate to IE8+ XDomainRequest of this will be one
			// AUJ: GET does not cause cross-domain scripting security and since XMLHttpRequest object
			// provides better error report - may as well use that
			if ( ( EDRV2.HTTP.hasIEXDR() ) && ( EDRV2.HTTP.isTargetURLCrossDomain( url ) ) && ( isAsynchRequested ) )
			{
				//return EDRV2.HTTP.requestGetIEXDRV2( url, asynchData, requestID );
			}

			//Notify
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );

			// get HTTP req object
			var httpReq = EDRV2.HTTP.createHTTPRequest();
			if ( httpReq == null ) throw new Error( 'Unable execute HTTP GET: Unable to create HTTP request object.' );

			var usrAgent = navigator.userAgent || EDRV2.HTTP.userAgent;

			//Setup up the ready state change event handler if asynch
			if ( isAsynchRequested )
			{
				httpReq.onreadystatechange = function ()
				{
					try
					{
						/*
							http://www.w3schools.com/ajax/ajax_xmlhttprequest_onreadystatechange.asp
							readyState:
							0: request not initialized 
							1: server connection established
							2: request received 
							3: processing request 
							4: request finished and response is ready
						*/
						if ( httpReq.readyState == 4 )
						{
							// parse content type
							var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

							// retrieve data
							var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText, contextData: asynchData };

							if ( httpReq.status >= 200 && httpReq.status < 300 || httpReq.status == 304 )
							{
								//Notify that the post request is complete                                                       
								EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp, error: null, httpStatus: httpReq.status } );

								delete httpReq;
								httpReq = null;
							}
							else
							{
								// got error
								var err = new Error( httpReq.status.toString() + ' (' + httpReq.statusText + ')' );

								EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETEWITHERROR, requestID: requestID, contextData: asynchData, data: resp, error: err, httpStatus: httpReq.status } );

								delete httpReq;
								httpReq = null;
							}
						}
						else
						{
							// request being process
							EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );
						}
					}
					catch ( err )
					{
						EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: null, error: err, httpStatus: null } );
					}
				}
			}

			// post to URL
			httpReq.open( 'GET', url, isAsynchRequested );
			httpReq.setRequestHeader( 'User-Agent', usrAgent );

			httpReq.send( null );

			if ( !isAsynchRequested )
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText };

				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp, error: null, httpStatus: httpReq.status } );

				delete httpReq;
				httpReq = null;

				return resp;
			}
			else
			{
				// because this is async call - just return back to caller w/ no information
				return;
			}
		}
		catch ( e )
		{
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: null, error: e, httpStatus: null } );
		}
	},

	requestGetIEXDRV2: function ( url, asynchData, requestID )
	{
		/// <summary>Post URL asynchronously using GET method using XDomainRequest (responses triggered via EDRV2.EventCollector).</summary>
		/// <param name="url">URL to post to.</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			// check if XDomainRequest object exists
			if ( ( typeof ( window.XDomainRequest ) == 'undefined' ) || ( window.XDomainRequest == null ) )
			{
				throw new Error( 'XDomainReqeuest is not available on this browser.' );
			}

			//Notify
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );

			// get HTTP req object
			var httpReq = new window.XDomainRequest();

			// onload - call as successful
			httpReq.onload = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is complete                                                       
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp, error: null, httpStatus: httpReq.status } );

				delete httpReq;
				httpReq = null;
			};

			// onerror - error calling server
			httpReq.onerror = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is has error 
				var err = new Error( 'Server returned cross-domain scripting error (MSIE)' );

				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.COMPLETEWITHERROR, requestID: requestID, contextData: asynchData, data: resp, error: err, httpStatus: httpReq.status } );

				delete httpReq;
				httpReq = null;
			};

			// ontimeout - timeout calling server
			httpReq.ontimeout = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is complete                                                       
				var err = new Error( 'Request timed-out' );

				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.TIMEOUT, requestID: requestID, contextData: asynchData, data: resp, error: err, httpStatus: httpReq.status } );

				delete httpReq;
				httpReq = null;
			};

			// onprogress
			httpReq.onprogress = function ()
			{
				//Notify that the post request is in progres                                                       
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );
			};

			// post to URL
			httpReq.timeout = EDRV2.HTTP.httpReqTimeout;
			httpReq.open( 'GET', url );
			window.setTimeout( function () { httpReq.send(); }, 0 );
		}
		catch ( e )
		{
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTGET, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: null, error: e, httpStatus: null } );
		}
	},

	requestPostV2: function ( url, data, fullContentType, useAsyncCall, asynchData, requestID )
	{
		/// <summary>Post to URL using POST method (responses triggered via EDRV2.EventCollector).</summary>
		/// <param name="url">URL to post to.</param>
		/// <param name="data">Data to post.</param>
		/// <param name="fullContentType">Content type (if null application/x-www-form-urlencoded will be used.</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			//Set our asynch indicator
			var isAsynchRequested = false;
			if ( ( typeof ( useAsyncCall ) != 'undefined' ) && ( useAsyncCall != null ) ) { isAsynchRequested = useAsyncCall; }

			// delegate to IE8+ XDomainRequest of this will be one
			// AUJ: (Oct 1st 2013) MS must have updated XMLHttpRequest object to handle cross-domain scripting security and since it
			// provides better error report - may as well use that
			if ( ( EDRV2.HTTP.hasIEXDR() ) && ( EDRV2.HTTP.isTargetURLCrossDomain( url ) ) && ( isAsynchRequested ) )
			{
				//return EDRV2.HTTP.requestPostIEXDRV2( url, data, asynchData, requestID );
			}

			//Notify
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );

			// get HTTP req object
			var httpReq = EDRV2.HTTP.createHTTPRequest();
			if ( httpReq == null ) throw new Error( 'Unable to execute HTTP POST: Unable to create HTTP request object.' );

			//Setup up the ready state change event handler if asynch
			if ( isAsynchRequested )
			{
				httpReq.onreadystatechange = function ()
				{
					try
					{
						/*
							http://www.w3schools.com/ajax/ajax_xmlhttprequest_onreadystatechange.asp
							readyState:
							0: request not initialized 
							1: server connection established
							2: request received 
							3: processing request 
							4: request finished and response is ready
						*/
						if ( httpReq.readyState == 4 )
						{
							// parse content type
							var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

							// retrieve data
							var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText, contextData: asynchData };

							if ( httpReq.status >= 200 && httpReq.status < 300 || httpReq.status == 304 )
							{
								//Notify that the post request is complete                                                       
								EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp, error: null, httpStatus: httpReq.status } );

								delete httpReq;
								httpReq = null;
							}
							else
							{
								// got error
								var err = new Error( httpReq.status.toString() + ' (' +  httpReq.statusText + ')' );

								EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETEWITHERROR, requestID: requestID, contextData: asynchData, data: resp, error: err, httpStatus: httpReq.status } );

								delete httpReq;
								httpReq = null;
							}
						}
						else
						{
							// processing
							EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );
						}
					}
					catch ( err )
					{
						// error while handling HTTP async callback
						EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: null, error: err, httpStatus: null } );
					}
				}
			}

			// post to URL
			httpReq.open( 'POST', url, isAsynchRequested );

			var usrAgent = navigator.userAgent || EDRV2.HTTP.userAgent;
			httpReq.setRequestHeader( 'User-Agent', usrAgent );
			httpReq.setRequestHeader( 'Origin', window.location.host );

			if ( fullContentType )
				httpReq.setRequestHeader( 'Content-Type', fullContentType );
			else
				httpReq.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );

			if ( data )
				httpReq.setRequestHeader( 'Content-Length', data.length );
			else
				httpReq.setRequestHeader( 'Content-Length', 0 );

			httpReq.send( data );

			if ( !isAsynchRequested )
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.getResponseHeader( 'Content-Type' ) );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: httpReq.getResponseHeader( 'Content-Length' ), data: httpReq.responseText };

				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp, error: null, httpStatus: httpReq.status } );

				delete httpReq;
				httpReq = null;

				return resp;
			}
			else
			{
				// this is async call - return nothing to caller
				return;
			}
		}
		catch ( e )
		{
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: null, error: e, httpStatus: null } );
		}
	},

	requestPostIEXDRV2: function ( url, data, asynchData, requestID )
	{
		/// <summary>Post URL asynchronously using POST method using XDomainRequest (responses triggered via EDRV2.EventCollector).</summary>
		/// <param name="url">URL to post to.</param>
		/// <param name="data">Data to post.</param>
		/// <param name="asynchData">The data that is to be attached to the callback for asynch requests</param>
		/// <param name="requestID">Request ID (to pass back to caller via EventCollector).</param>

		try
		{
			// check if XDomainRequest object exists
			if ( ( typeof ( window.XDomainRequest ) == 'undefined' ) || ( window.XDomainRequest == null ) )
			{
				throw new Error( 'XDomainReqeuest is not available on this browser.' );
			}

			//Notify
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );

			// get HTTP req object
			var httpReq = new window.XDomainRequest();

			// onload - call as successful
			httpReq.onload = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is complete                                                       
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETE, requestID: requestID, contextData: asynchData, data: resp, error: null, httpStatus: null } );

				delete httpReq;
				httpReq = null;
			};

			// onerror - error calling server
			httpReq.onerror = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is has error 
				var err = new Error( 'Server returned cross-domain scripting error (MSIE)' );

				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.COMPLETEWITHERROR, requestID: requestID, contextData: asynchData, data: resp, error: err, httpStatus: httpReq.status } );

				delete httpReq;
				httpReq = null;
			};

			// ontimeout - timeout calling server
			httpReq.ontimeout = function ()
			{
				// parse content type
				var contentType = EDRV2.HTTP.parseContentType( httpReq.contentType );

				// retrieve data
				var resp = { contentType: contentType.contentType, encodingType: contentType.encodingType, contentLength: -1, data: httpReq.responseText, contextData: asynchData };

				//Notify that the post request is complete                                                       
				var err = new Error( 'Request timed-out' );

				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.TIMEOUT, requestID: requestID, contextData: asynchData, data: resp, error: err, httpStatus: httpReq.status } );

				delete httpReq;
				httpReq = null;
			};

			// onprogress
			httpReq.onprogress = function ()
			{
				//Notify that the post request is processing                                                       
				EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.PROCESSING, requestID: requestID, contextData: asynchData, data: null, error: null, httpStatus: null } );
			};

			// post to URL
			httpReq.timeout = EDRV2.HTTP.httpReqTimeout;
			httpReq.open( 'POST', url );

			// this is a workaround because sometimes IE does not work properly
			// if .send() is called right away
			window.setTimeout( function () { httpReq.send( data ); }, 10 );
		}
		catch ( e )
		{
			EDRV2.EventCollector.fire( { type: EDRV2.EnumEventTypes.REQUESTPOST, status: EDRV2.EnumEventStatusTypes.ERROR, requestID: requestID, contextData: asynchData, data: null, error: err, httpStatus: null } );
		}
	},

	parseContentType: function ( contentType )
	{
		/// <summary>Parse value from Content-Type header.</summary>
		/// <param name="contentType">Value from Content-Type header.</param>

		// resp object
		var resp = { contentType: null, encodingType: null };

		if ( contentType == null ) return resp;

		// split by ;
		var tokens = contentType.split( ';' );

		resp.contentType = tokens[0];
		resp.encodingType = tokens[1];

		return resp;
	},

	createDataString: function ( nameValuePairs )
	{
		/// <summary>Creates the data string that can be used to send to httphandler</summary>
		/// <param name="nameValuePairs">JSON objects consisting of name / value properties</param>
		var result = '';
		for ( var i = 0; i < nameValuePairs.length; i++ )
		{
			if ( i > 0 ) result += '&';
			result += nameValuePairs[i].name + '=' + nameValuePairs[i].value;
		}
		return result;
	},

	createDataStringWithURL: function ( url, nameValuePairs )
	{
		/// <summary>Creates the data string that can be used to send to httphandler - will examine url parameters if present</summary>
		/// <param name="nameValuePairs">JSON objects consisting of name / value properties</param>

		//Validate and prep
		if ( url == null ) { return ""; }
		url = EDRV2.trim( url );
		var finalNameValuePairs = [];
		var finalURLWithParams = '';
		if ( nameValuePairs == null ) { nameValuePairs = []; }

		//Parse URL and see if we need to add the items to the nameValuePairs array
		var queryString = url.split( "?" );
		var params = [];
		if ( queryString.length == 2 ) { params = queryString[1].split( "&" ); }
		var param = [];
		var paramToAdd = null;
		var itemPresent = false;
		for ( var i = 0; i < params.length; i++ )
		{
			//If it is not already in the nameValuePair listing then add it
			param = params[i].split( "=" );
			if ( param.length == 2 )
			{
				paramToAdd = ( { name: param[0], value: param[1] } );
				itemPresent = false;
				for ( var j = 0; j < nameValuePairs.length; j++ )
				{
					if ( paramToAdd.name == nameValuePairs[j].name )
					{
						//Item present in the nameValuePairs so we can just exit
						itemPresent = true;
						break;
					}
				}
				if ( !itemPresent ) { finalNameValuePairs.push( paramToAdd ); } //Not in there, so we need to add it to our url array						
			}
		}

		//Now build the final url with the parameters (specified nameValuePairs will override current url params if both are present
		for ( var i = 0; i < nameValuePairs.length; i++ )
		{
			finalNameValuePairs.push( nameValuePairs[i] );
		}

		//Build the param string
		var paramString = EDRV2.HTTP.createDataString( finalNameValuePairs );
		finalURLWithParams = queryString[0];
		if ( paramString.length > 0 ) { finalURLWithParams += '?'; }
		finalURLWithParams += paramString;

		//Build and return the final url with params
		return finalURLWithParams;
	}

};
/****************************************************
EDRV2.HTTP utilities class.
*****************************************************/

/****************************************************
EDRV2.XML utilities class.

Provides utilities for working w/ XML.
*****************************************************/
EDRV2.XML =
{
	/*
	IE MS XML types
	Priority is given to the lowest index.
	http://msdn.microsoft.com/en-us/library/windows/desktop/ms757837(v=vs.85).aspx
	*/
	ieMSXMLTypes: ['Msxml2.DOMDocument.6.0', 'MSXML2.DOMDocument.3.0', 'Microsoft.XMLDOM'],

	/*
	IE MSXML XML ProgID used.
	*/
	ieMSXMLProgID: null,

	fromString: function ( xmlString )
	{
		/// <summary>Returns xmlString as XmlDocument object.</summary>
		/// <param name="xmlString">Xml formatted string data.</param>
		try
		{
			var parser = null;

			if ( window.ActiveXObject )
			{
				// IE
				// reset prog id
				EDRV2.XML.ieMSXMLProgID = null;

				// IE
				for ( var i = 0; i < EDRV2.XML.ieMSXMLTypes.length; i++ )
				{
					parser = null;

					try { parser = new ActiveXObject( EDRV2.XML.ieMSXMLTypes[i] ); } catch ( e ) { }

					if ( parser != null )
					{
						EDRV2.XML.ieMSXMLProgID = EDRV2.XML.ieMSXMLTypes[i];
						break;
					}
				}

				if ( parser != null )
				{
					parser.async = false;
					parser.loadXML( xmlString );
					return parser;
				}
			}
			else if ( window.DOMParser )
			{
				// Mozilla
				parser = new DOMParser();
				return parser.parseFromString( xmlString, 'text/xml' );
			}

			// nothing found
			throw new Error( 'Unable to load XmlDocument: Unable to create Xml parser object.' );
		}
		catch ( e )
		{
			throw e;
		}
	},

	fromHTTPGet: function ( url )
	{
		/// <summary>Returns response from URL as XmlDocument.</summary>
		/// <param name="url">URL to post to.</param>

		try
		{
			// get data
			var resp = EDRV2.HTTP.requestGet( url );

			if ( resp.data == '' )
				throw new Error( 'Unable to load XmlDocument (HTTP GET): Server did not return any data.' );
			else
				return EDRV2.XML.fromString( resp.data ); // return XmlDoc
		}
		catch ( e )
		{
			throw e;
		}
	},

	fromHTTPPost: function ( url, data, contentType )
	{
		/// <summary>Returns response from URL as XmlDocument.</summary>
		/// <param name="url">URL to post to.</summary>
		/// <param name="data">Data to post.</summary>
		/// <param name="fullContentType">Content type (if null application/x-www-form-urlencoded will be used.</summary>

		try
		{
			// get data
			var resp = EDRV2.HTTP.requestPost( url, data, contentType );

			if ( resp.data == '' )
				throw new Error( 'Unable to load XmlDocument (HTTP POST): Server did not return any data.' );
			else
				return EDRV2.XML.fromString( resp.data ); // return XmlDoc
		}
		catch ( e )
		{
			throw e;
		}
	},

	createXPathEvaluator: function ()
	{
		/// <summary>Returns XPath evaluator (for X-path query).</summary>
		try
		{
			return new XPathEvaluator();
		}
		catch ( ex )
		{
			throw ex;
		}
	},

	serializeXML: function ( xmlDoc )
	{
		/// <summary>Returns Xml string representation of XmlDocument.</summary>
		/// <param name="xmlDoc">XmlDocument to be serialized.</param>

		try
		{
			// return empty string
			if ( xmlDoc == null ) return '';

			if ( window.XMLSerializer )
			{
				// Mozilla and others (IE 9 supports the interface but
				// does not implement the function
				try
				{
					var ser = new XMLSerializer();
					return ser.serializeToString( xmlDoc.documentElement );
				}
				catch ( e )
				{
				}
			}

			if ( xmlDoc.xml )
			{
				// IE
				return xmlDoc.xml;
			}

			// at this point nothing else we can do
			throw Error( 'Unable to serialize XML: Browser does not support interface.' );
		}
		catch ( e )
		{
			throw e;
		}
	}
};
/****************************************************
EDRV2.XML utilities class.
*****************************************************/

/****************************************************
EDRV2.VALIDATION utilities class.

Provides basic validations utility.
*****************************************************/
EDRV2.VALIDATION =
{
	isValidEmailSyntax: function ( email )
	{
		/// <summary>Returns whether email has a valid syntax.</summary>
		/// <param name="email">Email to validate.</summary>

		//Preconditions
		email = EDRV2.trim( email || '' );
		if ( email == '' ) return false;

		//Regex matching		
		if ( email.match( /\s/ ) != null ) { return false; } //White space test
		if ( email.match( /[\.]{2}|[\-]{2}/ ) != null ) { return false; } //Multiple .. or --
		if ( email.match( /^(([A-Za-z0-9]+_+)|([A-Za-z0-9]+\-+)|([A-Za-z0-9]+\.+)|([A-Za-z0-9]+\++))*[A-Za-z0-9]+@((\w+\-+)|(\w+\.))*\w{1,63}\.[a-zA-Z]{2,6}$/ ) == null ) { return false; } //Invalid email syntax

		return true;  //Valid
	},
	isValidMultipleEmailSyntax: function ( emails )
	{
		/// <summary>Returns whether emails have a valid syntax.</summary>
		/// <param name="email">Emails to validate.</summary>

		//NOTE: comma delimited emails will fail the test, either replace thep upstream or throw a meaningful exception up?

		//Preconditions
		emails = EDRV2.trim( emails || '' );
		if ( emails == '' ) return false;

		if ( emails.match( /^(([A-Za-z0-9_\+\-]+\.)*[A-Za-z0-9_\+\-]+@([A-Za-z0-9\-]+\.)+([A-Za-z]{2,4})(\s*(;)\s*))*([A-Za-z0-9_\+\-]+\.)*[A-Za-z0-9_\+\-]+@([A-Za-z0-9\-]+\.)+([A-Za-z]{2,4})$/ ) == null ) { return false; } //Invalid email syntax

		return true;  //Valid
	}
};
/****************************************************
EDRV2.VALIDATION utilities class.
*****************************************************/

/****************************************************
EDRV2.DOM utilities class.

Provides DOM specific utilities.
*****************************************************/
EDRV2.DOM =
{
	getElement: function ( elem )
	{
		/// <summary>Returns reference to the DOM element.</summary>
		/// <param name="elem">Element ID (if passed in as String) else assumed as DOM element object.</param>
		/// <remarks>
		/// elem is allowed to be passed in as either String (element ID) or DOM element itself to make it easier
		/// to generalize a function call but it is recommended to call this function just for element ID.
		/// </remarks>
		try
		{
			// nothing to do
			elem = elem || '';
			if ( elem == '' ) return null;

			// check if elem is string - if so this is the ID
			if ( typeof ( elem ) == 'string' )
				return document.getElementById( elem ); 	// min browser version supported by EDR JS is compatible w/ this  function - no need to do xbrowser check.
			else
				return elem;
		}
		catch ( e )
		{
			throw e;
		}
	},

	getWindowSize: function ()
	{
		/// <summary>Returns viewable browser window size.</summary>
		var width = 0;
		var height = 0;
		var browserType = 'UNKNOWN';

		try
		{
			if ( ( typeof ( window.innerWidth ) == 'number' ) || ( typeof ( window.innerHeight ) == 'number' ) )
			{
				// new browsers
				browserType = 'NewBrowser';
				width = window.innerWidth;
				height = window.innerHeight;
			}
			else if ( ( document.documentElement ) && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) )
			{
				// ie 6
				browserType = 'IE 6';
				width = document.documentElement.clientWidth;
				height = document.documentElement.clientHeight;
			}
			else if ( ( document.body ) && ( document.body.clientWidth || document.body.clientHeight ) )
			{
				browserType = 'IE Old';
				width = document.body.clientWidth;
				height = document.body.clientHeight;
			}

			return { height: height, width: width, browserType: browserType };
		}
		catch ( e )
		{
			throw e;
		}
	},

	getWindowTotalSize: function ()
	{
		/// <summary>Returns total browser window size (including scrollable area).</summary>
		var width = 0;
		var height = 0;
		var browserType = 'UNKNOWN';

		try
		{
			if ( document.body.scrollWidth && document.body.scrollHeight )
			{
				// all but Explorer Mac         
				browserType = 'IE';
				height = document.body.scrollHeight;
				width = document.body.scrollWidth;
			}
			else if ( ( typeof ( window.innerWidth ) == 'number' ) || ( typeof ( window.innerHeight ) == 'number' ) )
			{
				// new browsers
				browserType = 'NewBrowser';
				width = window.innerWidth + window.scrollMaxX;
				height = window.innerHeight + window.scrollMaxY;
			}
			else if ( document.body.offsetHeight && document.body.offsetWidth )
			{
				// works in Explorer 6 Strict, Mozilla (not FF) and Safari         
				browserType = 'Offset Values';
				height = document.body.offsetHeight;
				width = document.body.offsetWidth;
			}
			else if ( ( document.documentElement ) && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) )
			{
				// ie 6
				browserType = 'IE 6';
				width = document.documentElement.clientWidth;
				height = document.documentElement.clientHeight;
			}
			else if ( ( document.body ) && ( document.body.clientWidth || document.body.clientHeight ) )
			{
				browserType = 'IE Old';
				width = document.body.clientWidth;
				height = document.body.clientHeight;
			}

			return { height: height, width: width, browserType: browserType };
		}
		catch ( e )
		{
			throw e;
		}
	},

	getElementScrollOffset: function ( elem )
	{
		/// <summary>Returns the current scroll coordinates.</summary>
		/// <param name="elem">Element to find scroll offset.</summary>
		try
		{
			var x = 0, y = 0;

			elem = elem || null;

			if ( ( elem != null ) && ( elem.scrollTop != null ) )
			{
				y = elem.scrollTop;
				x = elem.scrollLeft;
			}

			return { scrollX: x, scrollY: y };
		}
		catch ( e )
		{
			throw new Error( 'Unable to get element scroll offset: ' + e.message );
		}
	},

	getScrollOffset: function ()
	{
		/// <summary>Returns the current scroll coordinates.</summary>
		var y = 0;
		var x = 0;

		try
		{
			var pageOffset = self.pageYOffset || null;
			var docElem = document.documentElement || null;
			var docBody = document.body || null;

			if ( pageOffset != null ) // all except Explorer   
			{
				y = self.pageYOffset;
				x = self.pageXOffset;
			}
			else if ( ( docElem != null ) && ( docElem.scrollTop != null ) )
			{
				// Explorer 6 Strict   
				y = document.documentElement.scrollTop;
				x = document.documentElement.scrollLeft;
			}
			else if ( docBody != null )
			{
				// all other Explorers   
				y = document.body.scrollTop;
				x = document.body.scrollLeft;
			}

			return { scrollX: x, scrollY: y };
		}
		catch ( e )
		{
			throw e;
		}
	},

	getElementPosition: function ( elem )
	{
		/// <summary>Returns the element absolute position in the window viewable (client area).</summary>
		/// <param name="elem">DOM element.</param>
		try
		{
			var curTop = curLeft = 0;

			if ( ( elem != null ) && ( elem.offsetParent ) )
			{
				do
				{
					curTop += elem.offsetTop;
					curLeft += elem.offsetLeft;

				} while ( elem = elem.offsetParent );
			}

			return { top: curTop, left: curLeft };
		}
		catch ( e )
		{
			throw e;
		}
	},

	getElementRelativePosition: function ( elem )
	{
		/// <summary>Returns the element position relative to the parent.</summary>
		/// <param name="elem">DOM element.</param>
		try
		{
			var curTop = curLeft = 0;

			if ( ( elem != null ) && ( elem.offsetTop ) )
			{
				curTop = elem.offsetTop;
				curLeft = elem.offsetLeft;
			}

			return { top: curTop, left: curLeft };
		}
		catch ( e )
		{
			throw e;
		}
	},

	getElementSize: function ( elem )
	{
		/// <summary>Returns the element size.</summary>
		/// <param name="elem">DOM element.</param>

		try
		{
			var retVal = { width: 0, height: 0 };

			if ( elem != null )
			{
				// check if element is visible or not because if the element is not visible offsetHeight and offsetWidth
				// is 0

				var isVis = EDRV2.DOM.isElementVisible( elem, null );
				if ( isVis == false )
				{
					EDRV2.DOM.showElement( elem, false );
					retVal.width = elem.offsetWidth;
					retVal.height = elem.offsetHeight;
					EDRV2.DOM.hideElement( elem, false );
				}
				else
				{
					retVal.width = elem.offsetWidth;
					retVal.height = elem.offsetHeight;
				}
			}

			return retVal;
		}
		catch ( e )
		{
			throw e;
		}
	},

	setElementPosition: function ( elem, position, useWindowAsContainer )
	{
		/// <summary>Set element to a specific position on the browser.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="position">One of EDRV2.DOM.popupDIV.prototype.POSITIONS values.</param>
		/// <param name="useWindowAsContainer">True to calculate based on browser viewport, False to calculate based on parent.</param>

		// validation
		if ( ( typeof ( elem ) == 'undefined' ) || ( elem == null ) ) return false;

		try
		{
			// get elem size
			var elemSize = EDRV2.DOM.getElementSize( elem );
			if ( elemSize == null ) throw new Error( 'Div size is not available.' );

			// get parent size
			var parSize = null;
			if ( useWindowAsContainer )
				parSize = EDRV2.DOM.getWindowSize();
			else
				parSize = EDRV2.DOM.getElementSize( elem.offsetParent );

			// validate parent
			if ( parSize == null ) throw new Error( 'Parent element size is not available.' );

			// calculate top and left
			var top = 0;
			var left = 0;

			switch ( position )
			{
				case EDRV2.DOM.popupDIV.prototype.POSITIONS.TopLeft:
					top = 0;
					left = 0;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.TopMiddle:
					top = 0;
					left = ( parSize.width - elemSize.width ) / 2;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.TopRight:
					top = 0;
					left = parSize.width - elemSize.width;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.MiddleLeft:
					top = ( parSize.height - elemSize.height ) / 2;
					left = 0;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.MiddleMiddle:
					top = ( parSize.height - elemSize.height ) / 2;
					left = ( parSize.width - elemSize.width ) / 2;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.MiddleRight:
					top = ( parSize.height - elemSize.height ) / 2;
					left = parSize.width - elemSize.width;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.BottomLeft:
					top = parSize.height - elemSize.height;
					left = 0;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.BottomMiddle:
					top = parSize.height - elemSize.height;
					left = ( parSize.width - elemSize.width ) / 2;
					break;

				case EDRV2.DOM.popupDIV.prototype.POSITIONS.BottomRight:
					top = parSize.height - elemSize.height;
					left = parSize.width - elemSize.width;
					break;

				default:
					throw new Error( 'Invalid position: ' + position );
			}

			// get the screen off set if the parent is window
			if ( useWindowAsContainer )
			{
				var winOffset = EDRV2.DOM.getScrollOffset();
				top += winOffset.scrollY;
				left += winOffset.scrollX;
			}

			// change top left
			EDRV2.DOM.applyElementStyle( elem, 'top: ' + top + 'px; left: ' + left + 'px;' );
		}
		catch ( e )
		{
			e.message = 'Unable to set element position: ' + e.message;
			throw e;
		}
	},

	applyElementStyle: function ( elem, cssStyle )
	{
		/// <summary>Applies CSS style to element.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="cssStyle">CSS formatted style (attribute=value - multiple separated by semi-colon).</param>
		/// <remarks>cssStyle must be in CSS format such as background-color: Green; border: 1px solid Blue;</remarks>

		try
		{
			// validate
			if ( ( typeof ( elem ) == 'undefined' ) || ( elem == null ) ) return;
			if ( ( typeof ( elem.style ) == 'undefined' ) || ( elem.style == null ) ) return;

			cssStyle = EDRV2.trim( cssStyle );
			if ( cssStyle == '' ) return;

			// split style by ;
			var tokens = cssStyle.split( ';' );
			var token = '';
			var style = null;

			for ( i = 0; i < tokens.length; i++ )
			{
				// trim
				token = EDRV2.trim( tokens[i] );
				if ( token != '' )
				{
					// split by :
					style = token.split( ':' );

					// expecting 2 tokens
					if ( style.length == 2 )
					{
						// element 0 is the stylename - lowercase for later use
						style[0] = EDRV2.trim( style[0] ).toLowerCase();
						style[1] = EDRV2.trim( style[1] );

						// convert stylename to the property name
						// all properties starts w/ lowecase
						// multi-words property name is camel case, multi-words string stylename is separated by -
						// so run regexp that capatilize the first char after - and remove the - itself (thus, we convert string stylename to propertyname)
						style[0] = style[0].replace( /(\-[a-zA-Z])/gi, function ( m ) { return m.charAt( 1 ).toUpperCase(); } );

						// set tyle
						elem.style[style[0]] = style[1];
					}
				}
			}

			return;
		}
		catch ( e )
		{
			throw e;
		}
	},

	getElementStyle: function ( elem, cssAttributeNames )
	{
		/// <summary>Returns element style in CSS format.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="cssAttributeNames">CSS attribute name or an array of CSS attribute names (null or not specified will return all).</param>

		try
		{
			// validate
			if ( ( typeof ( elem ) == 'undefined' ) || ( elem == null ) ) throw new Error( 'Unable to get DOM element style: Invalid DOM element.' );
			if ( ( typeof ( elem.style ) == 'undefined' ) || ( elem.style == null ) ) throw new Error( 'Unable to get DOM element style: DOM element does not have style object.' );

			var cssAttrs = [];
			var isSingleAttr = false;
			if ( ( typeof ( cssAttributeNames ) != 'undefined' ) && ( cssAttributeNames != null ) )
			{
				if ( cssAttributeNames instanceof Array )
				{
					// use the specified array
					cssAttrs = cssAttributeNames;
				}
				else
				{
					// assume it is a single attribubte
					isSingleAttr = true;
					cssAttrs.push( cssAttributeNames );
				}
			}

			// get style collection
			var styleColl = elem.currentStyle || elem.style;

			// use the new standard to pull css styles if available
			var useComputedStyle = false;
			if ( document.defaultView && document.defaultView.getComputedStyle ) useComputedStyle = true;

			// splitting the logic into 2 to make it easier
			var css = '';
			var cssProp = '';
			var cssKey = '';
			var cssValue = '';

			if ( cssAttrs.length == 0 )
			{
				// get all styles
				for ( cssProp in styleColl )
				{
					// replace capital letter with - + the char
					cssKey = cssProp.replace( /([A-Z])/g, function ( m ) { return '-' + m.toLowerCase(); } );

					if ( useComputedStyle )
					{
						css += cssKey + ': ' + document.defaultView.getComputedStyle( elem, "" ).getPropertyValue( cssKey ) + '; ';
					}
					else
					{
						if ( ( typeof ( styleColl[cssProp] ) != 'function' ) && ( styleColl[cssProp] != null ) && ( styleColl[cssProp] != '' ) )
						{
							css += cssKey + ': ' + styleColl[cssProp] + '; ';
						}
					}
				}
			}
			else
			{
				// get specific
				for ( var i = 0; i < cssAttrs.length; i++ )
				{
					// convert for attribute format to property format
					cssProp = cssAttrs[i].replace( /(\-[a-zA-Z])/gi, function ( m ) { return m.charAt( 1 ).toUpperCase(); } );

					if ( useComputedStyle )
					{
						if ( isSingleAttr )
							return document.defaultView.getComputedStyle( elem, "" ).getPropertyValue( cssAttrs[i] );
						else
							css += cssAttrs[i] + ': ' + document.defaultView.getComputedStyle( elem, "" ).getPropertyValue( cssAttrs[i] ) + '; ';
					}
					else
					{
						if ( ( typeof ( styleColl[cssProp] ) != 'function' ) && ( styleColl[cssProp] != null ) && ( styleColl[cssProp] != '' ) )
						{
							if ( isSingleAttr )
								return styleColl[cssProp];
							else
								css += cssAttrs[i] + ': ' + styleColl[cssProp] + '; ';
						}
					}
				}
			}

			if ( isSingleAttr )
				return null;
			else
				return css;
		}
		catch ( e )
		{
			throw e;
		}
	},

	hasCSSAttribute: function ( elem, cssAttrName )
	{
		/// <summary>Returns whether the CSS attribute is specified in the element.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="cssAttrName">CSS attribute name.</param>

		try
		{
			// validate
			cssAttrName = cssAttrName || '';

			if ( cssAttrName == '' ) return false;

			// get value
			var val = EDRV2.DOM.getElementStyle( elem, cssAttrName );

			if ( ( val == null ) || ( val == '' ) )
				return false;
			else
				return true;
		}
		catch ( e )
		{
			throw new Error( 'Unable to determine CSS attribute existence: ' + e.mesage );
		}
	},

	isElementVisible: function ( elem, useCSSVisibility )
	{
		/// <summary>Returns whether element is visible or not.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="">True check visibility value, False check display value, null (or not specified) check both.</param>

		try
		{
			// validation
			if ( elem == null ) throw new Error( 'Unable to check DOM element visibility: DOM element does not exist.' );

			// get status for both values
			var isVisibilityVisible = true;
			var isDisplayVisible = true;

			var visibilityValue = EDRV2.trim( EDRV2.DOM.getElementStyle( elem, 'visibility' ) );
			var displayValue = EDRV2.trim( EDRV2.DOM.getElementStyle( elem, 'display' ) );

			if ( visibilityValue.toLowerCase() == 'hidden' ) isVisibilityVisible = false;
			if ( displayValue.toLowerCase() == 'none' ) isDisplayVisible = false;

			if ( ( typeof ( useCSSVisibility ) == 'undefined' ) || ( useCSSVisibility == null ) )
			{
				return ( isDisplayVisible && isVisibilityVisible )
			}
			else if ( useCSSVisibility == true )
			{
				return isVisibilityVisible;
			}
			else
			{
				return isDisplayVisible;
			}
		}
		catch ( e )
		{
			throw e;
		}
	},

	toggleElementVisibility: function ( elem, useCSSVisibility )
	{
		/// <summary>Toogles DOM element visibility.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="">True - change visibility value, False - change display value (default).</param>

		try
		{
			// determine whether to use DISPLAY or VISIBILITY if
			// second parameter is not set
			if ( ( typeof ( useCSSVisibility ) == 'undefined' ) || ( useCSSVisibility == null ) )
			{
				// default to use display
				useCSSVisibility = false;

				// use visibility if DISPLAY does not exist
				if ( ( !EDRV2.DOM.hasCSSAttribute( elem, 'display' ) ) && ( EDRV2.DOM.hasCSSAttribute( elem, 'visibility' ) ) ) useCSSVisibility = true;
			}

			// get current status
			var isVisible = EDRV2.DOM.isElementVisible( elem, useCSSVisibility );
			if ( isVisible )
				EDRV2.DOM.hideElement( elem, useCSSVisibility );
			else
				EDRV2.DOM.showElement( elem, useCSSVisibility );
		}
		catch ( e )
		{
			throw e;
		}
	},

	hideElement: function ( elem, useCSSVisibility )
	{
		/// <summary>Hide DOM element.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="">True - change visibility value, False - change display value (default).</param>

		try
		{
			// determine whether to use DISPLAY or VISIBILITY if
			// second parameter is not set
			if ( ( typeof ( useCSSVisibility ) == 'undefined' ) || ( useCSSVisibility == null ) )
			{
				// default to use display
				useCSSVisibility = false;

				// use visibility if DISPLAY does not exist
				if ( ( !EDRV2.DOM.hasCSSAttribute( elem, 'display' ) ) && ( EDRV2.DOM.hasCSSAttribute( elem, 'visibility' ) ) ) useCSSVisibility = true;
			}

			if ( useCSSVisibility )
				elem.style.visibility = 'hidden';
			else
				elem.style.display = 'none';
		}
		catch ( e )
		{
			throw e;
		}
	},

	showElement: function ( elem, useCSSVisibility )
	{
		/// <summary>Show DOM element.</summary>
		/// <param name="elem">DOM element.</param>
		/// <param name="">True - change visibility value, False - change display value (default).</param>

		try
		{
			// determine whether to use DISPLAY or VISIBILITY if
			// second parameter is not set
			if ( ( typeof ( useCSSVisibility ) == 'undefined' ) || ( useCSSVisibility == null ) )
			{
				// default to use display
				useCSSVisibility = false;

				// use visibility if DISPLAY does not exist
				if ( ( !EDRV2.DOM.hasCSSAttribute( elem, 'display' ) ) && ( EDRV2.DOM.hasCSSAttribute( elem, 'visibility' ) ) ) useCSSVisibility = true;
			}

			if ( useCSSVisibility )
				elem.style.visibility = 'visible';
			else
				elem.style.display = 'block';
		}
		catch ( e )
		{
			throw e;
		}
	},

	isElementInDocument: function ( elem )
	{
		/// <summary>Returns whether element is in the current DOM document.</summary>
		/// <param name="elem">Element to check.</param>

		// return True if this is null - just because of the usage of this is usually
		// to add/remove element from DOM.
		elem = elem || null;

		if ( elem == null ) return true;

		// reverse traverse to see if parentNode points back to document.
		while ( elem )
		{
			if ( elem == document ) return true;

			elem = elem.parentNode;
		}

		// not found
		return false;
	}
};
/****************************************************
EDRV2.DOM utilities class.
*****************************************************/

/****************************************************
EDRV2.DOM.EVENT utilities class.

Provides DOM specific event utilities.
*****************************************************/
EDRV2.DOM.EVENT =
{
	getEvent: function ( event )
	{
		/// <summary>Returns event object (x-browser).</summary>
		/// <param name="event">DOM event object from browser.</param>
		return event ? event : window.event;
	},

	getEventTarget: function ( event )
	{
		/// <summary>Returns the DOM element that TRIGGERED the event.</summary>
		/// <param name="event">DOM event object from browser.</param>
		try
		{
			if ( ( typeof ( event ) == 'undefined' ) || ( event == null ) ) throw new Error( 'Unable to get event target: Invalid event object.' );
			return event.target || event.srcElement;
		}
		catch ( e )
		{
			throw e;
		}
	},

	getEventSourceTarget: function ( event, elem )
	{
		/// <summary>Returns DOM element that TRAPS the event.</summary>
		/// <param name="event">DOM event object from browser.</param>
		/// <param name="elem">DOM element that TRAPS the event (shortcut for IE calls).</param>
		/// <remarks>IE does not support .currentTarget (element that actually traps the event). So this method will return the .srcElement instead.</remarks>
		try
		{
			if ( ( typeof ( event ) == 'undefined' ) || ( event == null ) ) throw new Error( 'Unable to get event source target: Invalid event object.' );
			return event.currentTarget || elem || event.srcElement;
		}
		catch ( e )
		{
			throw e;
		}
	},

	addEventHandler: function ( elem, eventName, eventHandler, useCapturePhase )
	{
		/// <summary>Adds event handler.</summary>
		/// <param name="elem">DOM element to trap event for.</param>
		/// <param name="eventName">DOM event name.</param>
		/// <param name="eventHandler">Function pointer to event handler.</param>
		/// <param name="useCapturePhase">True to use the capture phase, False to use bubble phase (default).</param>
		/// <returns> JSON { domElement: elem, eventName: eventName, handler: evt, useCapturePhase: useCapturePhase }</returns>
		try
		{
			// validate
			if ( elem == null ) throw new Error( 'Unable to add event handler: Invalid DOM element.' );
			if ( EDRV2.trim( eventName ) == '' ) throw new Error( 'Unable to add event handler: Invalid event name.' );
			if ( eventHandler == null ) throw new Error( 'Unable to add event handler: Invalid event callback function.' );

			// default to bubble phase
			useCapturePhase = useCapturePhase ? useCapturePhase : false;

			// if this is IE - create a closure to set the currentTarget property
			var evt = null;
			if ( window.event )
				evt = EDRV2.bindFunction( eventHandler, elem );
			else
				evt = eventHandler;

			if ( elem.addEventListener )
			{
				elem.addEventListener( eventName, evt, useCapturePhase );
			}
			else if ( elem.attachEvent )
			{
				elem.attachEvent( 'on' + eventName, evt );
			}
			else
			{
				// just assign it as property
				elem['on' + eventName] = evt;
			}

			return { domElement: elem, eventName: eventName, handler: evt, useCapturePhase: useCapturePhase };
		}
		catch ( e )
		{
			throw e;
		}
	},

	removeEventHandler: function ( elem, eventName, eventHandler, useCapturePhase )
	{
		/// <summary>Removes event handler.</summary>
		/// <param name="elem">DOM element to trap event for.</param>
		/// <param name="eventName">DOM event name.</param>
		/// <param name="eventHandler">Function pointer to event handler.</param>
		/// <param name="useCapturePhase">True to use the capture phase, False to use bubble phase (default).</param>

		try
		{
			// validate
			if ( elem == null ) throw new Error( 'Unable to remove event handler: Invalid DOM element.' );
			if ( EDRV2.trim( eventName ) == '' ) throw new Error( 'Unable to remove event handler: Invalid event name.' );

			// default to bubble phase
			useCapturePhase = useCapturePhase ? useCapturePhase : false;

			if ( elem.removeEventListener )
			{
				elem.removeEventListener( eventName, eventHandler, useCapturePhase );
			}
			else if ( elem.detachEvent )
			{
				elem.detachEvent( 'on' + eventName, eventHandler );
			}
			else
			{
				// just assign it as property
				elem['on' + eventName] = null;
			}
		}
		catch ( e )
		{
			throw e;
		}
	},

	stopPropagation: function ( event )
	{
		/// <summary>Stops event propagation (bubbling).</summary>
		/// <param name="event">DOM event object.</param>

		try
		{
			if ( event.stopPropagation )
				event.stopPropagation();
			else
				event.cancelBubble = true;
		}
		catch ( e )
		{
			throw e;
		}
	},

	preventDefault: function ( event )
	{
		/// <summary>Prevents default event behavior from being executed.</summary>
		/// <param name="event">DOM event object.</param>

		try
		{
			if ( event.preventDefault )
				event.preventDefault();
			else
				event.returnValue = false;
		}
		catch ( e )
		{
			throw e;
		}
	}
};
/****************************************************
EDRV2.DOM.EVENT utilities class.
*****************************************************/

/****************************************************
EDRV2.ObjectBase base class.

Provides base class for EDR JS objects.
*****************************************************/
EDRV2.ObjectBase = function ()
{
	/// <summary>Creates new instance of EDRV2.ObjectBase.</summary>
	if ( this instanceof EDRV2.ObjectBase )
	{
		this.disposableDOMEvents = [];
		this.base = null;

		this.isUsable = true;
		this.errorMessage = '';
	}
	else
	{
		return new EDRV2.ObjectBase();
	}
};

// Inheritance Properties
EDRV2.ObjectBase.prototype.constructor = EDRV2.ObjectBase;
EDRV2.ObjectBase.prototype.base = null; 		// set by derive class

// Properties
EDRV2.ObjectBase.prototype.isUsable = null;
EDRV2.ObjectBase.prototype.errorMessage = null;
EDRV2.ObjectBase.prototype.disposableDOMEvents = null; // array of DOM events added by using EDRV2.DOM.EventUtil.addEventHandler()

// Methods
EDRV2.ObjectBase.prototype.dispose = function ()
{
	// <summary>Disposes current instance (reclaim expensive resources).</summary>
	this.isUsable = false;

	if ( this.disposableDOMEvents != null )
	{
		var evt = null;

		for ( var i = 0; i < this.disposableDOMEvents.length; i++ )
		{
			// remove event handler
			// { domElement: elem, eventName: eventName, handler: evt, useCapturePhase: useCapturePhase }
			evt = this.disposableDOMEvents[i];

			EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

			// deref
			this.disposableDOMEvents[i] = null;
		}

		delete this.disposableDOMEvents;
		this.disposableDOMEvents = [];
	}

	return null;
};

EDRV2.ObjectBase.prototype.buildErrorMessage = function ( header, msgs, isHTML )
{
	/// <summary>Build error message.</summary>
	/// <param name="header">Error header.</param>
	/// <param name="msgs">Error messages (displayed as bullets if passed in as array).</param>
	/// <param name="isHTML">Build error message as HTML (using UL).</param>

	//if ( ( typeof ( header ) == 'undefined' ) || ( header == null ) )
	//{
	//	header = 'Unspecified error';
	//}

	var errMsgs = null;

	if ( ( typeof ( msgs ) == 'undefined' ) || ( msgs == null ) )
	{
		// not specified - empty array.
		errMsgs = [];
	}
	else if ( msgs instanceof Array )
	{
		// already an array - just use it
		errMsgs = msgs;
	}
	else
	{
		// not an array - convert into array
		errMsgs = [];
		errMsgs.push( msgs );
	}

	if ( ( typeof ( isHTML ) == 'undefined' ) || ( isHTML == null ) )
	{
		isHTML = false;
	}

	// build error message
	var msg = '';

	if ( errMsgs.length == 0 )
	{
		msg = EDRV2.trim( header );
	}
	else
	{
		var lineBreak = '';
		if ( isHTML )
			lineBreak = '<br />\n';
		else
			lineBreak = '\n';

		var listStart = '\n', listEnd = '\n', itemStart = '- ', itemEnd = '\n';
		if ( isHTML )
		{
			listStart = '<ul>\n';
			listEnd = '</ul>\n';
			itemStart = '<li> ';
			itemEnd = '</li>\n';
		}

		if ( ( typeof ( header ) != 'undefined' ) && ( header != null ) )
		{
			msg = header + ':' + lineBreak;
		}
		msg += listStart;

		for ( var i = 0; i < errMsgs.length; i++ )
		{
			msg += itemStart + errMsgs[i] + itemEnd;
		}

		msg += listEnd;
	}

	return msg;
};

EDRV2.ObjectBase.prototype.toString = function ()
{
	/// <summary>Returns string representation of object.</summary>
	return EDRV2.displayObjectProperties( this, false );
};
/****************************************************
EDRV2.ObjectBase base class.
*****************************************************/

/****************************************************
EDRV2.DOM.popupDIV class.

Provides functionality to pop-up a DIV.
*****************************************************/
EDRV2.DOM.popupDIV = function ( popupDivID, position, useWindow )
{
	/// <summary>Creates new popup DIV control.</summary>
	/// <param name="popupDivID">Main container for the popup.</param>
	/// <param name="position">Popup position.</param>
	/// <param name="useWindow">True - use entire browser window as container (default). False - use parent as container.</param>

	if ( this instanceof EDRV2.DOM.popupDIV )
	{
		try
		{
			// inheritance
			EDRV2.ObjectBase.apply( this, arguments );
			this.base = EDRV2.ObjectBase.prototype;

			// verify popup DIV
			var popup = EDRV2.DOM.getElement( popupDivID );
			if ( popup == null ) throw new Error( 'Invalid POPUP DIV id: ' + popupDivID );

			this.popupDivID = popupDivID;

			// verify position
			position = position || this.POSITIONS.Unknown;
			switch ( position )
			{
				case this.POSITIONS.TopLeft:
				case this.POSITIONS.TopMiddle:
				case this.POSITIONS.TopRight:
				case this.POSITIONS.MiddleLeft:
				case this.POSITIONS.MiddleMiddle:
				case this.POSITIONS.MiddleRight:
				case this.POSITIONS.BottomLeft:
				case this.POSITIONS.BottomMiddle:
				case this.POSITIONS.BottomRight:
					// save position
					this.popupPosition = position;
					break;

				default:
					throw new Error( 'Invalid position: ' + position );
			}

			// use window
			if ( typeof ( useWindow ) != 'undefined' )
			{
				this.useWindowAsContainer = useWindow;
			}

			// all set
			this.isUsable = true;
		}
		catch ( e )
		{
			this.isUsable = false;
			this.errorMessage = 'Unable to initialize popup addon: ' + e.message;
		}
	}
	else
		return new EDRV2.DOM.popupDIV( popupDivID, position, useWindow );
};

// inheritance
EDRV2.DOM.popupDIV.prototype = new EDRV2.ObjectBase();
EDRV2.DOM.popupDIV.prototype.constructor = EDRV2.DOM.popupDIV;

// events
EDRV2.DOM.popupDIV.prototype.onShow = null;
EDRV2.DOM.popupDIV.prototype.onClose = null;

// enums
EDRV2.DOM.popupDIV.prototype.POSITIONS = { Unknown: 0, TopLeft: 1, TopMiddle: 2, TopRight: 3, MiddleLeft: 4, MiddleMiddle: 5, MiddleRight: 6, BottomLeft: 7, BottomMiddle: 8, BottomRight: 9 };

// properties
EDRV2.DOM.popupDIV.prototype.popupDivID = null;
EDRV2.DOM.popupDIV.prototype.popupPosition = 0;
EDRV2.DOM.popupDIV.prototype.useWindowAsContainer = true;

// methods
EDRV2.DOM.popupDIV.prototype.show = function ()
{
	/// <summary>Show popup.</summary>
	if ( this.isUsable == false ) return;

	try
	{
		// get elem size
		var elem = EDRV2.DOM.getElement( this.popupDivID );
		if ( elem == null ) throw new Error( 'Div element not available.' );

		// set element position
		EDRV2.DOM.setElementPosition( elem, this.popupPosition, this.useWindowAsContainer );

		// open
		EDRV2.DOM.showElement( elem, false );

		// raise event
		if ( this.onShow != null ) this.onShow();
	}
	catch ( e )
	{
		e.message = 'Unable to show popup: ' + e.message;
		throw e;
	}
};

EDRV2.DOM.popupDIV.prototype.showAtSpecificPosition = function ( top, left )
{
	/// <summary>Show popup at defined position top left</summary>
	if ( this.isUsable == false ) return;

	try
	{

		// get elem 
		var elem = EDRV2.DOM.getElement( this.popupDivID );

		// change top left
		EDRV2.DOM.applyElementStyle( elem, 'top: ' + top + 'px; left: ' + left + 'px;' );

		// open
		EDRV2.DOM.showElement( elem, false );

		// raise event
		if ( this.onShow != null ) this.onShow();
	}
	catch ( e )
	{
		e.message = 'Unable to show popup: ' + e.message;
		throw e;
	}
};


EDRV2.DOM.popupDIV.prototype.hide = function ()
{
	/// <summary>Hides popup.</summary>
	if ( this.isUsable == false ) return;

	try
	{
		var elem = EDRV2.DOM.getElement( this.popupDivID );
		if ( elem == null ) throw new Error( 'Div element not available.' );

		// close 
		EDRV2.DOM.hideElement( elem, false );

		// raise event
		if ( this.onClose != null ) this.onClose();
	}
	catch ( e )
	{
		e.message = 'Unable to hide popup: ' + e.message;
		throw e;
	}
};

/****************************************************
EDRV2.DOM.popupDIV class.
*****************************************************/

/****************************************************
EDRV2.DOM.notificationWindow class.
****************************************************/
EDRV2.DOM.notificationWindow = function ( popupDivID, position, useWindow, headerDivID, contentDivID, closeElemID )
{
	///<summary> Create a notification window </summary>
	/// <param name="popupDivID">Main container for the popup.</summary>
	/// <param name="position">Popup position.</summary>
	/// <param name="useWindow">True - use entire browser window as container (default). False - use parent as container.</summary>
	/// <param name="headerDivID">Div ID to display header text in.</summary>
	/// <param name="contentDivID">Div ID to display content in.</summary>
	/// <param name="closeElemID">Element ID to trigger close window.</summary>
	if ( this instanceof EDRV2.DOM.notificationWindow )
	{
		try
		{
			//inheritance
			EDRV2.DOM.popupDIV.apply( this, arguments );
			this.base = EDRV2.DOM.popupDIV.prototype;

			var elem = null;

			// verify elements
			elem = EDRV2.DOM.getElement( headerDivID );
			if ( elem == null ) throw new Error( 'Header DIV not found.' );

			elem = EDRV2.DOM.getElement( contentDivID );
			if ( elem == null ) throw new Error( 'Content DIV not found.' );

			elem = EDRV2.DOM.getElement( closeElemID );
			if ( elem == null ) throw new Error( 'Close element not found.' );

			//fill in the rest of the properties
			this.headerDivID = headerDivID;
			this.contentDivID = contentDivID;
			this.closeElemID = closeElemID;

			// trap click event on close elem (which should be the last item checked above
			var nw = this;
			this.disposableDOMEvents.push( EDRV2.DOM.EVENT.addEventHandler( elem, 'click', function () { nw.hide(); } ) );
		}
		catch ( e )
		{
			this.isUsable = false;
			this.errorMessage = 'Unable to initialize notification window: ' + e.message;
		}
	}
	else
	{
		return new EDRV2.DOM.notificationWindow( popupDivID, position, useWindow, headerDivID, contentDivID, closeElemID );
	}
};

//inheritance
EDRV2.DOM.notificationWindow.prototype = new EDRV2.DOM.popupDIV();

//constructor
EDRV2.DOM.notificationWindow.prototype.constructor = EDRV2.DOM.notificationWindow;

//properties
EDRV2.DOM.notificationWindow.prototype.headerDivID = '';
EDRV2.DOM.notificationWindow.prototype.contentDivID = '';
EDRV2.DOM.notificationWindow.prototype.closeElemID = '';

//methods
EDRV2.DOM.notificationWindow.prototype.show = function ( header, content, useContentAsIs )
{
	///<summary> Display the notification window </summary>
	/// <param name="header">Header text.</summary>
	/// <param name="content">Content text.</summary>
	/// <param name="useContentAsIs">True to use the content as is, False to run it through buildErrorMessage().</summary>
	///<remarks> Extends the EDRV2.DOM.popupDIV.show method. </remarks>
	try
	{
		if ( this.isUsable == false ) return false;

		//update the header text and content
		var headerContainer = EDRV2.DOM.getElement( this.headerDivID );
		if ( headerContainer != null ) headerContainer.innerHTML = EDRV2.trim( header );

		var contentContainer = EDRV2.DOM.getElement( this.contentDivID );
		if ( contentContainer != null )
		{
			// don't run through buildErrorMessage() if request to use content as is
			if ( useContentAsIs )
				contentContainer.innerHTML = content;
			else
				contentContainer.innerHTML = this.buildErrorMessage( null, content, true );
		}

		//call the parent's show method
		this.base.show.call( this );

		return true;
	}
	catch ( e )
	{
		e.message = 'Unable to show notification window: ' + e.message;
		throw e;
	}
};
/****************************************************
EDRV2.DOM.notificationWindow class.
*****************************************************/

/****************************************************
EDRV2.NameValue class.

Provides name-value object.
*****************************************************/
EDRV2.NameValue = function ( name, value )
{
	if ( this instanceof EDRV2.NameValue )
	{
		// inheritance
		EDRV2.ObjectBase.apply( this, arguments );
		this.base = EDRV2.ObjectBase.prototype;

		this.name = name || '';
		this.value = value || null;
	}
	else
		return new EDRV2.NameValue( name, value );
};

EDRV2.NameValue.prototype = new EDRV2.ObjectBase();
EDRV2.NameValue.prototype.constructor = EDRV2.NameValue;

EDRV2.NameValue.prototype.name = '';
EDRV2.NameValue.prototype.value = null;

EDRV2.NameValue.prototype.toString = function ()
{
	return 'name: [' + this.name + '] value: [' + this.value + ']';
};
/****************************************************
EDRV2.NameValue class.
*****************************************************/

/****************************************************
EDRV2.Counter singleton counter class.
*****************************************************/
EDRV2.Counter = function ()
{
	/// <summary>Singleton object to keep counters for application.</summary>
	/// <remarks>The counter is incremented based on the key and this is PER application.</remarks>

	// private variable to hold the counters
	var m_counters = [];

	// private object
	var instance =
	{
		getNext: function ( key )
		{
			/// <summary>Returns next value for the counter.</summary>
			/// <param name="key">Key for the counter.</summary>
			try
			{
				// validation
				if ( ( typeof ( key ) == 'undefined' ) || ( key == null ) || ( key == '' ) ) throw new Error( 'Missing key for the counter' );

				// get current value
				var curVal = m_counters[key];

				// if not yet set - create new one otherwise increment
				if ( ( typeof ( curVal ) == 'undefined' ) || ( curVal == null ) )
					curVal = 1;
				else
					curVal++;

				// save value
				m_counters[key] = curVal;

				return curVal;
			}
			catch ( e )
			{
				throw new Error( 'Unable to increment counter value: ' + e.message );
			}
		}
	}

	// returns private instance
	return instance;
}();
/****************************************************
EDRV2.Counter singleton counter class.
*****************************************************/

/****************************************************
EDRV2.HTTP.TransmitRequest class.
*****************************************************/
EDRV2.HTTP.TransmitRequest = function ( url, completionEvt, autoConvResponse, ordGUID, propGUID, rptGUID )
{
	/// <summary>Encapsulates transmitting data via HTTP protocol (support asynchronous (default) and synchronous mode).</summary>
	/// <param name="url">URL to transmit data to (if not specified - can be set via URL property).</summary>
	/// <param name="completionEvt">Event to trigger upon completion of transmission (if not specified - can be set via completionEvent property).</summary>
	/// <param name="autoConvResponse">True to auto-convert response for known Content-Type, False to return raw data.</summary>
	/// <param name="ordGUID">Order GUID (optional).</summary>
	/// <param name="propGUID">Property GUID (optional).</summary>
	/// <param name="rptGUID">Report GUID (optional).</summary>

	if ( this instanceof EDRV2.HTTP.TransmitRequest )
	{
		try
		{
			// inheritance
			EDRV2.ObjectBase.apply( this, arguments );
			this.base = EDRV2.ObjectBase.prototype;

			// set properties
			this.URL = url || '';
			this.completionEvent = completionEvt || null;
			this.isAsynchronous = isAsync;

			this.orderGUID = ordGUID || null;
			this.propertyGUID = propGUID || null;
			this.reportGUID = rptGUID || null;

			// isAsync is boolean - default to true if not specified
			if ( ( typeof ( autoConvResponse ) === 'undefined' ) || ( autoConvResponse == null ) )
				this.autoConvertResponse = true;
			else
				this.autoConvertResponse = autoConvResponse;

			this.isAsynchronous = true; // default to async
			this.transmissionStatus = EDRV2.HTTP.TransmitRequest.prototype.EnumTransmissionStatus.New;

			// assign transmitID
			this.transmitID = EDRV2.Counter.getNext( 'EV2HTTPXMITREQ' );

			//
			var xmitData = [];

			var xmitDataAdd = function ( key, value, encodeValue )
			{
				// this contains the logic to ensure xmitData has unique keys
				// it assumes data has been cleaned and correct
				var keyTemp = key.toUpperCase();

				// encode value if needed
				if ( encodeValue == true ) value = encodeURIComponent( value );

				// data saved into the array is EDRV2.NameValue
				for ( var i = 0; i < xmitData.length; i++ )
				{
					if ( keyTemp == xmitData[i].name.toUpperCase() )
					{
						// found it - replace value and exit
						xmitData[i].value = value;
						return true;
					}
				}

				// add item
				xmitData.push( new EDRV2.NameValue( key, value ) );

				return true;
			};

			this.addParam = function ( key, value )
			{
				/// <summary>Add transmit data parameter (as-is - no encoding).</summary>
				/// <param name="key">Key for the data.</summary>
				/// <param name="value">Value.</summary>

				try
				{
					// validate
					key = EDRV2.trim( key );
					value = value || '';

					if ( key == '' ) return false;

					// delegate
					return xmitDataAdd( key, value, false );
				}
				catch ( e )
				{
					throw new Error( 'Unable to add TransmitRequest parameter: ' + e.message );
				}
			};

			this.addParamEncode = function ( key, value )
			{
				/// <summary>Add transmit data parameter and the value will be encoded.</summary>
				/// <param name="key">Key for the data.</summary>
				/// <param name="value">Value.</summary>

				try
				{
					// validate
					key = EDRV2.trim( key );
					value = value || '';

					if ( key == '' ) return false;

					// delegate
					return xmitDataAdd( key, value, true );
				}
				catch ( e )
				{
					throw new Error( 'Unable to add TransmitRequest parameter: ' + e.message );
				}
			};

			this.getParams = function ()
			{
				/// <summary>Returns transmit request data collection.</param>
				return xmitData;
			};

			this.isUsable = true;
			this.errorMessage = '';
		}
		catch ( e )
		{
			this.isUsable = false;
			this.errorMessage = 'Unable to initialize TransmitRequest: ' + e.message;
		}
	}
	else
		return new EDRV2.HTTP.TransmitRequest( url, completionEvt, autoConvResponse, ordGUID, propGUID, rptGUID );
};

// extents EDRV2.ObjectBase
EDRV2.HTTP.TransmitRequest.prototype = new EDRV2.ObjectBase();
EDRV2.HTTP.TransmitRequest.prototype.constructor = EDRV2.HTTP.TransmitRequest;
EDRV2.HTTP.TransmitRequest.prototype.base = null; 		// set by derive class

// provides enumered values for transmission status
EDRV2.HTTP.TransmitRequest.prototype.EnumTransmissionStatus = { New: 'NEW', Sending: 'SEND', Receiving: 'RECV', Failed: 'FAILED', Successful: 'SUCCESS' };

// properties
EDRV2.HTTP.TransmitRequest.prototype.transmitID = null;				// unique ID per application for transmitting data via this object (READONLY)

EDRV2.HTTP.TransmitRequest.prototype.URL = null;									// URL to post to
EDRV2.HTTP.TransmitRequest.prototype.completionEvent = null;			// event to trigger upon completion of the transmission
EDRV2.HTTP.TransmitRequest.prototype.autoConvertResponse = null;	// True to auto-convert known content-type, False to return raw response data
EDRV2.HTTP.TransmitRequest.prototype.isAsynchronous = null; 			// True to transmit data in async mode otherwise false

EDRV2.HTTP.TransmitRequest.prototype.orderGUID = null;				// Order GUID (set to null if no applicable)
EDRV2.HTTP.TransmitRequest.prototype.propertyGUID = null; 		// Property GUID (set to null if no applicable)
EDRV2.HTTP.TransmitRequest.prototype.reportGUID = null; 			// Report GUID (set to null if no applicable)

EDRV2.HTTP.TransmitRequest.prototype.contextData = null; 			// Optional data for caller to set that will persisted through the entire operation

EDRV2.HTTP.TransmitRequest.prototype.sourceName = null; 				// Optional name of the source
EDRV2.HTTP.TransmitRequest.prototype.sourceDescription = null;	// Optional description of the transmittion

EDRV2.HTTP.TransmitRequest.prototype.trackingData = null; 		// future use - placeholder for tracking data

EDRV2.HTTP.TransmitRequest.prototype.transmissionStatus = null;		// transmission status
EDRV2.HTTP.TransmitRequest.prototype.result = null;								// result of the transmission

// methods
EDRV2.HTTP.TransmitRequest.prototype.addParam = null;					// adds data (key, value)
EDRV2.HTTP.TransmitRequest.prototype.addParamEncode = null; 	// adds data (key, value) - value will be encodeURIComponent()
EDRV2.HTTP.TransmitRequest.prototype.getParams = null; 				// returns the current collection of data

EDRV2.HTTP.TransmitRequest.prototype.validate = function ()
{
	/// <summary>Validates transmission information.</summary>

	try
	{
		var tmp = null;

		// URL
		tmp = EDRV2.trim( tmp );
		if ( tmp == '' ) throw new Error( 'Missing URL' );

		// completion event
		tmp = this.completionEvent || null;
		if ( tmp == null ) throw new Error( 'Missing completion event' );

		// auto convert response
		tmp = this.autoConvertResponse || null;
		if ( tmp == null ) throw new Error( 'Missing auto-convert response' );

		return true;
	}
	catch ( e )
	{
		throw new Error( 'TransmitRequest invalid data: ' + e.message );
	}
};

EDRV2.HTTP.TransmitRequest.prototype.requestGet = function ( isAsync )
{
	/// <summary>Transmit data using GET method.</summary>
	/// <param name="isAsync">True to transmit asynchronously, False otherwise (if missing instance isAsynchronous will be used).</param>

	try
	{
		// validation
		if ( this.isUsable == false ) throw new Error( this.errorMessage );

		this.validate();


	}
	catch ( e )
	{
		throw new Error( 'Unable to transmit data (GET): ' + e.message );
	}
};
/****************************************************
EDRV2.HTTP.TransmitRequest class.
*****************************************************/

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//Name:     EDRV2.EventCollector
//Purpose:  Allows registration and execution of events and their subscriptions
//Desc:     This class implements an augmented singleton pattern that allows for private / public variables and methods
EDRV2.EventCollector = function ()
{
	//Private variables
	var m_handlers = {};

	function addHandlerExecute( type, handler )
	{
		//Check to see if we have handlers for the type already defined
		if ( typeof m_handlers[type] == "undefined" ) { m_handlers[type] = []; }  //Not yet defined, so do so
		m_handlers[type].push( handler );  //Add the handler
	};

	function fireExecute( event )
	{
		//Prep - ensure we have a target
		if ( !event.target ) { event.target = this; } //Ensure there is a target for the event

		//If we have handlers, then call them one by one
		if ( m_handlers[event.type] instanceof Array )
		{
			var handlers = m_handlers[event.type]
			for ( var i = 0; i < handlers.length; i++ )
			{
				handlers[i]( event ); //call it!
			}
		}
	};

	function removeHandlerExecute( type, handler )
	{
		//If we have items, then find the match and delete it
		if ( m_handlers[type] instanceof Array )
		{
			var handlers = m_handlers[event.type]
			for ( var i = 0; i < handlers.length; i++ )
			{
				if ( handlers[i] === handler ) { break; }  //Find the match, exit when found
			}

			//Remove the item at the index of the match
			handlers.splice( i, 1 );
		}
	};

	//Public methods and properties
	var eventObserverSingleton =
    {
    	addHandler: function ( type, handler )
    	{
    		addHandlerExecute( type, handler ); //Forward the call
    	},
    	fire: function ( event )
    	{
    		fireExecute( event );  //Forward the call
    	},
    	removeHandler: function ( type, handler )
    	{
    		removeHandlerExecute( type, handler );  //Forward the call to unregister the event handler
    	}
    }
	return eventObserverSingleton;
}();

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//Name:     EDRError
//Purpose:  Custom implementation of the Error class
//Desc:     Adds EDR specific functionality to the base Error class
EDRV2.EDRError = function ( message )
{
	///<summary>EDRError represents a custom derived error class that allows for data items</summary>
	///<remarks>Extends Error</remarks>
	if ( this instanceof EDRV2.EDRError )
	{
		Error.apply( this, arguments );
		this.base = Error.prototype;

		this.data = [];
	}
	else
	{
		return new EDRV2.EDRError( message );
	}
};
EDRV2.EDRError.prototype = new Error();
EDRV2.EDRError.prototype.constructor = EDRV2.EDRError;
EDRV2.EDRError.prototype.data = null; //Format {source:, name:, value: }
EDRV2.EDRError.prototype.canContinue = true;
EDRV2.EDRError.prototype.requiresSubmit = true;
EDRV2.EDRError.prototype.referenceID = '';
EDRV2.EDRError.prototype.toString = function ()
{
	//Declare work variables
	var result = '';
	var dataItem = null;

	//Compute the string representation
	result += 'MessageAAA' + this.message + 'BBB';
	result += 'CanContinueAAA' + this.canContinue + 'BBB';
	result += 'RequiresSubmitAAA' + this.requiresSubmit + 'BBB';
	result += 'ReferenceIDAAA' + this.referenceID + 'BBB';
	result += 'DataAAA';
	for ( i = 0, dataItem; dataItem = this.data[i]; i++ )
	{
		result += 'MethodCCC' + dataItem.method + 'DDD';
		result += 'MessageCCC' + dataItem.message + 'DDD';
		if ( ( typeof ( dataItem.showable ) == 'undefined' ) || ( dataItem.showable == null ) ) { dataItem.showable = true; }
		result += 'ShowableCCC' + dataItem.showable + 'DDD';
		result += 'ValueCCC' + dataItem.value + 'DDD';
	}

	//Return the final result
	return result;
};

EDRV2.rethrowError = function ( err, errDataItems, dataItemMethod, canContinue, requiresSubmit )
{
	///<summary>Rethrows an EDRError with the dataitems concatenated</summary>
	/// <param name="err">The error thrown in the caller</summary>
	/// <param name="errDataItems">The data items to be added</summary>
	/// <param name="dataItemMethod">The data items method to use on any data items with this value not specified</summary>

	//Declare work variables
	var eError = null;

	//Preconditions
	if ( ( typeof ( err ) == 'undefined' ) || ( err == null ) ) { throw new Error( "err is required" ); }

	//Convert the error to an EDRError
	eError = EDRV2.convertError( err, errDataItems, dataItemMethod, canContinue, requiresSubmit );

	//Now rethrow the updated / new EDR error
	throw eError;
};

EDRV2.convertError = function ( err, errDataItems, dataItemMethod, canContinue, requiresSubmit )
{
	///<summary>Returns an EDRError</summary>
	/// <param name="err">The error thrown in the caller</summary>
	/// <param name="errDataItems">The data items to be added</summary>
	/// <param name="dataItemMethod">The data items method to use on any data items with this value not specified</summary>

	//Declare work variables
	var eError = null;

	//Preconditions
	if ( ( typeof ( err ) == 'undefined' ) || ( err == null ) ) { throw new Error( "err is required" ); }
	if ( ( typeof ( errDataItems ) == 'undefined' ) || ( errDataItems == null ) ) { errDataItems = []; }
	if ( ( typeof ( canContinue ) == 'undefined' ) || ( canContinue == null ) ) { canContinue = true; } //Set to default if not specified
	if ( ( typeof ( requiresSubmit ) == 'undefined' ) || ( requiresSubmit == null ) ) { requiresSubmit = true; } //Set to default if not specified

	if ( !( errDataItems instanceof Array ) )
	{
		//Not an array, so make it one!
		var dataItem = errDataItems;
		errDataItems = [];
		errDataItems.push( dataItem );
	}

	//Make sure we have an EDRError
	if ( err instanceof EDRV2.EDRError )
	{
		eError = err; //We have a EDRError, so we are good
		if ( canContinue == false ) { eError.canContinue = canContinue; } //Only set this if it is false (never overwrite false with true)
		if ( requiresSubmit == false ) { eError.requiresSubmit = requiresSubmit; } //Only set this if it is false (never overwrite false with true)
	}
	else
	{
		//Not an EDRError, so create it
		eError = new EDRV2.EDRError();
		eError.message = err.message;
		eError.number = err.number;
		eError.name = err.name;
		eError.canContinue = canContinue;
		eError.requiresSubmit = requiresSubmit;
		delete err;
	}

	//Update the method values on the data where not set, using the param if supplied
	if ( EDRV2.trim( dataItemMethod ) != '' )
	{
		for ( i = 0; i < errDataItems.length; i++ )
		{
			if ( ( typeof ( errDataItems[i].method ) == 'undefined' ) || ( errDataItems[i].method == null ) || ( errDataItems[i].method == '' ) ) { errDataItems[i].method = dataItemMethod; }
		}
	}

	//Now set the data and return the updated / new EDR error
	eError.data = eError.data.concat( errDataItems );
	return eError;
};

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//Name:     EDRErrorData
//Purpose:  Data container for EDRErrors
//Desc:     Allows data details to be created
EDRV2.EDRErrorData = function ( errData )
{
	///<summary>Represents error data for use in the EDRError object</summary>
	/// <param name="errData">The error data: ex. { method: "DKTest.testErrors", message: "somename", showable: true, submit: true, value: 'someval' }</summary>
	if ( this instanceof EDRV2.EDRErrorData )
	{
		if ( errData != null ) { EDRV2.copyObjectData( errData, this ); } //convert from JSON to our object so all default values, etc. are correctly set
	}
	else
	{ return new EDRV2.EDRErrorData( errData ); }
};
EDRV2.EDRErrorData.prototype.constructor = EDRV2.EDRErrorData;
EDRV2.EDRErrorData.prototype.method = '';
EDRV2.EDRErrorData.prototype.message = '';
EDRV2.EDRErrorData.prototype.showable = true;
EDRV2.EDRErrorData.prototype.value = '';

/***************************************************************************************************
EDRV2.DebugWindow

DebugWindow is a singleton object that allows page to display debuggin information on the screen.

Usage:
EDRV2.DebugWindow.show();
EDRV2.DebugWindow.hide();
EDRV2.DebugWindow.addMessage(src, msg);
****************************************************************************************************/
EDRV2.DebugWindow = function ()
{
	/// <summary>DebugWindow is a singleton object that allows page to display debuggin information on the screen.</summary>

	// this is the main container of the window
	var dbgNd = null;
	var cntNd = null;
	var hdrNd = null;
	var dbgCntr = null;
	var dbgWinMsg = '';

	function buildMessage( isHeader, src, msg )
	{
		/// <summary>Builds message for debug window.</summary>
		/// <param name="isHeader">True if this is header row, False if this is message row.</param>
		/// <param name="src">Message source.</param>
		/// <param name="msg">Message to display.</param>

		src = src || 'UNKNOWN';
		msg = msg || '';

		if ( isHeader )
		  return '<div style=\'position: relative; clear: both; font-size: 10pt; \'><div style=\'float: left; width: 100px; border-right: 1px solid gray;\'>TIMESTAMP</div><div style=\'float: left; width: 250px; border-right: 1px solid gray;\'>' + src + '</div><div style=\'float: left; max-width: 430px;\'>' + msg + '</div><div style=\'float: right; cursor: pointer;\' onclick=\'javascript: EDRV2.DebugWindow.hide();\'>[X]</div></div>';
		else
		{
			var curTime = new Date();
			var ts = '' + curTime.getHours() + ':' + curTime.getMinutes() + ':' + curTime.getSeconds();
			return '<div style=\'position: relative; clear: both; border-top: 1px solid gray;\'><div style=\'float: left; width: 100px; border-right: 1px solid gray;\'>' + ts + '</div><div style=\'float: left; width: 250px; border-right: 1px solid gray;\'>' + src + '</div><div style=\'float: left; max-width: 410px;\'>' + msg + '</div></div>';
		}
	}

	var isInit = function ()
	{
		/// <summary>Initializes the debug window.</summary>

		try
		{
			// main div
			dbgNd = document.createElement( 'DIV' );
			dbgNd.id = '_EDRDbgWin';

			EDRV2.DOM.applyElementStyle( dbgNd, 'position: absolute; font-family: Arial; font-size: 8pt; left: 0px; bottom: 0px; width: 800px; height: 200px; border: 1px solid Gray; display: block; background-color: White; opacity: 1;' );

			// add header div
			hdrNd = document.createElement( 'DIV' );

			hdrNd.id = '_EDRDbgHdr';
			hdrNd.innerHTML = buildMessage( true, "SOURCE", "Message" );

			dbgNd.appendChild( hdrNd );

			EDRV2.DOM.applyElementStyle( hdrNd, 'position: relative; margin-left: 5px; margin-right: 5px; margin-top: 5px; height: 20px; background-color: #C0C0C0; opacity: 1;' );

			// add content div
			cntNd = document.createElement( 'DIV' );

			dbgNd.appendChild( cntNd );

			EDRV2.DOM.applyElementStyle( cntNd, 'position: relative; margin: 5px; height: 165px; background-color: #F0F0F0; overflow: scroll; opacity: 1;' );

			cntNd.innerHTML = buildMessage( false, "DBGWIN", "Initialized" );

			return true;
		}
		catch ( e )
		{
			// error initializing
			dbgWinMsg = 'Unable to initialize debug window: ' + e.message;
			return false;
		}
	}();

	var debugWin =
	{
		show: function ()
		{
			/// <summary>Displays debug window.</summary>

			// validation
			if ( !isInit ) return false;
			if ( document.body == null ) return false;

			if ( !EDRV2.DOM.isElementInDocument( dbgNd ) )
			{
				// add into DOM since it is not in
				document.body.appendChild( dbgNd );

				// set movable
				if ( dbgCntr == null )
				{
					dbgCntr = new EDRV2.Container( dbgNd );
					dbgCntr.setPopable( { autoReposition: true, position: EDRV2.DOM.popupDIV.prototype.POSITIONS.MiddleMiddle } );
				}

				dbgCntr.setMovable( hdrNd );
			}

			dbgCntr.show( null, EDRV2.DOM.popupDIV.prototype.POSITIONS.BottomLeft );

			return true;
		},

		hide: function ()
		{
			/// <summary>Hides debug window.</summary>

			// validation
			if ( !isInit ) return false;
			if ( document.body == null ) return false;

			// unset movable
			if ( dbgCntr != null )
			{
				dbgCntr.setMovable( null );
				dbgCntr.hide();
			}

			return true;
		},

		addMessage: function ( src, msg )
		{
			/// <summary>Adds new message into debug window.</summary>
			/// <param name="src">Message source.</param>
			/// <param name="msg">Message to display.</param>

			// validation
			if ( !isInit ) return false;
			if ( document.body == null ) return false;

			cntNd.innerHTML = buildMessage( false, src, msg ) + cntNd.innerHTML;
		}
	};

	return debugWin;

}();
/***************************************************************************************************
EDRV2.DebugWindow
****************************************************************************************************/

/***************************************************************************************************
EDRV2.Container

Provides functionalities to manipulate a container (like moving, positioning)

var cntr = new EDRV2.Container('_ConainerDiv');

cntr.setMovable('_TriggerDiv');
cntr.setMovable(null);

cntr.setPopable(opts);
cntr.show(parNode, position);
cntr.hide();
****************************************************************************************************/
EDRV2.Container = function ( containerElem )
{
	/// <summary>Provides functionalities to manipulate a container (like moving, positioning).</summary>
	/// <param name="containerElem">ID of the container.</summary>

	if ( this instanceof EDRV2.Container )
	{
		try
		{
			// inheritance
			EDRV2.ObjectBase.apply( this, arguments );
			this.base = EDRV2.ObjectBase.prototype;

			// validate
			var ctnr = EDRV2.DOM.getElement( containerElem );

			if ( ctnr == null ) throw new Error( 'Unable to initialize container: containerElem does not exist.' );

			// keep the ref as is to support either element ID or element object
			this.containerElem = containerElem;

			this.isUsable = true;
		}
		catch ( e )
		{
			// unusable
			this.isUsable = false;
			this.errorMessage = e.message;
		}
	}
	else
		return new EDRV2.Container( containerElem );
};

// define prototype
EDRV2.Container.prototype = new EDRV2.ObjectBase();
EDRV2.Container.prototype.constructor = EDRV2.Container;

// properties
EDRV2.Container.prototype.containerElem = null;

// enums 

// note that the first 9 POSITIONS values MUST match EDRV2.DOM.popupDIV.prototype.POSITIONS since it has be use
// interchangeably
EDRV2.Container.prototype.POSITIONS = { Unknown: 0, TopLeft: 1, TopMiddle: 2, TopRight: 3, MiddleLeft: 4, MiddleMiddle: 5, MiddleRight: 6, BottomLeft: 7, BottomMiddle: 8, BottomRight: 9 };
EDRV2.Container.prototype.EVENTTYPES = { Unknown: 0, MouseUp: 'MouseUp', MouseDown: 'MouseDown', MouseMove: 'MouseMove' };

// move-able methods
EDRV2.Container.prototype.movableData = null;

EDRV2.Container.prototype.setMovable = function ( triggerElem )
{
	/// <summary>Setup container to be movable/draggable.</summary>
	/// <param name="triggerElem">Element or the ID of the element that triggers move.</param>
	try
	{
		// validation
		if ( !this.isUsable ) return false;

		var evt = null;

		// reset/disable movable if trigger ID is null
		triggerElem = triggerElem || null;

		if ( triggerElem == null )
		{
			if ( this.movableData != null )
			{
				if ( this.movableData.evtMD != null )
				{
					// remove mouse down event
					evt = this.movableData.evtMD;
					EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

					delete evt;
					this.movableData.evtMD = null;
				}

				if ( this.movableData.evtMU != null )
				{
					// remove mouse up event
					evt = this.movableData.evtMU;
					EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

					delete evt;
					this.movableData.evtMU = null;
				}

				if ( this.movableData.evtMO != null )
				{
					// remove mouse out event
					evt = this.movableData.evtMO;
					EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

					delete evt;
					this.movableData.evtMO = null;
				}

				if ( this.movableData.evtMM != null )
				{
					// remove mouse move event
					evt = this.movableData.evtMM;
					EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

					delete evt;
					this.movableData.evtMM = null;
				}
			}

			// reset it
			this.movableData = null;

			return false;
		}

		// get trigger element
		var tElem = EDRV2.DOM.getElement( triggerElem );

		if ( tElem == null ) throw new Error( 'triggerElem does not exist.' );

		// clear current movable data if neccessary
		if ( this.movableData != null ) this.setMovable( null );

		// anonymous to handle mouseup
		var mouseUp = function ( evt )
		{
			try
			{
				// stop propagation
				EDRV2.DOM.EVENT.stopPropagation( evt );

				// clear mouseout and mousemove
				if ( this.movableData.evtMO != null )
				{
					// remove mouse out event
					evt = this.movableData.evtMO;
					EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

					delete evt;
					this.movableData.evtMO = null;
				}

				if ( this.movableData.evtMM != null )
				{
					// remove mouse move event
					evt = this.movableData.evtMM;
					EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

					delete evt;
					this.movableData.evtMM = null;
				}

				// clear data
				this.movableData.orgMP = null;
				this.movableData.orgCP = null;
				this.movableData.isMD = false;

				// switch cursor
				var tElem = EDRV2.DOM.getElement( this.movableData.tID );
				if ( tElem != null ) EDRV2.DOM.applyElementStyle( tElem, 'cursor: default;' );

				// get container position
				var cntr = EDRV2.DOM.getElement( this.containerElem );
				var pos = EDRV2.DOM.getElementRelativePosition( cntr );

				// raise event to indicate mouse up
				EDRV2.EventCollector.fire( { type: EDRV2.Container.prototype.EVENTTYPES.MouseUp, containerElement: this.containerElem, triggerElement: triggerElem, top: pos.top, left: pos.left } );

				return false;
			}
			catch ( e )
			{
				EDRV2.DebugWindow.addMessage( 'CONTAINER', 'Unable to trap MOUSEUP event: ' + e.message );
				return false;
			}
		};

		var mouseDown = function ( evt )
		{
			try
			{
				// stop propagation
				EDRV2.DOM.EVENT.stopPropagation( evt );

				// get container
				var cntr = EDRV2.DOM.getElement( this.containerElem );
				if ( cntr == null ) throw new Error( 'containerElem does not exist.' );

				// get container position
				var cntrPos = EDRV2.DOM.getElementPosition( cntr );
				if ( cntrPos == null ) throw new Error( 'Unable to get container current position.' );

				// get container parent position
				var parCntrPos = EDRV2.DOM.getElementPosition( cntr.parentNode );
				if ( parCntrPos == null ) throw new Error( 'Unable to get parent\'s container current position.' );

				// keep original positions
				this.movableData.orgMP = [evt.clientX, evt.clientY];
				this.movableData.orgCP = [( cntrPos.left - parCntrPos.left ), ( cntrPos.top - parCntrPos.top )];

				// trap mousemove event
				this.movableData.evtMM = EDRV2.DOM.EVENT.addEventHandler( document, 'mousemove', EDRV2.bindFunction( mouseMove, this ) );
				this.movableData.isMD = true;

				// switch cursor
				var tElem = EDRV2.DOM.getElement( this.movableData.tID );
				if ( tElem != null ) EDRV2.DOM.applyElementStyle( tElem, 'cursor: move;' );

				// get container position
				var cntr = EDRV2.DOM.getElement( this.containerElem );
				var pos = EDRV2.DOM.getElementPosition( cntr );

				// raise event to indicate mouse up
				EDRV2.EventCollector.fire( { type: EDRV2.Container.prototype.EVENTTYPES.MouseDown, containerElement: this.containerElem, triggerElement: triggerElem, top: pos.top, left: pos.left } );

				return false;
			}
			catch ( e )
			{
				EDRV2.DebugWindow.addMessage( 'CONTAINER', 'Unable to trap MOUSEDOWN event: ' + e.message );
				return false;
			}
		};

		var mouseMove = function ( evt )
		{
			try
			{
				// stop propagation
				EDRV2.DOM.EVENT.stopPropagation( evt );

				// get container
				var cntr = EDRV2.DOM.getElement( this.containerElem );
				if ( cntr == null ) throw new Error( 'containerElem does not exist.' );

				// exit if no original points
				if ( this.movableData.orgMP == null ) return false;
				if ( this.movableData.orgCP == null ) return false;

				// calculate distance
				var curMx = evt.clientX;
				var curMy = evt.clientY;

				var x = ( curMx - this.movableData.orgMP[0] ) + this.movableData.orgCP[0];
				var y = ( curMy - this.movableData.orgMP[1] ) + this.movableData.orgCP[1];

				// move it
				EDRV2.DOM.applyElementStyle( cntr, 'top: ' + y + 'px; left: ' + x + 'px;' );

				// raise event to indicate mouse up
				EDRV2.EventCollector.fire( { type: EDRV2.Container.prototype.EVENTTYPES.MouseMove, containerElement: this.containerElem, triggerElement: triggerElem, top: y, left: x } );

				return false;
			}
			catch ( e )
			{
				EDRV2.DebugWindow.addMessage( 'CONTAINER', 'Unable to trap MOUSEMOVE event: ' + e.message );
				return false;
			}
		}

		// create new data
		this.movableData = { tID: triggerElem, isMD: false, evtMD: null, evtMU: null, evtMM: null, evtMO: null, orgMP: null, orgCP: null };

		this.movableData.evtMD = EDRV2.DOM.EVENT.addEventHandler( tElem, 'mousedown', EDRV2.bindFunction( mouseDown, this ) );
		this.movableData.evtMU = EDRV2.DOM.EVENT.addEventHandler( tElem, 'mouseup', EDRV2.bindFunction( mouseUp, this ) );
		this.movableData.evtMO = EDRV2.DOM.EVENT.addEventHandler( tElem, 'mouseout', EDRV2.bindFunction( mouseUp, this ) );

		return true;
	}
	catch ( e )
	{
		this.movableData = null;
		throw Error( 'Unable to set MOVABLE: ' + e.message );
	}
};

// pop-able methods
EDRV2.Container.prototype.popableData = null;

EDRV2.Container.prototype.setPopable = function ( opts )
{
	/// <summary>Setup container to be a "pop-up" DIV.</summary>
	/// <param name="opts">Popup options.</param>
	/// <remarks>Once set to be "popable", the affect can't be reversed.</remarks>

	try
	{
		// create default options object
		opts = opts || { autoReposition: true, position: this.POSITIONS.MiddleMiddle };

		// create default options
		opts.autoReposition = opts.autoReposition || true;
		opts.position = opts.position || this.POSITIONS.MiddleMiddle;

		// if already exist - just change the options
		if ( this.popableData != null )
		{
			this.popableData.autoReposition = opts.autoReposition;

			// note that there is a chance resize event is already captured - remove it if needed
			if ( ( !this.popableData.autoReposition ) && ( this.popableData.evtPR != null ) )
			{
				var evt = this.popableData.evtPR;
				EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

				this.popableData.evtPR = null;
				delete evt;
			}

			return true;
		}

		// since does not exist - set it up
		this.popableData = { nd: null, pnd: null, autoReposition: opts.autoReposition, position: opts.position, evtPR: null };

		// get the node and parent node
		this.popableData.nd = EDRV2.DOM.getElement( this.containerElem );
		this.popableData.pnd = this.popableData.nd.parentNode;

		// since the hide(), show() method does not depend on display or visibility css attribute
		// sets both to be "displayed"
		var curCSSVal = EDRV2.DOM.getElementStyle( this.popableData.nd, 'display' );

		if ( ( curCSSVal != null ) && ( curCSSVal.toLowerCase() == 'none' ) ) EDRV2.DOM.applyElementStyle( this.popableData.nd, 'display: block;' );

		curCSSVal = EDRV2.DOM.getElementStyle( this.popableData.nd, 'visibility' );

		if ( ( curCSSVal != null ) && ( curCSSVal.toLowerCase() == 'hidden' ) ) EDRV2.DOM.applyElementStyle( this.popableData.nd, 'visibility: visible;' );

		// if node is in document - sever the link
		if ( EDRV2.DOM.isElementInDocument( this.popableData.nd ) )
		{
			// remove it from DOM to optimize application
			this.popableData.nd.parentNode.removeChild( this.popableData.nd );
		}

		return true;
	}
	catch ( e )
	{
		this.popableData = null;
		throw new Error( 'Unable to setup container as popup: ' + e.message );
	}
};

EDRV2.Container.prototype.pop = function ( parNode )
{
	/// <summary>Pops container into DOM.</summary>
	/// <param name="parNode">Parent node - NULL to use BODY.</param>

	try
	{
		// validation
		if ( this.popableData == null ) return false;

		// add into DOM if needed
		if ( !EDRV2.DOM.isElementInDocument( this.popableData.nd ) )
		{
			// use original parent node if available and parNode not specified
			parNode = parNode || this.popableData.pnd;

			// use body if still not available
			if ( parNode == null ) parNode = document.body;

			// pop-it
			parNode.appendChild( this.popableData.nd );

			// set ref to parNode
			this.popableData.pnd = parNode;
		}

		return true;
	}
	catch ( e )
	{
		throw new Error( 'Unable to pop element: ' + e.message );
	}
};

EDRV2.Container.prototype.show = function ( parNode, position )
{
	/// <summary>Shows container as a pop-up.</summary>
	/// <param name="parNode">Parent node - NULL to use BODY.</param>
	/// <param name="position">One of EDRV2.Container.prototype.POSITIONS values.</param>

	try
	{
		// allow calls to this function for DIV that has not been set as "popable"
		// but caller MUST specify position

		// validation
		if ( this.popableData == null )
		{
			// get element
			var elem = EDRV2.DOM.getElement( this.containerElem );

			// check parameters
			if ( ( elem != null ) && ( typeof ( position ) != 'undefined' ) && ( position != null ) )
			{
				// use body if parNode not specified
				parNode = parNode || document.body;

				EDRV2.DOM.setElementPosition( elem, position, ( parNode == document.body ) );
				EDRV2.DOM.showElement( elem );

				return true;
			}
			else
				return false;
		}

		// pop the element first
		this.pop( parNode );

		// display it so set element can work property (since size calculation
		// requires element to be visible)
		EDRV2.DOM.showElement( this.popableData.nd );

		// use default position if needed
		if ( ( typeof ( position ) == 'undefined' ) || ( position == null ) ) position = this.popableData.position;

		// set position
		EDRV2.DOM.setElementPosition( this.popableData.nd, position, ( this.popableData.pnd == document.body ) );

		// set autoposition if needed
		if ( ( this.popableData.autoReposition ) && ( this.popableData.evtPR == null ) )
		{
			this.popableData.evtPR = EDRV2.DOM.EVENT.addEventHandler( window, 'resize', EDRV2.bindFunction( function ( evt ) { this.show( parNode, position ); }, this ) );
		}

		return true;
	}
	catch ( e )
	{
		throw new Error( 'Unable to show pop-up element: ' + e.message );
	}
};

EDRV2.Container.prototype.showAtSpecificPosition = function ( parNode, top, left )
{
	/// <summary>Shows container as a pop-up at specific position.</summary>
	/// <param name="parNode">Parent node - NULL to use BODY.</param>
	/// <param name="top">Top pixel coordinate.</param>
	/// <param name="left">Left pixel coordinate.</param>

	try
	{
		// allow calls to this function for DIV that has not been set as "popable"
		// but caller MUST specify position

		// validation
		if ( this.popableData == null )
		{
			// get element
			var elem = EDRV2.DOM.getElement( this.containerElem );

			// check parameters
			if ( elem != null )
			{
				// use body if parNode not specified
				parNode = parNode || document.body;

				// set top, left position
				EDRV2.DOM.applyElementStyle( elem, 'top: ' + top + 'px; left: ' + left + 'px;' );
				EDRV2.DOM.showElement( elem );

				return true;
			}
			else
				return false;
		}

		// pop the element first
		this.pop( parNode );

		// display it so set element can work property (since size calculation
		// requires element to be visible)
		EDRV2.DOM.showElement( this.popableData.nd );

		// set top, left position
		EDRV2.DOM.applyElementStyle( elem, 'top: ' + top + 'px; left: ' + left + 'px;' );

		// set autoposition if needed
		if ( ( this.popableData.autoReposition ) && ( this.popableData.evtPR == null ) )
		{
			this.popableData.evtPR = EDRV2.DOM.EVENT.addEventHandler( window, 'resize', EDRV2.bindFunction( function ( evt ) { this.showAtSpecificPosition( parNode, top, left ); }, this ) );
		}

		return true;
	}
	catch ( e )
	{
		throw new Error( 'Unable to show pop-up element: ' + e.message );
	}

};

EDRV2.Container.prototype.hide = function ()
{
	/// <summary>Hides container as a pop-up.</summary>

	try
	{
		// allow calls to this function for DIV that has not been set as "popable"
		// since we can just hide the element

		// validation
		if ( this.popableData == null )
		{
			// get element
			var elem = EDRV2.DOM.getElement( this.containerElem );

			if ( elem != null ) EDRV2.DOM.hideElement( elem );

			return false;
		}

		// remove handler
		if ( this.popableData.evtPR != null )
		{
			var evt = this.popableData.evtPR;
			EDRV2.DOM.EVENT.removeEventHandler( evt.domElement, evt.eventName, evt.handler, evt.useCapturePhase );

			this.popableData.evtPR = null;
			delete evt;
		}

		// remove from parent
		if ( EDRV2.DOM.isElementInDocument( this.popableData.nd ) ) this.popableData.nd.parentNode.removeChild( this.popableData.nd );

		return true;
	}
	catch ( e )
	{
		throw new Error( 'Unable to hide pop-up element: ' + e.message );
	}
};
/***************************************************************************************************
EDRV2.Container
****************************************************************************************************/

/*************************************************************************
START: EDRV2.browserDetect
Detects/determines current browser.
Source: http://www.quirksmode.org/js/detect.html
**************************************************************************/
EDRV2.browserDetect =
{
	init: function ()
	{
		try
		{
			// add flag whether we were successful in getting the information
			this.isUsable = true;
			this.errorMessage = '';

			this.browser = this.searchString( this.dataBrowser ) || "An unknown browser";
			this.version = this.searchVersion( navigator.userAgent )
			|| this.searchVersion( navigator.appVersion )
			|| "an unknown version";
			this.OS = this.searchString( this.dataOS ) || "an unknown OS";
		}
		catch ( e )
		{
			this.isUsable = false;
			this.errorMessage = 'Unable to detect browser type: ' + ex.message;
		}
	},
	searchString: function ( data )
	{
		for ( var i = 0; i < data.length; i++ )
		{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if ( dataString )
			{
				if ( dataString.indexOf( data[i].subString ) != -1 )
					return data[i].identity;
			}
			else if ( dataProp )
				return data[i].identity;
		}
	},
	searchVersion: function ( dataString )
	{
		var index = dataString.indexOf( this.versionSearchString );
		if ( index == -1 ) return;
		return parseFloat( dataString.substring( index + this.versionSearchString.length + 1 ) );
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{
			string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		},
		{
			prop: window.opera,
			identity: "Opera",
			versionSearch: "Version"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS: [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
			string: navigator.userAgent,
			subString: "iPhone",
			identity: "iPhone/iPod"
		},
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]
};

EDRV2.browserDetect.init();
/**************************************************************************
END: EDRV2.browserDetect
**************************************************************************/


/**************************************************************************
BEGIN: EDRV2.inherits
**************************************************************************/


EDRV2.inherits = function(childCtor, parentCtor) {
	///<summary>Handles proper way of inheriting an object</summary>
	///<param name="childCtor">Object that will inherit</param>
	///<param name="parentCtor">Object that will be inherited</param>
	///<remarks>Reference: http://stackoverflow.com/questions/9812783/cannot-inherit-google-maps-map-v3-in-my-custom-class-javascript </remarks>
	function tempCtor() {};
	tempCtor.prototype = parentCtor.prototype;
	childCtor.superClass_ = parentCtor.prototype;
	childCtor.prototype = new tempCtor();
	childCtor.prototype.constructor = childCtor;
};

/**************************************************************************
END: EDRV2.inherits
**************************************************************************/

