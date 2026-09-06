/**
 * <pre>
 * 
 *  Accela
 *  File: AccelaTextBox.cs
 * 
 *  Accela, Inc.
 *  Copyright (C): 2007-2014
 * 
 *  Description:
 * 
 *  Notes:
 * $Id: Validation.js 79503 2007-11-08 07:04:56Z ACHIEVO\jackie.yu $.
 *  Revision History
 *  &lt;Date&gt;,    &lt;Who&gt;,    &lt;What&gt;
 *  05/14/2007     		lytton.cheng				Initial.
 * </pre>
 */

var text;
function checkLength(val)
{
    
	if (text == null) text = val.innerHTML;
	var value = ValidatorTrim(ValidatorGetValue(val.controltovalidate));
	if (value.trim().length == 0)
	{
	    return true;
	}

	var actualLength = 0;
	var controlToValidate = $get(val.controltovalidate);
    
    // need get the byte length of the inputted string 
    // since the maxLength of DB column(Varchar2) is 4000 bytes.
	if (val.maxLength > 1000 && controlToValidate != null && controlToValidate.type == 'textarea') 
    {
	    actualLength = getByteLength4String(value);
	}
	else 
	{
	    actualLength = value.length;
	}

	if (val.mask != "") 
    {
	    actualLength = getActualLength4Masked(value, val.mask);
	}
	//if type is AccelaPhoneText
	var phoneHiddenField = document.getElementById(val.controltovalidate + '_phoneMask');
	if(phoneHiddenField!=null){
	    if(phoneHiddenField.value.length>0){
	        var ret=phoneHiddenField.value.replace(/-/g,"").replace(/\s/g,"");
	        minLength=ret.length;
	        
	         var strValue=value.trim();
	         if (phoneHiddenField.value.indexOf("-") > -1) {
	             strValue = strValue.replace(/-/g, "");
	         }
	         if (phoneHiddenField.value.indexOf(" ") > -1) {
	             strValue = strValue.replace(/\s/g, "");
	         }
	        actualLength=strValue.length;
	    }
	}

	if (actualLength != 0 && (actualLength > val.maxLength || actualLength < val.minLength))
	{
		val.innerHTML = val.errorMessage;
		if (val.displayEntered.toLowerCase() == "true")
		{
			//val.innerHTML = "<br/><span class=\"form_sublabel\">"+val.errorMessage+"(" + value.length + " entered)</span>";
		}
		//alert("Error!!!");
		return false;
	}
    return true;
}

function cb_vefify(val) {
    //if current page is SPEAR page and user click the "save and resume later" button ,then the control does not need to validate
    if(typeof(CapEditPageNotValidateEmpetyValueControlFlag) != 'undefined' && CapEditPageNotValidateEmpetyValueControlFlag)
    {
        return true;
    }
//*****Orignal******
//    var value = val.controltovalidate;
//    if ( col != null ) {
//        for ( i = 0; i < col.length; i++ ) {
//            if (col.item(i).tagName == "INPUT") {
//                if ( col.item(i).checked ) {

//                    return true;
//                    }
//                }
//            }


//        return false;
//        }
//************************************
//Changed by daly radiobuttonlist doesn't work
    var value = val.controltovalidate;
   
    var rbltable = document.getElementById(value);
    if (rbltable.disabled) {
        if (rbltable.attributes["ValidateDisabledControl"] == null || rbltable.attributes["ValidateDisabledControl"] == 'undefined' || rbltable.attributes["ValidateDisabledControl"].nodeValue != 'Y') {
                return true;
        }
    }
    
    var rbs = rbltable.getElementsByTagName("INPUT");
    for(var i=0;i<rbs.length;i++)
    {
        if(rbs[i].checked)
        { 
           return true;
        }
    }
    
    return false;
}

function hideCbError(control)
{   
    var controlID = control.id;
    document.getElementById(controlID+'_err_indicator').style.display = "none";
    document.getElementById(controlID+'_label_0').className = "";
    document.getElementById(controlID+'_label_1').className = "";
    document.getElementById(controlID+'_label_2').className = "";
	    
	    
    document.getElementById(controlID+'_label_2').innerHTML = "";
}

function filter(control,isNeedDot,isNeedNegative,evt)
{
    evt = evt ? evt : window.event;
    var charCode = evt.keyCode ? evt.keyCode : evt.which;
    var currentChar = String.fromCharCode(charCode);

    //check if current char is valid decimal separator.
    var validChars = control.attributes["validChars"].value;
    var isInValidChars = validChars == null ? true : validChars.indexOf(currentChar) != -1;
    var regex = new RegExp("[" + validChars + "]+", "g");
    var _text = GetValue(control);
    var existsValidChar = regex.test(_text);
    var isInvalidDecimalSeparator = isNeedDot && isInValidChars && existsValidChar;

    //check if current char is valid negative sign.
    var isInvalidNegativeSign = isNeedNegative && _text.indexOf(GLOBAL_NEGATIVE_SIGN) != -1 && currentChar == GLOBAL_NEGATIVE_SIGN;

    //cancel invalid char.
    if (isInvalidDecimalSeparator || isInvalidNegativeSign) {
        if (window.event) {
            evt.returnValue = false;
        }
        else {
            evt.preventDefault();
        }

        return false;
    }
    
    return true;
}

function tb_verify(control)
{
    var textbox_req = document.getElementById(control.id);
    var textbox = document.getElementById(textbox_req.controltovalidate);
    var _text = GetValue(textbox);
    var controlID = control.id;
    
    if(_text.length==0) return false;;
    
    if(_text.substr(_text.length-1,1)==".")
    {
        return false;
    }
    
    return true;
        
}

