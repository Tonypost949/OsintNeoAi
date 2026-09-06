/**
 * <pre>
 * 
 *  Accela
 *  File: MyCollectionMethods.js
 * 
 *  Accela, Inc.
 *  Copyright (C): 2009-2014
 * 
 *  Description:
 * To deal with some message when adding selected CAPs to my collection.
 *  Notes:
 * $Id: MyCollectionMethods.js 266252 2014-02-20 10:26:50Z ACHIEVO\james.shi $.
 *  Revision History
 *  &lt;Date&gt;,    &lt;Who&gt;,    &lt;What&gt;
 *  03/31/2009     		rainbow.zhou				Initial.
 * </pre>
 */

//this is pop up the collection window click element
var addCollectionClickElement;

//set added successfully message position.
function setAddedMessagePosition(obj,isRightOrLeft)
{
    var divAdded = window.document.getElementById("divAdded");
    var divMessageSpan = window.document.getElementById("messageSpan");
    var messageSpanHeight = 0;

    if (divMessageSpan) {
        messageSpanHeight = divMessageSpan.offsetHeight;
    }
    if(isRightOrLeft == "True")
    {
        divAdded.style.left =  (getElementLeft(obj)-226 + obj.offsetWidth) + "px";
    }
    else
    {
        divAdded.style.left = getElementLeft(obj) + "px";
    }

    divAdded.style.top = (getElementTop(obj) - messageSpanHeight + obj.offsetHeight) + "px";
    divAdded.style.zIndex = "10";
}

//set added successfully message position.
function setAddedMessageForDetail(obj,isRightOrLeft)
{
    var divAdded = window.document.getElementById("divAdded");
    if(isRightOrLeft == "True")
    {
        divAdded.style.left = getElementLeft(obj) + "px"; 
    }
    else
    {
        divAdded.style.left =  (getElementLeft(obj)-226 + obj.offsetWidth) + "px";
    } 
    divAdded.style.top = (getElementTop(obj) + obj.offsetHeight) + "px";
    divAdded.style.zIndex = "10";
}

//display adding message.
function displayAddingMessage(msg){
    var p = new ProcessLoading();
    p.showLoading();
    p.setTitle(msg);
}

//display added message.
function displayAddedMessage(msg,isCreateCollection)
{
    var divAdded = window.document.getElementById("divAdded");
    divAdded.innerHTML = "<a href='javascript:void(0)' class='NotShowLoading' style='text-decoration: none; color:#666666; cursor:default' id='addedCollectionMsg'>" + msg + "</a>";
    divAdded.style.display = "block";
    document.getElementById('addedCollectionMsg').focus();
    setTimeout("hideAddedMessage('"+isCreateCollection+"')",6000);
}

function hideAddedMessage(isCreateCollection)
{
    var divAdded = window.document.getElementById("divAdded");
    divAdded.style.display = "none";
    if(isCreateCollection == "True")
    {
        window.location.href = window.location.href;
    }

    if (addCollectionClickElement != null) {
        addCollectionClickElement.focus();
        addCollectionClickElement = null;
    }
}  

function Reload(msg)
{
    if(msg=="")
    {
        window.location.href = window.location.href;
    }
    else
    {
        var divAdded = window.document.getElementById("divAdded");
        divAdded.innerHTML = msg;
        divAdded.style.display = "block";
        setTimeout(hiddenAddedSuccessMessage,6000); 
    }
}  

function hiddenAddedSuccessMessage()
{
    var divAdded = window.document.getElementById("divAdded");
    divAdded.style.display = "none";
    window.location.href = window.location.href;
}

function displayAlertMessage(msg)
{
    window.setTimeout("alert('"+ msg +"')",0);
}  

function getElementTop(obj)
{
    var top = obj.offsetTop;
    
    var parentobj = obj.offsetParent;
    while (parentobj)
    {
        if (parentobj.offsetTop == undefined) {
            break;
        }
        top += parentobj.offsetTop;
        parentobj = parentobj.offsetParent;
    }
    
    return top;
}
    
function getElementLeft(obj)
{
    var left = obj.offsetLeft;
    
    var parentobj = obj.offsetParent;
    while (parentobj)
    {
        if (parentobj.offsetLeft == undefined) {
            break;
        }
        left += parentobj.offsetLeft;
        parentobj = parentobj.offsetParent;
    }
    return left;
} 