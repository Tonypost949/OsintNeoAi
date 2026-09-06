/*
EDR namespace.
*/
EDR = {};
EDR.HTTP = {};
EDR.XML = {};
EDR.DOM = {};
EDR.VALIDATION = {};

EDR =
{
	/*
	DisplayObjectProperties()
		
	Displays object properties.
		
	obj: Object to enumerate.
	recurse: True - recurse through the properties, False - otherwise.
	prefix: Prefix the property/function name to indicate object hierarchy.
	*/
	DisplayObjectProperties: function (obj, recurse, prefix)
	{
		// flag whether to recurse
		var recursive = recurse || false;

		// prefix for the property/function name and it is passed in during the recursion
		// process
		var p = EDR.Trim(prefix || '');

		// build msg
		var msg = '';
		if (obj != null)
		{
			for (var i in obj)
			{
				if (i != 'EDRParent')
				{
					try
					{
						msg += p + i + '=' + obj[i] + '\n';

						if ((recursive) && (typeof obj[i] == 'object')) msg += EDR.DisplayObjectProperties(obj[i], recursive, p + i + '.');
					}
					catch (e)
					{
						// error is thrown if failed to get the value
						msg += i + '--FAILED TO ENUMERATE--\n';
					}
				}
				else
				{
					// EDRParent is specific for EDR JS object to link current object to its parent -- effectively creating circular reference
					if (obj[i] != null)
						msg += p + i + '=' + obj[i].toString() + '\n';
					else
						msg += p + i + '= --NULL--' + '\n';
				}
			}
		}

		return msg;
	},

	/*
	Trim()
		
	Trims spaces at beginning and end of the string.
	*/
	Trim: function (value)
	{
		// clean value
		var val = value || null;
		if (typeof val == 'undefined') return '';
		if (val == null) return '';

		// use regexp to trim
		try
		{
			return val.replace(/^\s+|\s+$/, '');
		}
		catch (e)
		{
			return '';
		}
	},

	/*
	CopyObjectData()

	Copies data from src to dest by looping through properties of dest
	and copying the value (of the same property name) from src.

	Note that this method only copies properties that is not of type function

	dest is returned from the function.
	*/
	CopyObjectData: function (src, dest)
	{
		// nothing to do
		if ((src == null) || (dest == null)) return dest;

		var propTypeOf = null;
		for (var destProp in dest)
		{
			propTypeOf = typeof (src[destProp]);
			if ((propTypeOf != 'undefined') && (propTypeOf != 'function')) dest[destProp] = src[destProp];
		}

		return dest;
	},

	/*
	BindFunction()
		
	Binds a handler to run under a specific context. Note this bind using "function currying" to allow parameters to be passed into the
	handler when the callback happens.
		
	fn				: Function pointer.
	context			: Context to execute function in.
	*/
	BindFunction: function (fn, context)
	{
		if (fn == null) return null;

		// remove the first 2 arguments passed in to this function (fn and context)
		// args contains additional parameters to this function
		var args = Array.prototype.slice.call(arguments, 2);

		// create a closure - this is how function binding works!
		return function ()
		{
			var innerArgs = Array.prototype.slice.call(arguments);
			var finalArgs = args.concat(innerArgs);

			// .apply() executes the function by settings 2 things:
			// 1. the context the function is executed in (null = global)
			// 2. final parameters list
			return fn.apply(context, finalArgs);
		};
	},

	/*
	NameValue object.
	*/
	NameValue: function (name, value)
	{
		if (this instanceof EDR.NameValue)
		{
			this.Name = name;
			this.Value = value;
		}
		else
			return new EDR.NameValue(name, value);
	}
}

EDR.NameValue.prototype.constructor = EDR.NameValue;
EDR.NameValue.prototype.Name = '';
EDR.NameValue.prototype.Value = '';

/****************************************************************************************************************************************************
EDR.NameValue object.
****************************************************************************************************************************************************/

/****************************************************************************************************************************************************
EDR XML Utilities.
****************************************************************************************************************************************************/
EDR.XML =
{
	/*
	IE MS XML types
	Priority is given to the lowest index.
	http://msdn.microsoft.com/en-us/library/windows/desktop/ms757837(v=vs.85).aspx
	*/
	IEMSXMLTypes: ['Msxml2.DOMDocument.6.0', 'MSXML2.DOMDocument.3.0', 'Microsoft.XMLDOM'],

	/*
	IE MSXML XML ProgID used.
	*/
	IEMSXMLProgID: null,

	/*
	XMLDocumentFromString()
		
	Returns XML DOM object w/ the xmlString loaded.
	*/
	XMLDocumentFromString: function (xmlString)
	{
		var parser = null;

		if (window.ActiveXObject)
		{
			// IE
			// reset prog id
			EDR.XML.IEMSXMLProgID = null;

			// IE
			for (var i = 0; i < EDR.XML.IEMSXMLTypes.length; i++)
			{
				parser = null;

				try { parser = new ActiveXObject(EDR.XML.IEMSXMLTypes[i]); } catch (e) { }

				if (parser != null)
				{
					EDR.XML.IEMSXMLProgID = EDR.XML.IEMSXMLTypes[i];
					break;
				}
			}

			if (parser != null)
			{
				parser.async = false;
				parser.loadXML(xmlString);
				return parser;
			}
		}
		else if (window.DOMParser)
		{
			// Mozilla
			parser = new DOMParser();
			return parser.parseFromString(xmlString, 'text/xml');
		}

		// nothing found
		return null;
	},

	/*
	XMLDocumentFromHTTPGet()
		
	Returns XML DOM object w/ data retrieved from calling the URL.
		
	URL is expected to ONLY return XML formatted data and it has been properly URL encoded.
	*/
	XMLDocumentFromHTTPGet: function (url)
	{
		// get data
		var resp = EDR.HTTP.HTTPGet(url);
		if (resp == null) return null;

		if (resp.ContentType != 'text/xml')
		{
			alert('Server did not return XML data.');
			return null;
		}
		else
		// return XmlDoc
			return EDR.XML.XMLDocumentFromString(resp.Data);
	},

	/*
	XMLDocumentFromHTTPPost()
		
	Returns XML DOM object w/ data retrieved from posting to the URL.
		
	URL is expected to ONLY return XML formatted data.
	*/
	XMLDocumentFromHTTPPost: function (url, data, contentType)
	{
		// get data
		var resp = EDR.HTTP.HTTPPost(url, data, contentType);
		if (resp == null) return null;

		if (resp.ContentType != 'text/xml')
		{
			alert('Server did not return XML data.');
			return null;
		}
		else
		// return XmlDoc
			return EDR.XML.XMLDocumentFromString(resp.Data);
	},

	/*
	CreateXPathEvaluator()
    
	Returns XPathEvaluator object for nonIE browsers.
	*/
	CreateXPathEvaluator: function ()
	{
		try { return new XPathEvaluator(); }
		catch (ex) { return null; }
	},

	/*
	SerializeXML()
			
	Serializes XmlDocument to string.
	*/
	SerializeXML: function (xmlDoc)
	{
		// return empty string
		if (xmlDoc == null) return '';

		if (window.XMLSerializer)
		{
			// Mozilla and others (IE 9 supports the interface but
			// does not implement the function
			try
			{
				var ser = new XMLSerializer();
				return ser.serializeToString(xmlDoc.documentElement);
			}
			catch (e)
			{
			}
		}

		if (xmlDoc.xml)
		{
			// IE
			return xmlDoc.xml;
		}

		// at this point nothing else we can do
		throw Error('Unable to serialize XML: Browser does not support interface.');
	}
}
/****************************************************************************************************************************************************
EDR XML Utilities.
****************************************************************************************************************************************************/

