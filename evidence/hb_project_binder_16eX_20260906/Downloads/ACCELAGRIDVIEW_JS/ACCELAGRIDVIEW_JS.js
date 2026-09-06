/**
 * <pre>
 * 
 *  Accela Citizen Access
 *  File: ACCELAGRIDVIEW_JS.js
 * 
 *  Accela, Inc.
 *  Copyright (C): 2008-2014
 * 
 *  Description:
 * 
 *  Notes:
 * $Id: PlanList.ascx.cs 72643 2007-07-10 21:52:06Z $.
 *  Revision History
 *  &lt;Date&gt;,    &lt;Who&gt;,    &lt;What&gt;
 * </pre>
 */
function CheckAll(me,hf)
{
    var index = me.name.indexOf('_');  
    var prefix = me.name.substr(0,index); 
    //Get GridView id, remove '_hfSaveSelectedItems' from hf to get grid view id. 
    var gridid = hf.substring(0,hf.length -20);
    for(var i=0; i<document.forms[0].length; i++) 
    { 
        var o = document.forms[0][i]; 
        if (o.type == 'checkbox' && o.id.indexOf('CB_') > -1 && o.id.indexOf(gridid) > -1) 
        { 
            if (me.name != o.name) 
            {
                if (o.name.substring(0, prefix.length) == prefix) 
                { 
                    // Must be this way
                    o.checked = me.checked;  
                    Check(o,hf);
                }
            }
        } 
    }
}



function ApplyStyle(me, selectedForeColor, selectedBackColor, foreColor, backColor, bold, checkBoxHeaderId) 
{ 
    var td = me.parentNode;
    if (td == null) {
        return;
    }

    var tr = td.parentNode;
    if (me.checked)
    { 
       tr.style.fontWeight = 700; // bold
       tr.style.color = selectedForeColor; 
       tr.style.backgroundColor = selectedBackColor; 
    } 
    else 
    { 
       document.getElementById(checkBoxHeaderId).checked = false;
       tr.style.fontWeight = bold; 
       tr.style.color = foreColor; 
       tr.style.backgroundColor = backColor; 
    } 
}

function SingleCheck(me) {
    for (var i = 0; i < document.forms[0].length; i++) {
        var o = document.forms[0][i];
        if (o.type == 'checkbox') {
            if (me.name != o.name) {
                if (me.checked) {
                    o.checked = !me.checked;
                }
            }
        }
    }
}

function SelectRadioButton(me)
{
    for(var i=0; i<document.forms[0].length; i++) 
    { 
        var obj = document.forms[0][i];
        if (obj.id.indexOf('RadioButtonField') != -1) 
        {
            if (me.name != obj.name) 
            {
                 if(me.checked)
                 {
                     obj.checked = !me.checked; 
                 }
            }
        } 
    } 
}

function Check(checkbox, hfId, isSingle)
{
    var hd = $get(hfId);
    
    if (hd.value == '' || isSingle)
    {
        hd.value = ',';
    }
    var ids = checkbox.id.split('_');
    var id = ids[ids.length - 2] + '_' + ids[ids.length - 1];
    if(checkbox.checked)
    {
        if(hd.value.indexOf(',' + id + ',') == -1)
        {
            hd.value = hd.value + id + ',';
        }
    }
    else
    {
        if(hd.value.indexOf(',' + id + ',') > -1)
        {
            hd.value = hd.value.replace(id + ',','');
        }
    }
}

function CheckRequired4GridView(gridValidatorId) {
    var lbl = $get(gridValidatorId + "_lbl_error_msg");
    var gridValidator = $get(gridValidatorId);

    if (lbl && gridValidator) {
        var errorMessage = gridValidator.getAttribute('ErrorMsg');
        lbl.innerHTML = '<div class="ACA_Error_Label"><table role="presentation"><tr><td><div class="ACA_Error_Indicator_In_Same_Row"><img class="ACA_NoBorder" alt="" src="../app_themes/Default/assets/error_16.gif" /></div></td><td>' + errorMessage + '</td></tr></table></div>';
        if (typeof (showMessageForSection508) == "function") {
            showMessageForSection508(errorMessage);
        }
        var anchor = document.getElementById(gridValidatorId+"_anchor");
        goToMessageBlock(anchor);
        var container = $(lbl);
        container.attr("tabindex", -1);
        container.attr("role", "link");
        container.attr("aria-label", errorMessage);
        container.focus();
    }

    return false;
}

function TriggleExport(type, gridId, linkId) 
{
    __doPostBack(linkId, gridId + '|' + type);

    //Show the Loading.
    var p = new ProcessLoading();
    p.showLoading(false); 
}

 function ExportCSV(sender, args)
 {
     //export file.
     if (sender._postBackSettings != null &&
         sender._postBackSettings.sourceElement != null && 
         sender._postBackSettings.sourceElement.id.indexOf('4btnExport') > -1) {
         var a = $get('iframeExport');
         var d = new Date();

         a.src = GLOBAL_APPLICATION_ROOT + "Export2CSV.ashx?flag=" + d.getSeconds() + d.getMinutes();
     }
 } 
 
function triggleAddToCart(e,btnAppendToCartId,isRightToLeft,gridObj)
{
    var postBackControlID = btnAppendToCartId;
    // This param is define in ShoppingCartMethods.js , it's use for focus link after pop up window closed.
    cartClickElement = gridObj;
    AddCapToCart(e,gridObj,isRightToLeft,postBackControlID);
}

function triggerCloneRecord(btnCloneRecordId, gridObj)
{
    var postBackControlID = btnCloneRecordId;
    var postBackArgument = gridObj.id;
    __doPostBack(postBackControlID, postBackArgument);
}

var showGirdViewShortList = true;

// trigger the short list
// id: the short list button id
// selectedId: the hidden field's id whose control store the selected checkbox's value.
function triggerShortList(id, gridId, selectedId) {
    var selectedItems = $('#' + selectedId).val();

    if (showGirdViewShortList && selectedItems.replace(',', '') == '') {
        return false;
    }
    else {
        showGirdViewShortList = !showGirdViewShortList;
        return true;
    }
}