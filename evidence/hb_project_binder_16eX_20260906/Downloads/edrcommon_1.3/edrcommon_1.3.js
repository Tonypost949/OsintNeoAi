// JavaScript source code
( function ()
{
  'use strict';

	angular.module( 'EDR.Logging', [] )

	.value( 'appInfo', { appName: '--UNKNOWN--', appVersion: '0.0.00' } )

	.factory( 'logService', ['appInfo', function ( appInfo )
	{
		/*
			Logging Service
		*/
		var thisSvc = {};

		thisSvc.SEVERITIES = { INFO: 'INFO', WARNING: 'WARNING', ERROR: 'ERROR', CRASHED: 'CRASHED' };

		/*
			@name logService.log() - log information to logging facility
		*/
		thisSvc.log = function ( severity, brief, msg, elapsedInMS )
		{
			try
			{
				console.log( appInfo.appName + ':' + severity + ': ' + msg );
			}
			catch ( e )
			{
				// ignore since we're just using console 
			}
		};

		return thisSvc;
	}] )

	.factory( 'trackingService', [function ( appInfo )
	{
		/*
			Tracking service for EDR angular app
		*/
		var thisSvc = {};

		/*
			@name trackingService.track() - track information to tracking facility
		*/
		thisSvc.track = function () { };

		return thisSvc;
	}] );


	angular.module( 'EDR.HTTP.Utilities', ['EDR.Logging'] )

	.value( 'knownHosts',
	[
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
	]
	)

	.factory( 'urlService', ['$location', 'logService', 'knownHosts', function ( $location, logService, knownHosts )
	{
		/*
			HTTP Utilities Service
		*/
		var $$href = document.createElement( 'A' );

		var thisSvc = {};

		/*
			@name urlService.buildURL() - build URL
		*/
		thisSvc.buildURL = function ( host, path, qryStrs, useDocProtocol )
		{
			try
			{
				// use current location to determine protocol + port
			  var url = $location.protocol() + '://' + host + ':' + $location.port() + path;
        

				// append ? if needed
				if ( url.indexOf( '?' ) === -1 ) url += '?';

				// build query string
				if ( qryStrs instanceof Array )
				{
					for ( var i = 0; i < qryStrs.length; i++ )
					{
						url += '&' + qryStrs[i].key + '=' + encodeURIComponent( qryStrs[i].value );
					}
				}

				// done
				return url;
			}
			catch ( e )
			{
				logService.log( logService.SEVERITIES.ERROR, 'urlService.buildURL()', e.message );
				throw e;
			}
		};

	  /*
			@name urlService.buildURLv2() - build URL with port
		*/
		thisSvc.buildURLv2 = function ( host, port, path, qryStrs, useDocProtocol )
		{
		  try
		  {
		    // use current location to determine protocol + port
		    var url = $location.protocol() + '://' + host + ':' + (port === null? $location.port: port);

		    if (path[0] !== '/') path = '/' + path;

		    url += path;

		    // append ? if needed
		    if ( url.indexOf( '?' ) === -1 ) url += '?';

		    // build query string
		    if ( qryStrs instanceof Array )
		    {
		      for ( var i = 0; i < qryStrs.length; i++ )
		      {
		        url += '&' + qryStrs[i].key + '=' + encodeURIComponent( qryStrs[i].value );
		      }
		    }

		    // done
		    return url;
		  }
		  catch ( e )
		  {
		    logService.log( logService.SEVERITIES.ERROR, 'urlService.buildURL()', e.message );
		    throw e;
		  }
		};

	  /*
			@name urlService.switchHostAndProtocol() - take a URL and change the host to the known host and use the document protocol
		*/
		thisSvc.switchHostAndProtocol = function (url)
		{
		  try
		  {
		    // parse the URL
		    var parsedURL = thisSvc.parseURL(url);
        
		    if (parsedURL === null) return null;

		    // rebuild it
		    return thisSvc.buildURLv2(thisSvc.translateHost(parsedURL.host), parsedURL.port, parsedURL.pathName, null, true);
		  }
		  catch (e)
		  {
		    logService.log(logService.SEVERITIES.ERROR, 'urlService.switchHostAndProtocol()', e.message);
		    throw e;
		  }
		};
	
		/*
			@name urlService.parseURL() - parse URL
		*/
		thisSvc.parseURL = function ( url )
		{
			try
			{
				// validate
				if ( angular.isUndefined( url ) ) return null;

				// use A to parse URL (yes .. cheating gooooood)
				this.$$hRef.href = url;

				// make it easier to ref
				var loc = this.$$hRef;

				return { protocol: loc.protocol, schema: loc.schema, host: loc.host, hostName: loc.hostname, port: loc.port, pathName: loc.pathname, hash: loc.hash, queryString: loc.search };
			}
			catch ( e )
			{
				logService.log( logService.SEVERITIES.ERROR, 'urlService.parseURL()', e.message );
				throw e;
			}
		};

		/*
			@name urlService.translateHost() - translate production host to the corresponding host on current
		*/
		thisSvc.translateHost = function ( targetProductionHost )
		{
			try
			{
				// validate
				if ( angular.isUndefined( targetProductionHost ) || ( targetProductionHost == null ) )
				{
					logService.log( logService.SEVERITIES.WARNING, 'urlService.translateHost()', 'targetHost is undefined or null' );
					return null;
				}

				// 
				targetProductionHost = targetProductionHost.toLowerCase();
				var currentHost = $location.host().toLowerCase();

				// find matching translation
				for ( var i = 0; i < knownHosts.length; i++ )
				{
					if ( knownHosts[i].key === targetProductionHost )
					{
						for ( var j = 0; j < knownHosts[i].hosts.length; j++ )
						{
							if ( knownHosts[i].hosts[j].currentHost === currentHost )
							{
								logService.log( logService.SEVERITIES.INFO, 'urlService.translateHost()', 'Found ' + targetProductionHost + ' translation for ' + currentHost + ' as ' + knownHosts[i].hosts[j].targetHost );
								return knownHosts[i].hosts[j].targetHost;
							}
						}
					}
				}

				// default to the passed in host
				logService.log( logService.SEVERITIES.WARNING, 'urlService.translateHost()', 'Unable to find translation for ' + targetProductionHost + ' on ' + currentHost );
				return targetProductionHost;
			}
			catch ( e )
			{
				logService.log( logService.SEVERITIES.ERROR, 'urlService.translateHost()', e.message );
				throw e;
			}
		};

		return thisSvc;
	}] );

} )();