/****************************************************************************************************************************************************
EDR Validation Utilities.
****************************************************************************************************************************************************/
EDR.VALIDATION =
{
	/*
	Name:    AreSameValues()
	Desc:    Determines if two values are the same.
	Returns: Returns true or false based on comparison.
	*/
	AreSameValues: function (string1, string2)
	{
		return (string1 == string2);
	},

	/*
	Name:    IsValidEmailSyntax()
	Desc:    Determines if an email address is valid.
	Returns: Returns true if the email is found to be valid, false otherwise.
	*/
	IsValidEmailSyntax: function (email)
	{
		//Preconditions
		if (email == null || email == undefined) { return false; }

		//Regex matching		
		if (email.match(/\s/) != null) { return false; } //White space test
		if (email.match(/[\.]{2}|[\-]{2}/) != null) { return false; } //Multiple .. or --
		if (email.match(/^(([A-Za-z0-9]+_+)|([A-Za-z0-9]+\-+)|([A-Za-z0-9]+\.+)|([A-Za-z0-9]+\++))*[A-Za-z0-9]+@((\w+\-+)|(\w+\.))*\w{1,63}\.[a-zA-Z]{2,6}$/) == null) { return false; } //Invalid email syntax

		return true;  //Valid
	}

}

/****************************************************************************************************************************************************
EDR Validation Utilities.
****************************************************************************************************************************************************/