function checkZipCode(val)
{
    var zipHiddenField = document.getElementById(val.controltovalidate + '_ZipFromAA');
    var maskHiddenField = document.getElementById(val.controltovalidate + '_zipMask');
    if(zipHiddenField != null && zipHiddenField.value != '0')//not need to check
    {
        return true;
    }
    
    var value = ValidatorTrim(ValidatorGetValue(val.controltovalidate));
    var controlID = val.controlID;
    
    value = value.trim();
    
    //alert(document.getElementById(controlID).value);
    //alert("index:"+value.indexOf("-"));
    if (value.indexOf("-") == value.trim().length -1 )
    {
        value = value.substring(0, value.length-1).trim();
    }
    
    if (value.length == 0)
    {
        SetValueById(controlID,"");
        return true;
    }
    
    SetValueById(controlID,value);
    
    return validateZip(value,controlID,maskHiddenField);

}

function validateZip(value)
{
    var valid = "0123456789-";
    var hyphencount = 0;
    //    if (value.length!=5 && value.length!=10) {
    //        return false;
    //    }
    var iIndex=0;
    var maskCtrl=null;
    var maskLen=0;
    if(arguments.length==3){
        maskCtrl=arguments[2];
        if (maskCtrl == null) {
            return false;
        }
        maskLen=maskCtrl.value.length;
        iIndex=maskCtrl.value.indexOf("-");
        if(iIndex!=-1){
            if(value.length!=iIndex && value.length!=maskLen){
                return false;
            }
        }
    }
    for (var i=0; i < value.length; i++) {
        temp = "" + value.substring(i, i+1);

        if (temp == "-") {
            hyphencount++;
        }

        if (valid.indexOf(temp) == "-1") {
            //alert("Invalid characters in your zip code.  Please try again.");
            return false;
         }
         
        if ((hyphencount > 1) || ((value.length==10) && ""+value.charAt(5)!="-")) {
        //alert("The hyphen character should be used with a properly formatted 5 digit+four zip code, like '12345-6789'.   Please try again.");
            return false;
        }
    }
    
    return true;
}

// Add a parameter for onfocus to control client id when click error message link.
function doErrorCallbackFun(errorMessage, controlID, flag, childId, validateType, validChildIds, invalidChildIds) {
    var objErrIndicator = document.getElementById(controlID+'_err_indicator');
    var objLabel0 = document.getElementById(controlID+'_label_0');
    var objLabel1 = document.getElementById(controlID+'_label_1');
    var objLabel2 = document.getElementById(controlID + '_label_2');
    var childObj = null;

    if (!isNullOrEmpty(childId)) {
        childObj = { childId: childId, validateType: validateType, validChildIds: validChildIds, invalidChildIds: invalidChildIds };
    }

    if (isNullOrEmpty(myValidationErrorPanel.getError(controlID)) && validChildIds && validChildIds.split(',').contains(childId)) {
        flag = 0;
    }

    //0:initial 1:message 2: fail
    if (flag == 2) {
        if (objErrIndicator != null) {
            objErrIndicator.style.display = "";
        }

        if (objLabel0 != null) {
            objLabel0.className = "ACA_Error_Label";
        }

        if (objLabel1 != null) {
            objLabel1.className = "ACA_Error_Label";
        }

        if (errorMessage == "undefined") {
            errorMessage = "";
        }
	    
        if (objLabel2 != null) {
            objLabel2.className = "ACA_Error_Label aca_error_message font10px";
            objLabel2.innerHTML = errorMessage;   
        }
	}
	else if (flag == 0) {
        if(objErrIndicator != null) {
            objErrIndicator.style.display = "none";
        }
        
        if (objLabel0 != null) {
            objLabel0.className = "";
        }
	    
	    if (objLabel1 != null) {
            objLabel1.className = "";
        }
        
        if (objLabel2 != null) {
            objLabel2.className = "";
            objLabel2.innerHTML = "";
        }
    }

    //for section 508
    if (typeof (myValidationErrorPanel) != "undefined") {
        var flagOfGridViewValidation = $('#' + controlID).attr('validationByHiddenTextBox');
        var requredMessage = $(objLabel0).text();
        var resultMessage = "";
        var needHandle = true;

        if (flagOfGridViewValidation) {
            needHandle = false;
        }
        else {
            requredMessage = requredMessage == "*" ? myValidationErrorPanel.textRequired : requredMessage;
            var theLabel = $(objLabel1).text();
            errorMessage = (flag == 0 || typeof (errorMessage) == "undefined") ? "" : errorMessage;

            if (controlID.indexOf("ctl00_PlaceHolderMain_ddlInitUserList") > -1
            && document.getElementById('ctl00_PlaceHolderMain_rdInitUsers') != null
            && document.getElementById('ctl00_PlaceHolderMain_rdInitUsers').nextSibling != null) {
                theLabel = $(document.getElementById('ctl00_PlaceHolderMain_rdInitUsers').nextSibling).text();
            }

            resultMessage = (flag == 0) ? "" : theLabel + " " + requredMessage + " " + errorMessage;
        }

        if (needHandle) {
            myValidationErrorPanel.updateError(controlID, resultMessage, childObj);
            if (myValidationErrorPanel.errorPanelVisible) {
                var isAccessibilityEnabled = typeof (accessibilityEnabled) == "function" ? accessibilityEnabled() : false;
                myValidationErrorPanel.printErrors(isAccessibilityEnabled);
            }
        }
    }
}

