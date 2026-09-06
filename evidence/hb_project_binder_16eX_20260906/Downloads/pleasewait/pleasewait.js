/*
    Name: PleaseWait.js
    Desc: Contains a JavaScript class to show or hide PleaseWait message box.
    Note: This JS library requires that EDRLibrary (EDR namespace definition) be included in the host page before this reference.
    Created: 05-13-2011
*/

// Namespace declarations
EDR.CONTROLS.PleaseWait = {};
EDR.CONTROLS.PleaseWait = function (mainContainerDivID, textDivID, position)
{
	/// <summary>Creates new instance of EDR.CONTROLS.PleaseWait object.</summary>
	/// <param name="mainContainerDivID" type="string">DIV ID of the main container (used to hide or show control).</param>
	/// <param name="textDivID" type="string">DIV ID of the text container (used to display custom please wait text).</param>
	/// <param name="position" type="JSON">JSON { left: 0.0, top: 0.0, bottom: 0.0, right: 0.0 } - UNDEFINED or NULL values will be ignored.</param>
	if (this instanceof EDR.CONTROLS.PleaseWait)
	{
		// inheritance via constructor stealing
		EDR.ObjectBase.apply(this, arguments);
		this.base = EDR.ObjectBase.prototype;
		
		try
		{
			// validations
			if (typeof(mainContainerDivID) == 'undefined') throw new Error('Main container DIV ID is undefined.');
			if (mainContainerDivID == null) throw new Error('Main container DIV ID is NULL.');

			if (typeof (textDivID) == 'undefined') throw new Error('Text container DIV ID is undefined.');
			if (textDivID == null) throw new Error('Text container DIV ID is NULL.');

			var mainContDiv = document.getElementById(mainContainerDivID);
			if (mainContDiv == null) throw new Error('DIV \'' + mainContainerDivID + '\' does not exist.');

			var textDiv = document.getElementById(textDivID);
			if (textDiv == null) throw new Error('DIV \'' + textDivID + '\' does not exist.');
			
			// set position
			this.setPosition(position);

			// all set
			this.mainContainerDivID = mainContainerDivID;
			this.textDivID = textDivID;
		}
		catch (err)
		{
			this.isUsable = false;
			this.initializationErrorMessage = err.message;

			this.displayMessage('Unable to initialize PleaseWait control: ' + this.initializationErrorMessage);
		}
	}
	else
		return new EDR.CONTROLS.PleaseWait(mainContainerDivID, textDivID, position);
};

// inheritance
EDR.CONTROLS.PleaseWait.prototype = new EDR.ObjectBase();
EDR.CONTROLS.PleaseWait.prototype.constructor = EDR.CONTROLS.PleaseWait;

// properties 
EDR.CONTROLS.PleaseWait.prototype.mainContainerDivID = '';
EDR.CONTROLS.PleaseWait.prototype.textDivID = '';
EDR.CONTROLS.PleaseWait.prototype.containerPosition = { left: null, top: null, bottom: null, right: null };

// methods
EDR.CONTROLS.PleaseWait.prototype.setPosition = function (position)
{
	// set position
	if ((typeof(position) != 'undefined') && (position != null))
	{
		if ((typeof(position.left) != 'undefined') && (position.left != null)) this.containerPosition.left = position.left;
		if ((typeof(position.top) != 'undefined') && (position.top != null)) this.containerPosition.top = position.top;
		if ((typeof(position.bottom) != 'undefined') && (position.bottom != null)) this.containerPosition.bottom = position.bottom;
		if ((typeof(position.right) != 'undefined') && (position.right != null)) this.containerPosition.right = position.right;
	}
};

EDR.CONTROLS.PleaseWait.prototype.setMessage = function (msg)
{
	/// <summary>Sets message to be displayed.</summary>
	/// <param name="msg">Message to be displayed.</summary>
	
	// validation
	if (!this.isUsable) return false;

	var textElem = EDR.DOM.GetElement(this.textDivID);
	if (textElem != null)
	{
		msg = msg || 'Please wait ...';
		textElem.innerHTML = msg;
	}
};

EDR.CONTROLS.PleaseWait.prototype.show = function (msg, position, cb)
{
	// validation
	if (!this.isUsable) return false;

	// set message
	this.setMessage(msg);

	// use jQuery animation to show
	var elem = $("div#" + this.mainContainerDivID);
	if (elem != null)
	{
		// set position
		this.setPosition(position);

		if (this.containerPosition.left != null) elem.css('left', this.containerPosition.left);
		if (this.containerPosition.top != null) elem.css('top', this.containerPosition.top);
		if (this.containerPosition.bottom != null) elem.css('bottom', this.containerPosition.bottom);
		if (this.containerPosition.right != null) elem.css('right', this.containerPosition.right);

		elem.fadeIn(1000, cb); //Don't need to worry about the callback in this case						
	}

	//EDR.DOM.ShowHide(this.mainContainerDivID, true);
};

EDR.CONTROLS.PleaseWait.prototype.hide = function ()
{
	// validation
	if (!this.isUsable) return false;

	// use jQuery animation to hide
	var elem = $("div#" + this.mainContainerDivID);
	if (elem != null)
	{
		elem.fadeOut(1000, null); //Don't need to worry about the callback in this case
	}

	//EDR.DOM.ShowHide(this.mainContainerDivID, false);
};