/****************************************************************************************************************************************************
EDR HTTP utilities.
****************************************************************************************************************************************************/
EDR.HTTP =
{
	/*
	UserAgent
		
	User agent to use when using HTTP request object.
	*/
	UserAgent: 'Mozilla/4.0 (compatible; MSIE 7.0; EDR IDG JS;)',

	/*
	IE MS XML types
	Priority is given to the lowest index.
	http://msdn.microsoft.com/en-us/library/windows/desktop/ms757837(v=vs.85).aspx
	*/
	IEMSXMLHTTPTypes: ['Msxml2.XMLHTTP.6.0', 'MSXML2.XMLHTTP.3.0', 'Microsoft.XMLHTTP'],

	/*
	IE MSXML XMLHTTP ProgID used.
	*/
	IEMSXMLHTTPProgID: null,

	/*
	HTTPRequest()
		
	Returns HTTP request object.
	*/
	HTTPRequest: function ()
	{
		/// <summary>Creates HTTP request object.</summary>
		var httpReq = null;

		if (window.XMLHttpRequest)
		{
			// new browsers
			httpReq = new XMLHttpRequest();
		}
		else if (window.ActiveXObject)
		{
			// reset prog id
			EDR.HTTP.IEMSXMLHTTPProgID = null;

			// IE
			for (var i = 0; i < EDR.HTTP.IEMSXMLHTTPTypes.length; i++)
			{
				httpReq = null;

				try { httpReq = new ActiveXObject(EDR.HTTP.IEMSXMLHTTPTypes[i]); } catch (e) { }

				if (httpReq != null)
				{
					EDR.HTTP.IEMSXMLHTTPProgID = EDR.HTTP.IEMSXMLHTTPTypes[i];
					break;
				}
			}
		}

		return httpReq;
	},

	/*
	HTTPResponse()
		
	Get response data from calling URL.

	Returns NULL if problem, else returns an object w/ 4 properties, ContentType, EncodingType, ContentLength and Data.
	*/
	HTTPGet: function (url)
	{
		// get HTTP req object
		var httpReq = EDR.HTTP.HTTPRequest();
		if (httpReq == null)
		{
			alert('Unable to create HTTP request object.');
			return null;
		}

		var usrAgent = navigator.userAgent || EDR.HTTP.UserAgent;

		// post to URL
		httpReq.open('GET', url, false);
		//httpReq.setRequestHeader('User-Agent', usrAgent);
		httpReq.send(null);

		// parse content type
		var contentType = EDR.HTTP.HTTPParseContentType(httpReq.getResponseHeader('Content-Type'));

		// retrieve data
		var resp = { ContentType: contentType.ContentType, EncodingType: contentType.EncodingType, ContentLength: httpReq.getResponseHeader('Content-Length'), Data: httpReq.responseText };
		httpReq = null;

		return resp;
	},

	/*
	HTTPPost()
		
	Get response from posting to a URL.
		
	Returns NULL if problem, else returns an object w/ 4 properties, ContentType, EncodingType, ContentLength and Data.
	*/
	HTTPPost: function (url, data, fullContentType)
	{
		// get HTTP req object
		var httpReq = EDR.HTTP.HTTPRequest();
		if (httpReq == null)
		{
			alert('Unable to create HTTP request object.');
			return null;
		}

		// post to URL
		httpReq.open('POST', url, false);

		var usrAgent = navigator.userAgent || EDR.HTTP.UserAgent;
		//httpReq.setRequestHeader('User-Agent', usrAgent);

		if (fullContentType)
			httpReq.setRequestHeader('Content-Type', fullContentType);
		else
			httpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

		//if (data)
		//	httpReq.setRequestHeader('Content-Length', data.length);
		//else
		//	httpReq.setRequestHeader('Content-Length', 0);

		httpReq.send(data);

		// parse content type
		var contentType = EDR.HTTP.HTTPParseContentType(httpReq.getResponseHeader('Content-Type'));

		// retrieve data
		var resp = { ContentType: contentType.ContentType, EncodingType: contentType.EncodingType, ContentLength: httpReq.getResponseHeader('Content-Length'), Data: httpReq.responseText };
		httpReq = null;

		return resp;
	},

	/*
	HTTPParseContentType()
		
	Parses Content-Type (<mime_type>; <encoding_type>).
		
	Returns object w/ 2 properties, ContentType, EncodingType.
	*/
	HTTPParseContentType: function (contentType)
	{
		// resp object
		var resp = { ContentType: null, EncodingType: null };

		if (contentType == null) return resp;

		// split by ;
		var tokens = contentType.split(';');

		resp.ContentType = tokens[0];
		resp.EncodingType = tokens[1];

		return resp;
	},

	/*
	UrlComponentEncode()
		
	Properly encodes URL component (key=<component>).
		
	*/
	UrlComponentEncode: function (str)
	{
		// validations
		if (!str) return '';

		str = EDR.Trim(str);
		if (str == '') return '';

		// use escape to do the first pass
		str = escape(str);

		// convert characters that escape() does not convert
		str = str.replace(/[*+\/@]|%20/g, function (s)
		{
			switch (s)
			{
				case '*': return '%2A'; break;
				case '+': return '%2B'; break;
				case '/': return '%2F'; break;
				case '@': return '%40'; break;
				case '%20': return '+'; break;
				default: return s;
			}
		});

		return str;
	},

	CreateDataString: function (nameValuePairs)
	{
		/// <summary>Creates the data string that can be used to send to httphandler</summary>
		/// <param name="nameValuePairs">JSON objects consisting of name / value properties</param>
		var result = '';
		for (var i = 0; i < nameValuePairs.length; i++)
		{
			if (i > 0) result += '&';
			result += nameValuePairs[i].name + '=' + nameValuePairs[i].value;
		}
		return result;
	},

	CreateDataStringWithURL: function (url, nameValuePairs)
	{
		/// <summary>Creates the data string that can be used to send to httphandler - will examine url parameters if present</summary>
		/// <param name="nameValuePairs">JSON objects consisting of name / value properties</param>

		//Validate and prep
		if (url == null) { return ""; }
		url = EDRV2.trim(url);
		var finalNameValuePairs = [];
		var finalURLWithParams = '';
		if (nameValuePairs == null) { nameValuePairs = []; }

		//Parse URL and see if we need to add the items to the nameValuePairs array
		var queryString = url.split("?");
		var params = [];
		if (queryString.length == 2) { params = queryString[1].split("&"); }
		var param = [];
		var paramToAdd = null;
		var itemPresent = false;
		for (var i = 0; i < params.length; i++)
		{
			//If it is not already in the nameValuePair listing then add it
			param = params[i].split("=");
			if (param.length == 2)
			{
				paramToAdd = ({ name: param[0], value: param[1] });
				itemPresent = false;
				for (var j = 0; j < nameValuePairs.length; j++)
				{
					if (paramToAdd.name == nameValuePairs[j].name)
					{
						//Item present in the nameValuePairs so we can just exit
						itemPresent = true;
						break;
					}
				}
				if (!itemPresent) { finalNameValuePairs.push(paramToAdd); } //Not in there, so we need to add it to our url array						
			}
		}

		//Now build the final url with the parameters (specified nameValuePairs will override current url params if both are present
		for (var i = 0; i < nameValuePairs.length; i++)
		{
			finalNameValuePairs.push(nameValuePairs[i]);
		}

		//Build the param string
		var paramString = EDRV2.HTTP.createDataString(finalNameValuePairs);
		finalURLWithParams = queryString[0];
		if (paramString.length > 0) { finalURLWithParams += '?'; }
		finalURLWithParams += paramString;

		//Build and return the final url with params
		return finalURLWithParams;
	}

}
/****************************************************************************************************************************************************
EDR HTTP utilities.
****************************************************************************************************************************************************/