//delimiterLength is mask delimiter length for mask control, example: Example: mask is "999-99-99", the length is 2
//delimiterLength + length of user input text = length, that means if delimiterLength is greater than 0, the lenght must be greater than 0.
//the actual length of a control should be the length of end user input, that meass is does not contain space, mask delimiters.
function getActualLength4Masked(value, mask)
{
    if (!value || value.trim().length == 0) {
        return 0;
    }

    var delimiters = getDelimiters(mask);
    if (!delimiters || delimiters.length == 0) {
        return value.trim().length;
    }

    var actualLength = 0;
    for (var i = 0; i < parseInt(value.length, 10); i++) {

        var currentChar = value.substring(i, i + 1);

        if (currentChar == " " || delimiters.contains(currentChar)) {
            continue;
        }

        actualLength++;
    }
    return actualLength;
}

//this function is from MaskedEditBehavior._createMask()
function getDelimiters(mask)
{
    var i = 0;
    var delimiters = "";
    while (i < parseInt(mask.length,10)) 
    {
        if ("9L$CAN?".indexOf(mask.substring(i, i+1)) == -1) 
        {
            if(mask.substring(i,i+1) != "{" && mask.substring(i,i+1) != "}")
            {
                delimiters += mask.substring(i,i+1);
            }
        }
        i++;
    }
    
    var delimArr = new Array();
    var j;
    var isDuplated = false;
    var m = 0;
    for(i=0;i <  parseInt(delimiters.length,10); i++)
    {
        isDuplated = false;
        for(j = 0; j< delimArr.length; j++)
        {
            if(delimiters.substring(i,i+1) == delimArr[j])
            {
                isDuplated = true;
            }
        }
        if(!isDuplated)
        {
            delimArr[m]=delimiters.substring(i,i+1);
            m++;
        }
    }
    
    //alert("getDelimiters...delimiters:" + delimiters);
    return delimArr;
}

//Set a value to a dropdownlist ignoring the case
function SetDropdownValue(controlId,value)
{
    var ddl = document.getElementById(controlId);
    
    for(var i = 0;i<ddl.options.length;i++)
    {
        if(ddl.options[i].value.toUpperCase()==value.toUpperCase())
        {
            ddl.options[i].selected= true;
            break;
        }
    }
}


// Simple helper to return the "exMaxLen" attribute for
// the specified field. Using "getAttribute" won't work
// with Firefox.
function GetMaxLength(targetField)
{
return targetField.exMaxLen;
}

//
// Limit the text input in the specified field.
//
function LimitInput(targetField, sourceEvent)
{
    var isPermittedKeystroke;
    var enteredKeystroke;
    var maximumFieldLength;
    var currentFieldLength;
    var inputAllowed = true;
    var selectionLength = parseInt(GetSelectionLength(targetField));
    
    if ( GetMaxLength(targetField) != null )
    {
        // Get the current and maximum field length
        currentFieldLength = parseInt(GetValue(targetField).length);
        maximumFieldLength = parseInt(GetMaxLength(targetField));

        // Allow non-printing, arrow and delete keys
        enteredKeystroke = window.event ? sourceEvent.keyCode : sourceEvent.which;
        isPermittedKeystroke = ((enteredKeystroke < 32)                                // Non printing
                     ||(enteredKeystroke >= 33 && enteredKeystroke <= 40)    // Page Up, Down, Home, End, Arrow
                     ||(enteredKeystroke == 46))                            // Delete

        // Decide whether the keystroke is allowed to proceed
        if ( !isPermittedKeystroke )
        {
            if ( ( currentFieldLength - selectionLength ) >= maximumFieldLength )
            {
                inputAllowed = false;
            }
        }
        
        // Force a trim of the textarea contents if necessary
        if ( currentFieldLength > maximumFieldLength )
        {
            SetValue(targetField, targetField.value.substring(0, maximumFieldLength));
        }
    }
    
    sourceEvent.returnValue = inputAllowed;
    return (inputAllowed);
}

//
// Limit the text input in the specified field.
//
function LimitPaste(targetField, sourceEvent)
{
    var clipboardText;
    var resultantLength;
    var maximumFieldLength;
    var currentFieldLength;
    var pasteAllowed = true;
    var selectionLength = GetSelectionLength(targetField);

    if ( GetMaxLength(targetField) != null )
    {
     // Get the current and maximum field length
     currentFieldLength = parseInt(GetValue(targetField).length);
        maximumFieldLength = parseInt(GetMaxLength(targetField));

        clipboardText = window.clipboardData.getData("Text");
        resultantLength = currentFieldLength + clipboardText.length - selectionLength;
        if ( resultantLength > maximumFieldLength)
        {
            pasteAllowed = false;
        }    
    }    
    
    sourceEvent.returnValue = pasteAllowed;
    return (pasteAllowed);
}

// validate the number when pasting
function LimitParse(control,evt) {
    var patt = /^(-?\d+(\.\d+)?|(\.\d+))$/;
    var isNumber = patt.test(GetValue(control));
    
    evt = evt ? evt : window.event;
    var key = evt.keyCode?evt.keyCode:evt.which; 
    
    if (!isNumber) {
        if(window.event)
        {
            evt.returnValue = false;
        }
        else
        {
            evt.preventDefault();
        } 
        SetValue(control,"");
    }
    
    return true;
}

//
// Returns the number of selected characters in
// the specified element
//
function GetSelectionLength(targetField)
{
    if ( targetField.selectionStart == undefined )
    {
        return document.selection.createRange().text.length;
    }
    else
    {
        return (targetField.selectionEnd - targetField.selectionStart);
    }
}

function ClearSplitChar(txtControl,mustNumber)
{
    var controlVal = GetValue(txtControl);
    if (controlVal != "") {
        if (mustNumber) {
            SetValue(txtControl, controlVal.search(/\d/) > -1 ? controlVal : "");
        }
        else {
            SetValue(txtControl, controlVal.search(/[^-\s]/) > -1 ? controlVal : "");
        }
    }    
}

//********************validation error handler begin

var ValidationError = {};

