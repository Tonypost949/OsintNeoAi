/**
 * <pre>
 * 
 *  Accela
 *  File: ShoppingCartMethods.js
 * 
 *  Accela, Inc.
 *  Copyright (C): 2009-2011
 * 
 *  Description:
 * To deal with some message when adding selected CAPs to my collection.
 *  Notes:
 * $Id: ShoppingCartMethods.js 194148 2011-03-30 06:42:36Z ACHIEVO\daly.zeng $.
 *  Revision History
 *  &lt;Date&gt;,    &lt;Who&gt;,    &lt;What&gt;
 *  05/14/2009     		meit.mei				Initial.
 * </pre>
 */

var cartClickElement;
        
//display adding message.
function displayAddingToCartMessage(msg) {
    var p = new ProcessLoading();
    p.showLoading();
    p.setTitle(msg);
} 

//display added message.
function displayCartMessage(msg, isNeedRefreshCartNumber, cartNumberHTML) {
    var divAdded = window.document.getElementById("divAdded");
    divAdded.innerHTML = "<a href='javascript:void(0)' class='NotShowLoading' style='text-decoration: none; color:#666666; cursor:default' id='addedCartMsg'>" + msg + "</a>";
    divAdded.style.display = "block";

    if (isNeedRefreshCartNumber == "True") {
        updateCartNumber(cartNumberHTML);
    }

    document.getElementById('addedCartMsg').focus();
    setTimeout("hideCartMessage()", 6000);
} 
      
function hideCartMessage()
{
    var divAdded = window.document.getElementById("divAdded");
    divAdded.style.display = "none";
    if (cartClickElement != null) {
        cartClickElement.focus();
        cartClickElement = null;
    }
} 

function displayCartAlertMessage(msg)
{
    showMessage("messageSpan", msg, "Notice", true, 1);
}
  
function AddCapToCart(e,gridObj,isRightToLeft,postBackControlID)
{
    var obj = e.srcElement? e.srcElement : e.target;
    var postBackArgument = gridObj.id;
    __doPostBack(postBackControlID,postBackArgument);

    setAddedMessagePosition(obj,isRightToLeft);
}
        