/****************************************************************************************************************************************************
EDR DOM utilities.
****************************************************************************************************************************************************/
EDR.DOM =
{
	/*
	GetElement()
    
	Returns DOM element if exists.
    
	elem      := DOM element or DOM element ID (string).
	*/
	GetElement: function (elem)
	{
		// nothing to do
		if (elem == null) return null;

		// check if elem is string - if so this is the ID
		var elemC = null;
		if (typeof (elem) == 'string')
			elemC = document.getElementById(elem);
		else
			elemC = elem;

		return elemC;
	},

	/*
	GetWindowSize()
    
	Returns window height and width.
	*/
	GetWindowSize: function ()
	{
		var width = null;
		var height = null;
		var browserType = null;

		if ((typeof (window.innerWidth) == 'number') || (typeof (window.innerHeight) == 'number'))
		{
			// new browsers
			browserType = 'NewBrowser';
			width = window.innerWidth;
			height = window.innerHeight;
		}
		else if ((document.documentElement) && (document.documentElement.clientWidth || document.documentElement.clientHeight))
		{
			// ie 6
			browserType = 'IE 6';
			width = document.documentElement.clientWidth;
			height = document.documentElement.clientHeight;
		}
		else if ((document.body) && (document.body.clientWidth || document.body.clientHeight))
		{
			browserType = 'IE Old';
			width = document.body.clientWidth;
			height = document.body.clientHeight;
		}

		return { WindowHeight: height, WindowWidth: width, BrowserType: browserType };
	},

	/*
	GetWindowTotalSize()
    
	Returns window height and width.
	*/
	GetWindowTotalSize: function ()
	{
		var width = null;
		var height = null;
		var browserType = null;

		if ((typeof (window.innerWidth) == 'number') || (typeof (window.innerHeight) == 'number'))
		{
			// new browsers
			browserType = 'NewBrowser';
			width = window.innerWidth + window.scrollMaxX;
			height = window.innerHeight + window.scrollMaxY;
		}
		else if (document.body.scrollWidth && document.body.scrollHeight)
		{
			// all but Explorer Mac         
			browserType = 'IE';
			height = document.body.scrollHeight;
			width = document.body.scrollWidth;
		}
		else if (document.body.offsetHeight && document.body.offsetWidth)
		{
			// works in Explorer 6 Strict, Mozilla (not FF) and Safari         
			browserType = 'Offset Values';
			height = document.body.offsetHeight;
			width = document.body.offsetWidth;
		}
		else if ((document.documentElement) && (document.documentElement.clientWidth || document.documentElement.clientHeight))
		{
			// ie 6
			browserType = 'IE 6';
			width = document.documentElement.clientWidth;
			height = document.documentElement.clientHeight;
		}
		else if ((document.body) && (document.body.clientWidth || document.body.clientHeight))
		{
			browserType = 'IE Old';
			width = document.body.clientWidth;
			height = document.body.clientHeight;
		}

		return { WindowHeight: height, WindowWidth: width, BrowserType: browserType };
	},

	/*
	GetScrollOffset()		
	Gets the offest dependent on browser
		
	Returns: {ScrollX: n, ScrollY: n}
	*/
	GetScrollOffset: function ()
	{
		var y = null;
		var x = null;

		if (self.pageYOffset) // all except Explorer   
		{
			y = self.pageYOffset;
			x = self.pageXOffset;
		}
		else if (document.documentElement && document.documentElement.scrollTop)
		// Explorer 6 Strict   
		{
			y = document.documentElement.scrollTop;
			x = document.documentElement.scrollLeft;
		}
		else if (document.body) // all other Explorers   
		{
			y = document.body.scrollTop;
			x = document.body.scrollLeft;
		}
		return { ScrollX: x, ScrollY: y };
	},

	/*
	DisplayDivBrowserCenter()
    
	Calculate to show a DIV on the center of the screen.

	elem                  := DOM element or ID.
	width                 := width of the DIV (if null elem.offsetWidth will be used).
	height                := height of the DIV (if null elem.offsetHeight will be used).
	closeOnDocumentClick  := boolean: true - closes this div if document is click on, false - does not close.
	options	:= JS object 
	.UseDisplayCSS	:= True - use display css attribute to handle show/hide element.
	.OffsetTop		:= Offset the calculated TOP value w/ this value.
	.OffsetLeft		:= Offset the calculated LEFT value w/ this value.
	.OffsetHeight	:= Add this value to the div height before calculating TOP.
	.OffsetWidth	:= Add this value to the div width before calculating LEFT.

	*/
	DisplayDivBrowserCenter: function (elem, width, height, closeOnDocumentClick, options)
	{
		var top = null;
		var left = null;

		if ((options == null) || (typeof (options) == 'undefined')) options = new Object();
		if (typeof (options.UseDisplayCSS) == 'undefined') options.UseDisplayCSS = false; // by default use visibility to support backward compatibility
		if (typeof (options.OffsetTop) == 'undefined') options.OffsetTop = 0;
		if (typeof (options.OffsetLeft) == 'undefined') options.OffsetLeft = 0;
		if (typeof (options.OffsetHeight) == 'undefined') options.OffsetHeight = 0;
		if (typeof (options.OffsetWidth) == 'undefined') options.OffsetWidth = 0;

		// nothing to do
		if (elem == null) return false;

		// check if elem is string - if so this is the ID
		var elemC = EDR.DOM.GetElement(elem);
		if (elemC == null) return false;

		// get the scroll offset - contains the offset of the page after it is scrolled.
		var scroll = EDR.DOM.GetScrollOffset();
		var winSize = EDR.DOM.GetWindowSize();

		// determine the width and height
		if ((typeof (width) == 'undefined') || (width == null)) width = elemC.offsetWidth + options.OffsetWidth;
		if ((typeof (height) == 'undefined') || (height == null)) height = elemC.offsetHeight + options.OffsetHeight;

		if (width != null)
		{
			// calculate left based on inner width of the window as the client area
			if (width <= winSize.WindowWidth) left = Math.floor(((winSize.WindowWidth - width) / 2));

			left += options.OffsetLeft + scroll.ScrollX;
			left += 'px';
		}

		if (height != null)
		{
			// calculate top based on inner height of the window as the client area
			if (height <= winSize.WindowHeight) top = Math.floor(((winSize.WindowHeight - height) / 2));

			top += options.OffsetTop + scroll.ScrollY;
			top += 'px';
		}

		// delegate the logic
		//alert('width: ' + width + ' height: ' + height);
		//alert('top: ' + top + ' left: ' + left);
		EDR.DOM.DisplayEDRDOMDiv(elemC, top, left, closeOnDocumentClick, options);
	},

	/*
	DisplayEDRDOMDiv()
    
	Display a DIV at the specified location. This function adds the functionality to
	close the DIV if area other than the DIV is clicked on. If requested to do so,
	it assumes the DIV has been set to stop event bubbling if it is clicked on 
	(onclick="EDR.DOM.EventUtil.StopPropagation(e);").
    
	elem                  := DOM element or ID.
	top                   := top coordinate (elem.style.top).
	left                  := left coordinate (elem.style.left).
	closeOnDocumentClick  := boolean: true - closes this div if document is click on, false - does not close.
	options	:= JS object 
	.UseDisplayCSS	:= True - use display css attribute to handle show/hide element.

	Note:
	top/left: 
	- must include CSS unit measurements (px, pt, in, etc)
	- NULL will not set the property
        
	closeOnDocumentClick:
	- default value is TRUE.
	*/
	DisplayEDRDOMDiv: function (elem, top, left, closeOnDocumentClick, options)
	{
		// nothing to do
		if (elem == null) return false;

		if ((options == null) || (typeof (options) == 'undefined')) options = new Object();
		if (typeof (options.UseDisplayCSS) == 'undefined') options.UseDisplayCSS = false;

		// check if elem is string - if so this is the ID
		var elemC = EDR.DOM.GetElement(elem);
		if (elemC == null) return false;

		// set location
		if (top != null) elemC.style.top = top;
		if (left != null) elemC.style.left = left;

		// default to true
		if (typeof (closeOnDocumentClick) == 'undefined') closeOnDocumentClick = true;
		if (closeOnDocumentClick == null) closeOnDocumentClick = true;

		// clear previous call to this
		if (window.EDRDOMShowDivEvent || window.EDRDOMShowDivID)
		{
			EDR.DOM.HideEDRDOMDiv();
		}

		// trap document click to close this div
		if (closeOnDocumentClick)
		{
			var evt = EDR.DOM.EventUtil.AddEventHandler(document, "click", function () { EDR.DOM.HideEDRDOMDiv(); }, false);
			window.EDRDOMShowDivOptions = options;
			window.EDRDOMShowDivEvent = evt;
			window.EDRDOMShowDivID = elemC;
		}

		// show DIV
		if (options.UseDisplayCSS)
			EDR.DOM.ShowHide(elemC, true, null);
		else
			EDR.DOM.ShowHideByVisibility(elemC, true, null);

		return true;
	},

	/*
	HideEDRDOMDiv()
    
	Function used internally as a counterpart of DisplayDiv(). This function
	closes DIV that is current specified as window.EDRDOMShowDivID and also
	detach event specified in window.EDRDOMShowDivEvent
	*/
	HideEDRDOMDiv: function ()
	{
		// detach event first
		if (window.EDRDOMShowDivEvent)
		{
			with (window.EDRDOMShowDivEvent)
			{
				EDR.DOM.EventUtil.RemoveEventHandler(DOMElement, EventName, Handler, UseCapturePhase);
			}

			window.EDRDOMShowDivEvent = null;
		}

		// get options
		var options = null;
		if (typeof (window.EDRDOMShowDivOptions) != 'undefined')
			options = window.EDRDOMShowDivOptions;
		else
			options = new Object();

		if (typeof (options.UseDisplayCSS) == 'undefined') options.UseDisplayCSS = false;

		// hide div
		if (options.UseDisplayCSS)
			EDR.DOM.ShowHide(window.EDRDOMShowDivID, false, null);
		else
			EDR.DOM.ShowHideByVisibility(window.EDRDOMShowDivID, false, null);

		window.EDRDOMShowDivID = null;

	},

	/*
	ShowHide()
		
	Show/hide DOM element.
  
	elem              := DOM element or DOM element ID.
	showIt            := True - show element, False - hide element, null - toggle from current state.
	displayCSSValue   := CSS display value to use -default to "block" (if null).
	*/
	ShowHide: function (elem, showIt, displayCSSValue)
	{
		// nothing to do
		if (elem == null) return null;

		// check if elem is string - if so this is the ID
		var elemC = EDR.DOM.GetElement(elem);
		if (elemC == null) return null;

		// CSS display attribute has multiple values - default to block if none specified.
		if (displayCSSValue == null) displayCSSValue = 'block';

		if (showIt == null)
		{
			//get current value - 'none' is the only value to hide
			showIt = !EDR.DOM.IsElementDisplayed(elemC);
		}

		if (showIt)
		{
			elemC.style.display = displayCSSValue;
		}
		else
			elemC.style.display = 'none';

		return showIt;
	},

	/*
	ShowHideByVisibility()
		
	Show/hide DOM element.
  
	elem                := DOM element or DOM element ID.
	showIt              := True - show element, False - hide element, null - toggle from current state.
	visibilityCSSValue  := CSS visiblity value to use -default to "visible" (if null).
	*/
	ShowHideByVisibility: function (elem, showIt, visibilityCSSValue)
	{
		// nothing to do
		if (elem == null) return null;

		// check if elem is string - if so this is the ID
		var elemC = EDR.DOM.GetElement(elem);
		if (elemC == null) return null;

		// CSS display attribute has multiple values - default to block if none specified.
		if (visibilityCSSValue == null) visibilityCSSValue = 'visible';

		if (showIt == null)
		{
			//get current value - 'none' is the only value to hide
			showIt = !EDR.DOM.IsElementDisplayedByVisibility(elemC);
		}

		if (showIt)
			elemC.style.visibility = visibilityCSSValue;
		else
			elemC.style.visibility = 'hidden';

		return showIt;
	},

	/*
	Fade()
	  
	Used to make an HTML DIV element slowly appear for that fade in effect.
	  
	startPoint			:= the starting level of opacity, in increments of 10 with a range of 0-100.
	endPoint				:= the ending level of opacity, in increments of 10 with a range of 0-100.
	divID             	:= DOM element or ID of DIV tag.
	fadePeriod	:= How long in seconds to wait between iteration.
	*/
	Fade: function (startPoint, endPoint, divID, fadePeriod)
	{
		var obj = document.getElementById(divID);

		if (obj == null)
		{
			alert('OpacityIn(): Unable to find \'' + divID + '\' element.');
			return;
		}

		var timerPeriod = 1
		if (typeof (fadePeriod) != 'undefined') timerPeriod = fadePeriod;

		if (startPoint < endPoint)
		{
			obj.style.filter = "alpha(opacity=" + (startPoint + 10) + ")"; //IE
			obj.style.MozOpacity = (startPoint + 10) / 100; //Firefox

			if (startPoint != (endPoint - 10)) setTimeout("EDR.DOM.Fade(" + (startPoint + 10) + "," + endPoint + ",'" + divID + "')", timerPeriod);
		}
		else if (startPoint > endPoint)
		{
			obj.style.filter = "alpha(opacity=" + (endPoint - 10) + ")"; //IE
			obj.style.MozOpacity = (endPoint - 10) / 100; //Firefox

			if (endPoint != (startPoint + 10)) setTimeout("EDR.DOM.Fade(" + (startPoint - 10) + "," + endPoint + ",'" + divID + "')", timerPeriod);
		}
	},

	/*
	IsElementDisplayed()
    
	Returns whether element is currently displayed or not based on DISPLAY css attribute.
	*/
	IsElementDisplayed: function (elem)
	{
		// nothing to do
		if (elem == null) return false;

		// check if elem is string - if so this is the ID
		var elemC = EDR.DOM.GetElement(elem);
		if (elemC == null) return null;

		//get current value - 'none' is the only value to hide
		if (elemC.style.display == 'none')
			return false;
		else
			return true;
	},

	/*
	IsElementDisplayedByVisibility()
    
	Returns whether element is currently displayed or not based on VISIBILITY css attribute.
	*/
	IsElementDisplayedByVisibility: function (elem)
	{
		// nothing to do
		if (elem == null) return false;

		// check if elem is string - if so this is the ID
		var elemC = EDR.DOM.GetElement(elem);
		if (elemC == null) return null;

		//get current value - 'none' is the only value to hide
		if (elemC.style.visibility == 'hidden')
			return false;
		else
			return true;
	},

	/*
	Move()
		
	Moves element (top = y, left = x).
	*/
	Move: function (elem, top, left)
	{
		// nothing to do
		if (elem == null) return true;

		if (top != null) elem.style.top = top;
		if (left != null) elem.style.left = left;

		return true;
	},

	/*
	CreateSelectOption()
		
	Creates option element (for dropdownlist).
		
	selectCtrl					: = SELECT DOM element (if specified item will be added into the control).
	posReference				:= if specified becomes the point of reference where to add the new option to. Otherwise, new option will be added to the end of the list.
	(note: this can be the index or the option element itself)
	insertBefore				:= True, insert new option before the posReference, False, to insert after.
	text							:= option text
	value							:= option value (if null, text will be used).
	*/
	AddSelectOption: function (selectCtrl, posReference, insertBefore, text, value)
	{
		var newOption = document.createElement('option');
		newOption.text = text;
		newOption.value = value;

		if (selectCtrl != null)
		{
			// implement posReference later.

			try
			{
				// most browser
				selectCtrl.add(newOption, null);
			}
			catch (ex)
			{
				// IE
				selectCtrl.add(newOption);
			}
		}

		return newOption;
	},

	/*
	ApplyStyle()
		
	Applies CSS style to an element.
		
	elem: HTML elemenet.
	cssStyle: CSS style string formart (ie: text that you would put in style attribute of html tag).
	*/
	ApplyStyle: function (elem, cssStyle)
	{
		//document.getElementById('_DebugText').value = cssStyle; //EDR.DisplayObjectProperties(elem, false);
		// validate
		if (elem == null) return false;

		elem = EDR.DOM.GetElement(elem);

		if (!elem.style) return false;
		if (cssStyle == null) return false;

		// trim
		cssStyle = EDR.Trim(cssStyle);
		if (cssStyle == '') return false;

		// split style by ;
		var tokens = cssStyle.split(';');
		var token = '';
		var style = null;

		for (i = 0; i < tokens.length; i++)
		{
			// trim
			token = EDR.Trim(tokens[i]);
			if (token != '')
			{
				// split by :
				style = token.split(':');

				// expecting 2 tokens
				if (style.length == 2)
				{
					// element 0 is the stylename - lowercase for later use
					style[0] = EDR.Trim(style[0]).toLowerCase();
					style[1] = EDR.Trim(style[1]);

					// convert stylename to the property name
					// all properties starts w/ lowecase
					// multi-words property name is camel case, multi-words string stylename is separated by -
					// so run regexp that capatilize the first char after - and remove the - itself (thus, we convert string stylename to propertyname)
					style[0] = style[0].replace(/(\-[a-zA-Z])/gi, function (m) { return m.charAt(1).toUpperCase(); });

					// set tyle
					elem.style[style[0]] = style[1];
				}
			}
		}

		return true;
	},

	/*
	EDR.DOM.GetStyle()
		
	Get the CSS style from an element.
		
	elem: HTML elemenet.
	cssStyle: CSS style string formart (ie: text that you would put in style attribute of html tag).
	*/
	GetStyle: function (elem, cssStyle)
	{
		//document.getElementById('_DebugText').value = cssStyle; //EDR.DisplayObjectProperties(elem, false);
		// validate
		if (elem == null) return null;

		elem = EDR.DOM.GetElement(elem);

		if (!elem.style) return null;
		if (cssStyle == null) return null;

		// trim
		cssStyle = EDR.Trim(cssStyle);
		if (cssStyle == '') return null;

		// convert stylename to the property name
		// all properties starts w/ lowecase
		// multi-words property name is camel case, multi-words string stylename is separated by -
		// so run regexp that capatilize the first char after - and remove the - itself (thus, we convert string stylename to propertyname)
		cssStyle = cssStyle.replace(/(\-[a-zA-Z])/gi, function (m) { return m.charAt(1).toUpperCase(); });

		// return
		if (elem.style[cssStyle] != undefined)
		{
			return elem.style[cssStyle];
		} else
		{
			return null; // if style doesn't exist, return null
		}

	},

	/*
	GetTextboxValue(): get the value of textbox
	elem             := DOM element or DOM element ID.
	*/
	GetTextboxValue: function (elem)
	{

		// nothing to do
		if (elem == null) return null;

		// check if elem is string - if so this is the ID
		var elemC = null;
		if (typeof (elem) == 'string')
			elemC = document.getElementById(elem);
		else
			elemC = elem;

		if (elemC == null) return null;

		return elemC.value;
	},

	/*
	SetTextboxValue(): set the value of the textbox
  
	elem             := DOM textbox element or DOM textbox element ID.
	value            := The value that will be put into the textbox
	*/
	SetTextboxValue: function (elem, value)
	{
		// nothing to do
		if (elem == null) return null;

		// check if elem is string - if so this is the ID
		var elemC = null;
		if (typeof (elem) == 'string')
			elemC = document.getElementById(elem);
		else
			elemC = elem;

		if (elemC == null) return null;

		// set the textbox value    
		elemC.value = value;

		return value;
	}

}