//validation error panel
ValidationError.Panel = function() {
    var cssClass = "ACA_Content";

    if (typeof($) != "undefined" && $.global != null) {
        if ($.global.isForPopUp) {
            cssClass = "ACA_Content_Popup";
        } else if ($.global.messageCSS != null) {
            cssClass = $.global.messageCSS;
        }
    }

    this.enabled = false;
    this.errorPanelVisible = true;
    this.iframeID = null;
    //below value will be updated after page loaded;
    this.isRTL = false;
    this.accessKey = "";
    this.errorIconAlt = "";
    this.errorIconURL = "";

    //below default text should be replaced by language-specific text after page loaded;
    this.textMore = "";
    this.textErrorNotice1 = "";
    this.textErrorNotice2 = "";
    this.textRequired = "";

    this.textNoErrorFound = "";
    this.errorNoticeID = "";
    this.pannelID1 = "ErrorList1";
    this.pannelID2 = "ErrorList2";
    this.errors = { };
    this.ids4recheck = { };
    this.maxErrorNumber4Display = 3;
    this.errorListPattern = "<div class='" + cssClass + "'><div class=\"ACA_Message_Error\"><table role=\"presentation\" class=\" \" border=\"0\" cellpadding=\"0\" cellspacing=\"0\"><tr><td valign=top style=\"padding-top: 2px;\"><img class=\"ACA_NoBorder\" alt=\"{0}\" src=\"{1}\"/></td><TD width=15><DIV>&nbsp;</DIV></TD><td vAlign=middle>{2}</td></tr></table></div></div> ";
    this.errorListItemPattern = "<a href=\"javascript:void(0)\" onclick=\"if (typeof(SetNotAsk)!=\'undefined\') SetNotAsk();if (typeof(myValidationErrorPanel)!=\'undefined\' && myValidationErrorPanel.skipTo) myValidationErrorPanel.skipTo('{0}',{1})\" {2} class=\"ACA_Message_Error_Link ACA_Message_Error_FontSize NotShowLoading\">{3}{4}{5}</a>";
    this.errorListMoreItemBeginPattern = "<a href=\"javascript:void(0)\" id=\"moreAnchorLink\" onclick=\"if (typeof(SetNotAsk)!=\'undefined\') SetNotAsk();if (typeof(myValidationErrorPanel)!=\'undefined\' && myValidationErrorPanel.toggleMoreLink) myValidationErrorPanel.toggleMoreLink('{0}_more')\" class=\"ACA_Message_Error_Link ACA_Message_Error_FontSize NotShowLoading\">{1}</a><div id=\"{0}_more\" style=\"display:none\">";
    this.errorListMoreItemEnd = "</div>";
};

//setup params after page loaded
ValidationError.Panel.prototype.InitParams = function(isRTL, accessKey, errorIconAlt, errorIconURL, textRequired, textMore, textErrorNotice1, textErrorNotice2) {
    this.isRTL = isRTL;
    this.accessKey = accessKey;
    this.errorIconAlt = errorIconAlt;
    this.errorIconURL = errorIconURL;
    this.textRequired = textRequired;
    this.textMore = textMore;
    this.textErrorNotice1 = textErrorNotice1;
    this.textErrorNotice2 = textErrorNotice2;
    this.enabled = true;
};

//get current iframe object
ValidationError.Panel.prototype.getIFrame = function(iframeID) {
    var oIframe = null;
    if (iframeID) {
        oIframe = window.frames[iframeID] ? window.frames[iframeID] : document.getElementById(iframeID);
    }
    
    return oIframe;
};

//get current document object
ValidationError.Panel.prototype.getDocument = function(iframeID) {
    var oDoc = null;
    
    if (iframeID) {
        var oIframe = this.getIFrame(iframeID);
        oDoc = oIframe ? oIframe.document || oIframe.contentDocument : null;
    } else {
        oDoc = document;
    }
    
    return oDoc;
};

//skip to target
ValidationError.Panel.prototype.skipTo = function(targetID, isToLocal) {
    var oIframe = null;
    var oDoc = document;
    iframeID = isToLocal ? null : this.iframeID;

    if (iframeID) {
        oIframe = this.getIFrame(iframeID);
        oDoc = this.getDocument(iframeID);
    }

    var oWindow = oIframe ? oIframe : window;
    var targetObj = oDoc ? oDoc.getElementById(targetID) : null;
    var originalNeedAsk = oIframe && oIframe.NeedAsk ? oIframe.NeedAsk : null;

    if (originalNeedAsk != null) {
        oWindow.SetNotAsk(false);
    }

    if (targetObj) {
        //special logic
        var targetTypes = ["text", "radio", "checkbox", "button", "file", "image", "password", "reset", "submit", "select-one", "select-multiple", "textarea"];
        var targetObjType = typeof(targetObj.type) == "undefined" ? "" : targetObj.type.toLowerCase();

        if (targetObjType == "" || targetObjType == "radio") {
            var tempObj = oDoc.getElementById(targetID + "_0");

            if (tempObj != null && typeof(tempObj.type) != "undefined"
                && (tempObj.type.toLowerCase() == "radio" || tempObj.type.toLowerCase() == "checkbox")) {
                targetObj = tempObj;
            }
        }
        
        if ($.trim(targetObjType) == "" || $.inArray(targetObjType, targetTypes) != -1) {
            try {
                if ($.global.isForPopUp == false) {
                    var p = $(targetObj).position();
                    window.scrollTo(p.left, p.top);
                }

                //To resolve the Location issue on Chrome and Safari.
                var ifrm = getParentDocument().getElementById("ACAFrame");
                if (ifrm != null && !isFireFox()) {
                    ifrm.setAttribute("scrolling", "yes");
                }

                targetObj.focus();

                if (ifrm != null && !isFireFox()) {
                    ifrm.setAttribute("scrolling", "no");
                }
            } catch(e) {
            }
        }
    }

    if (originalNeedAsk != null) {
        oWindow.SetNotAsk(originalNeedAsk);
    }
};

