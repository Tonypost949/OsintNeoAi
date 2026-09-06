/// <reference path="http://localhost/global/jscripts/edrlibrary.js" />

EDR.WEBGEOCODERPAGE = {};
EDR.WEBGEOCODERPAGE =
{
	pageContainerMargin: [10, 20, 10, 20], 	// page container margin [top, right, bottom, left]

	pageContainerHeight: 0,
	pageContainerWidth: 0,

	contentContainerHeight: 0,

	zoomParcelOnPageLoad: false, //global variable to reZoom if parcel is large if info window is visible on page load

	pageLoad: function ()
	{
		/// <summary>Handles pageLoad() event</summary>

		// trap resize event
		EDR.DOM.EventUtil.AddEventHandlerV2(window, 'resize', EDR.WEBGEOCODERPAGE.pageResize, false);

		// resize controls
		EDR.WEBGEOCODERPAGE.pageResize();

	    //set zoomParcelOnPageLoad variable to true
		EDR.WEBGEOCODERPAGE.zoomParcelOnPageLoad = true;

        //Slider for map opacity
	    try
	    {
	        $("#sldOpac").slider({
	            value: 100,
	            min: 0, max: 100, step: 1,
	            slide: function (event, ui)
	            {
	                $("#dvOpacity").html(ui.value);
	                var newOpacity = parseInt(ui.value);
	                EDR.EDRMapV2Google.adjustOverlayMapTypeOpacity('DMP_WMS_Layer', (newOpacity / 100));	                
	            }
	        });
	        $("#dvOpacity").html($("#sldOpac").slider("value"));            	       
	    }
	    catch (ex) { throw new Error('Opacity Slider error: ' + ex.message); }

		return true;
	},

	pageResize: function ()
	{
		/// <summary>Handles pageResize() event</summary>

		// get window size
		var winSize = EDR.DOM.GetWindowSize();

		// resize page container
		EDR.WEBGEOCODERPAGE.pageContainerWidth = winSize.WindowWidth - (EDR.WEBGEOCODERPAGE.pageContainerMargin[1] + EDR.WEBGEOCODERPAGE.pageContainerMargin[3]);
		EDR.WEBGEOCODERPAGE.pageContainerHeight = winSize.WindowHeight - (EDR.WEBGEOCODERPAGE.pageContainerMargin[0] + EDR.WEBGEOCODERPAGE.pageContainerMargin[2]);

		EDR.DOM.ApplyStyle('_WGPageContainer', 'width: ' + EDR.WEBGEOCODERPAGE.pageContainerWidth.toString() + 'px; height: ' + EDR.WEBGEOCODERPAGE.pageContainerHeight.toString() + 'px;');

		// resize content container (values are hardcoded because this is a fixed size document
		EDR.WEBGEOCODERPAGE.contentContainerHeight = EDR.WEBGEOCODERPAGE.pageContainerHeight - (43 + 20 + 11 + 20 + 20); // (heights: header + header info + content header + footer + copyright)

		EDR.DOM.ApplyStyle('_WGContentContainer', 'height: ' + EDR.WEBGEOCODERPAGE.contentContainerHeight.toString() + 'px;');

		// resize left column
		EDR.WEBGEOCODERPAGE.contentLeftColumnResize();

		return true;
	},

	contentLeftColumnResize: function ()
	{
		/// <summary>When overriden, resize the left column.</summary>
		return true;
	},

	pleaseWaitPosition: function ()
	{
		/// <summary>When overriden, return position for pleasewait window.</summary>
		return true;
	},
		
    getGISMapServerDMPParcelsURL: function ()
    {
        //return EDR.DOM.getElement('hfGISMapServerDMPParcels').value;
        return $("#hfGISMapServerDMPParcels")[0].value;
    }
};