/*
Provides cross browser functionalities.
*/
EDR.DOM.EventUtil =
{
	/*
	GetEvent()
		
	Returns the event object.
	*/
	GetEvent: function (event)
	{
		return event ? event : window.event;
	},

	/*
	GetEventTarget()
		
	Returns the element that triggered the event.
	*/
	GetEventTarget: function (event)
	{
		var evt = EDR.DOM.EventUtil.GetEvent(event);
		if (evt == null) return null;

		return evt.target || evt.srcElement;
	},

	/*
	GetSourceTarget()
		
	Returns the element that trapped the event.
	
	elem := In IE, event.currentTarget is not defined, so use this object instead
	*/
	GetSourceTarget: function (event, elem)
	{
		var evt = EDR.DOM.EventUtil.GetEvent(event);
		if (evt == null) return null;

		return evt.currentTarget || elem;
	},

	/*
	AddEventHandler()
		
	Adds event handler.
		
	elem					:= DOM element.
	eventName			:= Name of the event to handle.
	eventHandler		:= Event handler.
	useCapturePhase	:= Use capture phase instead of capture phase (if supported).
		
	This function returns an defined object as follows:
	{
	DOMElement: elem,
	EventName: eventName,
	Handler: eventHandler,
	UseCapturePhase: useCapturePhase
	}
		
	*/
	AddEventHandler: function (elem, eventName, eventHandler, useCapturePhase)
	{
		// validate
		if (elem == null) return null;
		if (EDR.Trim(eventName) == '') return null;
		if (eventHandler == null) return null;

		// default to bubble phase
		useCapturePhase = useCapturePhase ? useCapturePhase : false;

		try
		{
			if (elem.addEventListener)
			{
				elem.addEventListener(eventName, eventHandler, useCapturePhase);
			}
			else if (elem.attachEvent)
			{
				elem.attachEvent('on' + eventName, eventHandler);
			}
			else
			{
				// just assign it as property
				elem['on' + eventName] = eventHandler;
			}

			return { DOMElement: elem, EventName: eventName, Handler: eventHandler, UseCapturePhase: useCapturePhase };
		}
		catch (e)
		{
			return null;
		}
	},

	/*
	AddEventHandlerV2()
		
	Adds event handler. For IE
		
	elem					:= DOM element.
	eventName			:= Name of the event to handle.
	eventHandler		:= Event handler.
	useCapturePhase	:= Use capture phase instead of capture phase (if supported).
		
	This function returns an defined object as follows:
	{
	DOMElement: elem,
	EventName: eventName,
	Handler: eventHandler,
	UseCapturePhase: useCapturePhase
	}
		
	*/
	AddEventHandlerV2: function (elem, eventName, eventHandler, useCapturePhase)
	{
		// validate
		if (elem == null) return null;
		if (EDR.Trim(eventName) == '') return null;
		if (eventHandler == null) return null;

		// default to bubble phase
		useCapturePhase = useCapturePhase ? useCapturePhase : false;

		// if this is IE - create a closure to set the currentTarget property
		var evt = null;
		if (window.event)
			evt = EDR.BindFunction(eventHandler, elem);
		else
			evt = eventHandler;


		try
		{
			if (elem.addEventListener)
			{
				elem.addEventListener(eventName, evt, useCapturePhase);
			}
			else if (elem.attachEvent)
			{
				elem.attachEvent('on' + eventName, evt);
			}
			else
			{
				// just assign it as property
				elem['on' + eventName] = evt;
			}

			return { DOMElement: elem, EventName: eventName, Handler: evt, UseCapturePhase: useCapturePhase };
		}
		catch (e)
		{
			return null;
		}
	},

	/*
	RemoveEventHandler()
		
	Removes event handler.
		
	elem					:= DOM element.
	eventName			:= Name of the event to handle.
	eventHandler		:= Event handler.
	useCapturePhase	:= Use capture phase instead of capture phase (if supported).
	*/
	RemoveEventHandler: function (elem, eventName, eventHandler, useCapturePhase)
	{
		// validate
		if (elem == null) return false;
		if (EDR.Trim(eventName) == '') return false;

		// default to bubble phase
		useCapturePhase = useCapturePhase ? useCapturePhase : false;

		try
		{
			if (elem.removeEventListener)
			{
				elem.removeEventListener(eventName, handler, useCapturePhase);
			}
			else if (elem.detachEvent)
			{
				elem.detachEvent('on' + eventName, eventHandler);
			}
			else
			{
				// just assign it as property
				elem['on' + eventName] = null;
			}

			return true;
		}
		catch (e)
		{
			return false;
		}
	},

	/*
	StopPropagation()
		
	Stops event propagation.
	*/
	StopPropagation: function (event)
	{
		var evt = EDR.DOM.EventUtil.GetEvent(event);

		if (evt.stopPropagation)
			evt.stopPropagation();
		else
			evt.cancelBubble = true;
	},

	/*
	PreventDefault()
		
	Prevent default event.
	*/
	PreventDefault: function (event)
	{
		var evt = EDR.DOM.EventUtil.GetEvent(event);

		if (evt.preventDefault)
			evt.preventDefault();
		else
			evt.returnValue = false;
	},

	/*
	BindHandler
		
	Binds a handler to run under a specific context. Note this bind using "function currying" to allow parameters to be passed into the
	handler when the callback happens.
		
	fn					: Function pointer.
	context			: Context to execute function in.
	*/
	BindHandler: function (fn, context)
	{
		if (fn == null) return null;
		return EDR.BindFunction(fn, context);
	}
}