//toggle "more" link visibility
ValidationError.Panel.prototype.toggleMoreLink = function(targetID) {
	if(document.getElementById('moreAnchorLink').innerHTML == "more..."){
		document.getElementById('moreAnchorLink').innerHTML = "less...";
	}else{
		document.getElementById('moreAnchorLink').innerHTML = "more...";
	}
    var targetObj = document.getElementById(targetID);
    targetObj.style.display = targetObj.style.display == "none" ? "" : "none";
};

//get error message
ValidationError.Panel.prototype.getError = function (controlID) {
    var result = null;
    
    $.each(this.errors, function(key, value) {
        if (key == controlID) {
            result = value;
            return;
        }
    });

    result = ValidationErrorUtil.getErrorMsgFromValue(result);
    if (!isNull(result)) {
        result = result.errorMsg;
    }

    return result;
};

//detect whether error collection contains current controlID
ValidationError.Panel.prototype.containError = function(controlID) {
    var result = false;
    
    $.each(this.errors, function(key, value) {
        if (key == controlID) {
            result = true;
            return;
        }
    });
    
    return result;
};

//ensure all errors are valid
ValidationError.Panel.prototype.ensureErrorsValid = function() {
    var thisObject = this;
    var oDoc = this.getDocument(this.iframeID);

    if (oDoc) {
        $.each(this.errors, function(key, value) {
            var controlObject = oDoc.getElementById(key);
            if (controlObject == null) {
                thisObject.errors[key] = null;
            }
        });
    }
};

//update error message to the collection
ValidationError.Panel.prototype.updateError = function (controlID, errorMessage, childObj) {
    if (!this.enabled) {
        return;
    }

    var msgId = controlID;
    var validateType = "";
    if (!isNull(childObj) && !isNullOrEmpty(childObj.childId)) {
        msgId = childObj.childId;
    }
    if (!isNull(childObj) && !isNullOrEmpty(childObj.validateType)) {
        validateType = childObj.validateType;
    }

    // errorMsgValues[] = { msgId, validate: [{type, msg}] }
    this.errors[controlID] = ValidationErrorUtil.setErrorMsg(this.errors[controlID], msgId, validateType, errorMessage, childObj);
};

//get error list HTML string
ValidationError.Panel.prototype.getErrorList = function() {
    var isRTL = this.isRTL;
    var result = "";
    var counter = 0;
    var hasMoreItem = false;
    var maxErrorNumber4Display = this.maxErrorNumber4Display;
    var errorListMoreItemBeginPattern = this.errorListMoreItemBeginPattern;
    var textMore = this.textMore;
    var errorListItemPattern = this.errorListItemPattern;
    var firstErrorID = "";
    var errorNoticeID = "";
    var thisObject = this;

    this.ensureErrorsValid();

    $.each(this.errors, function(key, value) {
        var errorMsgItem = ValidationErrorUtil.getErrorMsgFromValue(value);
        if (isNull(errorMsgItem) || isNullOrEmpty(errorMsgItem.errorMsg)) {
            return;
        }

        var newLine = result == "" ? "" : "<br>";
        counter++;
        var currentItemID = key + "v_a_l_i_d" + counter;

        if (counter == 1) {
            errorNoticeID = key + "v_a_l_i_d0";
            firstErrorID = currentItemID;
        }

        if (counter == (maxErrorNumber4Display + 1)) {
            var errorListMoreItemBegin = errorListMoreItemBeginPattern.replace(/\{0\}/g, key).replace(/\{1\}/g, textMore);
            result += newLine + newLine + errorListMoreItemBegin;
            hasMoreItem = true;
        }

        var additionalPropertyString = " id=\"" + currentItemID + "\"";
        var items = [counter, ".", errorMsgItem.errorMsg];
        items = isRTL ? items.reverse() : items;

        var focusId = errorMsgItem.controlId;
        var errorItem = errorListItemPattern
            .replace(/\{0\}/g, focusId)
            .replace(/\{1\}/g, false)
            .replace(/\{2\}/g, additionalPropertyString)
            .replace(/\{3\}/g, items[0])
            .replace(/\{4\}/g, items[1])
            .replace(/\{5\}/g, items[2]);
        result += newLine + errorItem;
    });

    if (hasMoreItem) {
        result += this.errorListMoreItemEnd;
    }

    if (counter == 0) {
        result = this.textNoErrorFound;
    } else {
        this.errorNoticeID = errorNoticeID;
        var accessKeyStringConst = " accesskey=\"" + this.accessKey + "\" ";
        var accessKeyString = ($.detectedBrowser.msie) ? accessKeyStringConst : "";
        var additionalPropertyString = accessKeyString + " id=\"" + this.errorNoticeID + "\"";
        var errorNoticePattern = counter == 1 ? this.textErrorNotice1 : this.textErrorNotice2;
        var errorNotice = errorNoticePattern.replace(/\{0\}/g, counter);
        var items = [errorNotice, "", ""];
        items = isRTL ? items.reverse() : items;
        var errorNoticeItem = errorListItemPattern
            .replace(/\{0\}/g, firstErrorID)
            .replace(/\{1\}/g, true)
            .replace(/\{2\}/g, additionalPropertyString)
            .replace(/\{3\}/g, items[0])
            .replace(/\{4\}/g, items[1])
            .replace(/\{5\}/g, items[2]);
        var prefixString = ($.detectedBrowser.msie) ? "" : "<a tabindex=-1 href=\"javascript:void(0)\" onclick=\"document.getElementById('" + this.errorNoticeID + "').focus()\" " + accessKeyStringConst + "></a>";
        result = prefixString + errorNoticeItem + "<br><br>" + result;
        result = this.errorListPattern.replace(/\{0\}/g, thisObject.errorIconAlt).replace(/\{1\}/g, thisObject.errorIconURL).replace(/\{2\}/g, result);
    }

    return result;
};