/***********************************************
START: EDR.ObjectBase
************************************************/
EDR.ObjectBase = function ()
{
	/// <summary>EDR object base class.</summary>
	if (this instanceof EDR.ObjectBase)
	{
	}
	else
		return new EDR.ObjectBase();
};

// prototype declaration
EDR.ObjectBase.prototype.constructor = EDR.ObjectBase;
EDR.ObjectBase.prototype.base = null; // set by derived class

// properties
EDR.ObjectBase.prototype.isUsable = true;
EDR.ObjectBase.prototype.initializationErrorMessage = '';

// methods
EDR.ObjectBase.prototype.displayMessage = function (msg)
{
	alert(msg);
};
/***********************************************
END: EDR.ObjectBase
************************************************/

/***********************************************
START: EDR.Size
************************************************/
EDR.Size = {};

EDR.Size = function (width, height)
{
	/// <summary>Creates new instance of EDR.Size object.</summary>
	/// <param name="width" type="float">Width of the size.</param>
	/// <param name="height" type="float">Height of the size.</param>
	if (this instanceof EDR.Size)
	{
		this.Width = parseFloat(width);
		this.Height = parseFloat(height);
	}
	else
	{
		return new EDR.Size(width, height);
	}
};

// constructor
EDR.Size.prototype.constructor = EDR.Size;

// properties
EDR.Size.prototype.Width = 0.0;
EDR.Size.prototype.Height = 0.0;

EDR.Size.prototype.toString = function ()
{
	/// <summary>Returns string representation of this instance.</summary>
	return 'Size: width=' + this.Width + ' height=' + this.Height;
};

/***********************************************
END: EDR.Size
************************************************/

/***********************************************
START: EDR.Point
************************************************/
EDR.Point = {};

EDR.Point = function (x, y)
{
	/// <summary>Creates new instance of EDR.Size object.</summary>
	/// <param name="x" type="float">X coordinate of the value.</param>
	/// <param name="y" type="float">Y coordinate of the value.</param>
	if (this instanceof EDR.Point)
	{
		this.X = parseFloat(x);
		this.Y = parseFloat(y)
	}
	else
	{
		return new EDR.Point(x, y);
	}
};

// constructor
EDR.Point.prototype.constructor = EDR.Point;

// properties
EDR.Point.prototype.X = 0.0;
EDR.Point.prototype.Y = 0.0;

EDR.Point.prototype.toString = function ()
{
	/// <summary>Returns string representation of this instance.</summary>
	return 'Point: x=' + this.Width + ' y=' + this.Height;
};

/***********************************************
END: EDR.Point
************************************************/

/***********************************************
START: EDR.ImageInformation
************************************************/
EDR.ImageInformation = {};