//register IDs for recheck
ValidationError.Panel.prototype.registerIDs4Recheck = function(controlID) {
    this.ids4recheck[controlID] = "";
};

//on recheck
ValidationError.Panel.prototype.onRecheck = function(sender, args) {
    if (typeof(myValidationErrorPanel) != "undefined") {
        var sourceElementID = (sender && sender._postBackSettings && sender._postBackSettings.sourceElement) ? sender._postBackSettings.sourceElement.id : "";
        myValidationErrorPanel.doRecheck(sourceElementID);
    }
};

//do recheck
ValidationError.Panel.prototype.doRecheck = function(sourceElementID) {
    if (!this.enabled) {
        return;
    }

    var needRecheckAllErrors = false;
    $.each(this.ids4recheck, function(key, value) {
        if (sourceElementID == key || sourceElementID.indexOf(key) == 0) {
            needRecheckAllErrors = true;
        }
    });

    if (needRecheckAllErrors) {
        this.recheckAllErrors(false);
    }
};

//recheck all errors
ValidationError.Panel.prototype.recheckAllErrors = function(needSkipToErrorList) {
    if (!this.enabled) {
        return;
    }

    var thisObject = this;
    var needUpdateErrorList = false;
    $.each(this.errors, function(key, value) {
        var targetObject = document.getElementById(key);
        var targetErrIndicator = document.getElementById(key + '_err_indicator');
        var notExistObject = targetObject == null;
        var displayStyle = targetErrIndicator && targetErrIndicator.style && targetErrIndicator.style["display"] ? targetErrIndicator.style["display"].toLowerCase() : "";
        if (notExistObject || displayStyle == "none") {
            needUpdateErrorList = true;
            thisObject.errors[key] = null;
        }
    });

    if (needUpdateErrorList) {
        needSkipToErrorList = needSkipToErrorList == null ? false : needSkipToErrorList;
        this.printErrors(needSkipToErrorList);
    }
};


//reserve all errors
ValidationError.Panel.prototype.reservedAllErrors = function () {
    if (!this.enabled) {
        return;
    }

    var removeErrors = [];
    $.each(this.errors, function (key, value) {
        if ($.exists('#' + key)) {
            if (value != null) {
                $.each(value[0].validate, function () {
                    if (!isNullOrEmpty(this.msg)) {
                        //the dropdownlist validation control and DuplicateValidate control named begin with "key"
                        $.each($('span[id*="' + key + '"]'), function () {
                            if (this.controltovalidate && this.controltovalidate.indexOf(key) > -1) {
                                this.isNeedValidate = true;
                                ValidatorValidate(this, null, null);
                                ValidatorUpdateIsValid();
                            }
                        });
                    }
                });
            }
        } else {
            //if this control don't exist, need to clear this control error.
            removeErrors.push(key);
        }
    });

    if (removeErrors && removeErrors.length > 0) {
        for (var i = 0; i < removeErrors.length; i++) {
            doErrorCallbackFun('', removeErrors[i], 0);
            delete this.errors[removeErrors[i]];
        }
    }
};

//clear current section errors, only after post back.
ValidationError.Panel.prototype.clearCurrentSectionErrors = function (sectionId) {
    if (!this.enabled) {
        return;
    }

    var removeErrors = [];
    $.each(this.errors, function (key, value) {
        if (key.indexOf(sectionId) == 0) {
            removeErrors.push(key);
        }
    });

    if (removeErrors && removeErrors.length > 0) {
        for (var i = 0; i < removeErrors.length; i++) {
            doErrorCallbackFun('', removeErrors[i], 0);
            delete this.errors[removeErrors[i]];
        }
    }
};

//clear errors
ValidationError.Panel.prototype.clearErrors = function() {
    if (!this.enabled) {
        return;
    }

    $.each(this.errors, function(key, value) {
        doErrorCallbackFun('', key, 0);
    });

    this.errors = { };
    this.printErrors();
};

//print errors
ValidationError.Panel.prototype.printErrors = function(needFocus) {
    if (!this.enabled) {
        return;
    }

    var panelString = this.getErrorList();
    var errorListPanel1 = document.getElementById(this.pannelID1);
    var errorListPanel2 = document.getElementById(this.pannelID2);
    var errorListPanel = errorListPanel2 || errorListPanel1 || null;

    if (errorListPanel) {
        errorListPanel.innerHTML = panelString;
    }

    if (typeof(SetNotAsk) != 'undefined') {
        SetNotAsk();
    }

    if (needFocus == null || needFocus) {
        this.errorNoticeID && window.setTimeout("myValidationErrorPanel.skipTo(myValidationErrorPanel.errorNoticeID, true)", 1);
    }
};

//new instance
if (typeof (myValidationErrorPanel) == "undefined" && typeof (ValidationError) != "undefined") {
    var myValidationErrorPanel = new ValidationError.Panel();
}

//init validation error panel
function InitValidationErrorPanel() {
    var param_isRTL = $.global.isRTL;
    var param_accessKey = typeof (GLOBAL_VALIDATION_RESULTS_ACCESSKEY) == "undefined" ? "" : GLOBAL_VALIDATION_RESULTS_ACCESSKEY;
    var param_errorIconAlt = typeof (getText.global_js_showError_alt) == "undefined" ? "" : getText.global_js_showError_alt;
    var param_errorIconURL = typeof (getText.global_js_showError_src) == "undefined" ? "" : getText.global_js_showError_src;
    var param_textMore = typeof (getText.global_section508_more) == "undefined" ? "" : getText.global_section508_more;
    var param_textRequired = typeof (getText.global_section508_required) == "undefined" ? "" : getText.global_section508_required;
    var param_textErrorNotice1 = typeof (getText.global_section508_errornotice1) == "undefined" ? "" : getText.global_section508_errornotice1;
    var param_textErrorNotice2 = typeof (getText.global_section508_errornotice2) == "undefined" ? "" : getText.global_section508_errornotice2;
    myValidationErrorPanel.InitParams(param_isRTL, param_accessKey, param_errorIconAlt, param_errorIconURL, param_textRequired, param_textMore, param_textErrorNotice1, param_textErrorNotice2);

    if (typeof (Sys) != "undefined" && Sys.WebForms && Sys.WebForms.PageRequestManager && Sys.WebForms.PageRequestManager.getInstance) {
        var prm = Sys.WebForms.PageRequestManager.getInstance();

        if (prm && prm.add_endRequest) {
            prm.add_endRequest(myValidationErrorPanel.onRecheck);
        }
    }
}

//set ctrl required html
function SetCtrlRequiredHtml(isRequired, ctrlClinetId) {
    var $requiredTag = $('#' + ctrlClinetId + '_label_0');

    if (isRequired) {
        // add the required tag and validate error message
        var requiredText = ACA_REQUIRED_FIELD;
        $requiredTag.html('<div class="ACA_Required_Indicator">*</div>');
        setAccelaControlTip(ctrlClinetId, requiredText);
    }
    else {
        // clear required tag and validate error message
        $requiredTag.html('');
        setAccelaControlTip(ctrlClinetId);
    }
}

//********************validation error handler end
//Required
/***********************************************************************************************
*
* Func: AddValidationToRequiedControl
* Desc: Add Required Validation for one control to Page_Validators collection.
* Para: 
*       requiredControlID   -    Control ID
*       requiredValidatorID  -   required validator control id
*       isOnFocus           - isOnFocus
***********************************************************************************************/
function AddValidationToRequiedControl(requiredControlID, requiredValidatorID, isOnFocus) {

    // 1. Get control by ID
    var RequiedControl = $get(requiredControlID);

    if (RequiedControl == null) {
        return;
    }

    // 2. Get Validator ID and control object.
    var requiredValidatorControl = $get(requiredValidatorID);

    // 2.1 Initialize Required Validation Control's properties.
    requiredValidatorControl.controltovalidate = requiredControlID;
    requiredValidatorControl.errormessage = "";
    requiredValidatorControl.focusOnError = "";
    
    if (isOnFocus) {
        requiredValidatorControl.focusOnError = "t";
    }

    if (typeof (RequiredFieldValidatorEvaluateIsValid) != "undefined") {
        requiredValidatorControl.evaluationfunction = RequiredFieldValidatorEvaluateIsValid;
    }

    //register our defined validation function for raido button list.
    if ($(':radio', $(RequiedControl)).length > 0) {
        requiredValidatorControl.evaluationfunction = "cb_vefify";
    }

    requiredValidatorControl.initialvalue = "";

    // 2.2 Add Required Control's validation control into Page_Validators
    if (typeof (Page_Validators) != "undefined") {
        Page_Validators[Page_Validators.length] = requiredValidatorControl;
    }

    // 3. Append three functions to this control object.
    $get(requiredValidatorID).dispose = function () {
        Array.remove(Page_Validators, document.getElementById(requiredValidatorID));
    }

    Sys.Application.add_init(function () {
        $create(AjaxControlToolkit.ValidatorCallbackBehavior, { "callbackControlID": requiredControlID, "callbackFailFunction": "doErrorCallbackFun", "highlightCssClass": "HighlightCssClass", "id": requiredControlID }, null, null, $get(requiredValidatorID));
    });

    if (RequiedControl.type == "checkbox") {
        Sys.UI.DomEvent.addHandler(RequiedControl, "click", ValidateToControlOnExpression);
    } else {
        Sys.UI.DomEvent.addHandler(RequiedControl, "change", ValidateToControlOnExpression);
    }
}

/***********************************************************************************************
*
* Func: RemoveValidationFromRequiredControl
* Desc: Remove one control's Required Validation from Page_Validators collections.
* Para: 
*       requiredControlID     -    Control ID
*       requiredValidatorID   -    Requird validator control id   
*
***********************************************************************************************/
function RemoveValidationFromRequiredControl(requiredControlID, requiredValidatorID) {
    // 1. Get control by ID
    var requiredControl = $get(requiredControlID);

    if (requiredControl == null) {
        return;
    }

    // 2. Remove control's required validation from Page_Validators(More details please see func AddValidationToRequiedControl).
    if (typeof (Page_Validators) != "undefined" && Page_Validators != null) {
        for (var i = 0; i < Page_Validators.length; i++) {
            var val = Page_Validators[i];

            if (val != null && val.controltovalidate != null
                && val.id == requiredValidatorID && val.controltovalidate == requiredControlID) {
                Array.removeAt(Page_Validators, i);
                i--;
            }
        }
    }
}

/***********************************************************************************************
*
* Func: ValidateToControlOnExpression
* Desc: When the value of required control is changed, this function will be fired.
* Para: 
*       N/A
*   
***********************************************************************************************/
function ValidateToControlOnExpression() {

    var validateControl;
    if (typeof (event) != "undefined") {
        validateControl = event.srcElement;
    }
    else {
        validateControl = this;
    }

    if (!isNull(validateControl) && !isNullOrEmpty(validateControl.className)) {
        if (validateControl.className.indexOf("ACA_ReadOnly") > -1) {
            return;
        }
    };

    var flag = 0; // 0 -- success, 2-- failed
    if (validateControl.type == "checkbox" && validateControl.checked == false) {
        flag = 2;
    } else {
        if (validateControl.value == "") {
            flag = 2;
        }
    }

    doErrorCallbackFun("", validateControl.id, flag);
}