EDR.ImageInformation = function (imageInfo)
{
	/// <summary>Creates new instance of EDR.ImageInformation object.</summary>
	/// <param name="imageInfo" type="EDR.ImageInformation">Image information to copy from.</param>
	if (this instanceof EDR.ImageInformation)
	{
		if (imageInfo != null) EDR.CopyObjectData(imageInfo, this);
	}
	else
		return new EDR.ImageInformation(imageInfo);
};

// constructor
EDR.ImageInformation.prototype.constructor = EDR.ImageInformation;

// properties
EDR.ImageInformation.prototype.ImageURL = '';
EDR.ImageInformation.prototype.PrintImageURL = '';
EDR.ImageInformation.prototype.MozPrintImageURL = '';
EDR.ImageInformation.prototype.ShadowImageURL = '';
EDR.ImageInformation.prototype.PrintShadowImageURL = '';
EDR.ImageInformation.prototype.Size = null; 									// EDR.Size object containing the image size
EDR.ImageInformation.prototype.ShadowSize = null; 						// EDR.Size object containing the shadow image size (used by Mapping JS such as Google API)
EDR.ImageInformation.prototype.AnchorPoint = null; 						// EDR.Point object containing image anchor point (used by Mapping JS such as Google API)
EDR.ImageInformation.prototype.InfoWindowAnchorPoint = null; 	// EDR.Point object containing info window anchor point (used by Mapping JS such as Google API)

EDR.ImageInformation.prototype.toString = function ()
{
	/// <summary>Returns string representation of this instance.</summary>
	var ret = 'Image: ' + this.ImageURL;
	if (this.Size != null) ret += '[W:' + this.Size.Width + '/H:' + this.Size.Height + ']';

	return ret;
};

/***********************************************
END: EDR.ImageInformation
************************************************/

/***********************************************
Objects overrides.
************************************************/

/*
Adds trim() to String
*/
String.prototype.trim = function ()
{
	return EDR.Trim(this);
}

/*
Adds selectSingleNode() selectNodes() to XML Element to nonIE browsers.
*/
if (window.ActiveXObject == null)
{
	/*
	selectSingleNode()
    
	Returns the first node matches the xPath
	*/
	Element.prototype.selectSingleNode = function (xPath)
	{
		// create XPathEvaluator()
		var xPathEval = EDR.XML.CreateXPathEvaluator();
		if (xPathEval == null)
		{
			// unable to get XPathEvaluator object - so overwrite function to always return error.
			alert('SelectSingleNode(): Browser does not support XPath.');
			return null;
		}
		else
		{
			// managed to get an evaluator - so overwrite function to use the evaluator
			var retNode = null;

			// use XPathEvaluator to select by XPath
			var xPathRes = xPathEval.evaluate(xPath, this, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
			if (xPathRes != null) retNode = xPathRes.singleNodeValue;

			return retNode;
		}
	}

	/*
	selectNodes()
    
	Returns all nodes matching XPath.
	*/
	Element.prototype.selectNodes = function (xPath)
	{
		// create XPathEvaluator()
		var xPathEval = EDR.XML.CreateXPathEvaluator();
		if (xPathEval == null)
		{
			// unable to get XPathEvaluator object - so overwrite function to always return error.
			alert('selectNodes(): Browser does not support XPath evaluator.');
			return null;
		}
		else
		{
			// managed to get an evaluator - so overwrite function to use the evaluator
			var retNodes = [];

			// use XPathEvaluator to select by XPath
			var xPathRes = xPathEval.evaluate(xPath, this, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
			if (xPathRes != null)
			{
				var curElem = xPathRes.iterateNext();
				while (curElem != null)
				{
					retNodes.push(curElem);
					curElem = xPathRes.iterateNext();
				}
			}

			return retNodes;
		}
	}
}

/***********************************************
Objects overrides.
************************************************/

/***********************************************
Browser detection object.

Note: Copied from: http://www.quirksmode.org/js/detect.html
************************************************/
var BrowserDetect = {
	init: function ()
	{
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data)
	{
		for (var i = 0; i < data.length; i++)
		{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString)
			{
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString)
	{
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index + this.versionSearchString.length + 1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ string: navigator.userAgent,
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
			identity: "Opera"
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

BrowserDetect.init();
/***********************************************
Browser detection object.
************************************************/

// other namespaces
EDR.CONTROLS = {};