var ValidationErrorUtil = new function () {
    this.setErrorMsg = setErrorMsg;
    this.getErrorMsgFromValue = getErrorMsgFromValue;

    // errorMsgValues[] = { msgId, validate: [{type, msg}] }
    function setErrorMsg(errorMsgValues, msgId, validateType, message, childObj) {
        if (isNull(errorMsgValues) || !(errorMsgValues instanceof Array) || errorMsgValues.length == 0) {
            errorMsgValues = new Array();

            if (!isNull(childObj)) {
                errorMsgValues = initErrorMsgValues(childObj, validateType, message);
            } else {
                errorMsgValues[0] = updateErrorMsgItem(null, msgId, validateType, message);
            }

            return errorMsgValues;
        }

        if (!isNull(childObj)) {
            $.each(errorMsgValues, function (index, item) {
                if (childObj.validChildIds && childObj.validChildIds.split(',').contains(item.msgId)) {
                    item = updateErrorMsgItem(item, item.msgId, validateType, '');
                } else if (childObj.invalidChildIds && childObj.invalidChildIds.split(',').contains(item.msgId)) {
                    item = updateErrorMsgItem(item, item.msgId, validateType, message);
                }
            });
        } else {
            $.each(errorMsgValues, function (index, item) {
                if (item.msgId == msgId) {
                    item = updateErrorMsgItem(item, item.msgId, validateType, message);
                    return false;
                }
            });
        }

        return errorMsgValues;
    }

    function initErrorMsgValues(childObj, validateType, message) {
        var errorMsgValues = new Array();

        var validateChildIds = childObj.validChildIds.split(',');
        $.each(validateChildIds, function (index, childId) {
            if (!isNullOrEmpty(childId)) {
                errorMsgValues[errorMsgValues.length] = updateErrorMsgItem(null, childId, validateType, '');
            }
        });

        var invalidateChildIs = childObj.invalidChildIds.split(',');
        $.each(invalidateChildIs, function (index, childId) {
            if (!isNullOrEmpty(childId)) {
                errorMsgValues[errorMsgValues.length] = updateErrorMsgItem(null, childId, validateType, message);
            }
        });
        return errorMsgValues;
    }

    function updateErrorMsgItem(errorMsgItem, msgId, validateType, msg) {
        if (!errorMsgItem || errorMsgItem.msgId != msgId) {
            return { msgId: msgId, validate: [{ type: validateType, msg: msg}] };
        } else {
            var containValidType = false;
            $.each(errorMsgItem.validate, function () {
                if (this.type == validateType) {
                    this.msg = msg;
                    containValidType = true;
                    return false;
                }
            });

            if (!containValidType) {
                errorMsgItem.validate[errorMsgItem.validate.length] = { type: validateType, msg: msg };
            }
            return errorMsgItem;
        }
    }

    // get error message from error value.
    // value is list as the format: [ControlID/ChildID]={ msgId, validate: [{type, msg}] }.
    function getErrorMsgFromValue(errorValue) {
        if (isNull(errorValue)) {
            return null;
        }

        // Sort the array by msgId
        sortErrorsByMsgId(errorValue);
        var errorMsgItem = {};
        $.each(errorValue, function () {
            var errorItem = this;
            var foundErrorMsg = false;
            $.each(errorItem.validate, function () {
                if ($.trim(this.msg) != "") {
                    errorMsgItem = { controlId: errorItem.msgId, errorMsg: this.msg };
                    foundErrorMsg = true;
                    return false;
                }
            });

            // break the each if found error.
            if (foundErrorMsg) {
                return false;
            }
        });

        if (isNull(errorMsgItem) || $.trim(errorMsgItem.errorMsg) == "") {
            return null;
        }

        return errorMsgItem;
    }
    
    // Bubble sort - by msgId
    function sortErrorsByMsgId(arr) {
        var temp = '';
        for (var k = 0; k < arr.length; k++) {
            for (var m = 0; m < arr.length - k - 1; m++) {
                if (arr[m].msgId > arr[m + 1].msgId) {
                    temp = arr[m + 1];
                    arr[m + 1] = arr[m];
                    arr[m] = temp;
                }
            }
        }
    }
};

ValidationError.Panel.prototype.isValidationPassExceptRequiredField = function (userControlId) {
    var totalFailedValidationCount = 0;
    var totalRequiredFailedValidationCount = 0;
        
    // Get required validation error items count.
    if (Page_Validators != undefined && Page_Validators != null && Page_Validators.length > 0) {
        for (var i = 0; i < Page_Validators.length; i++) {
            if (Page_Validators[i].id.indexOf(userControlId) > -1 && Page_Validators[i].isvalid != undefined && !Page_Validators[i].isvalid) {
                totalFailedValidationCount += 1;

                if (Page_Validators[i].id.indexOf("_baseReq") > -1 || Page_Validators[i].id.indexOf("_req") > -1
                    || (Page_Validators[i].validateType != undefined && Page_Validators[i].validateType == "required")) {
                    totalRequiredFailedValidationCount += 1;
                }
            }
        }
    }

    if (totalFailedValidationCount - totalRequiredFailedValidationCount < 1) {
        return true;
    }
    else {
        // Invoke this method to set focus.
        this.getErrorList();
        myValidationErrorPanel.skipTo(myValidationErrorPanel.errorNoticeID, true);
    }

    return false;
}