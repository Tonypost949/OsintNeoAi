/**
* <pre>
*  Accela Citizen Access
*  File: RelatedRecordsTree.js
*
*  Accela, Inc.
*  Copyright (C): 2011-2014
*
*  Description: Scripts for the Related Records tree.
*
*  Notes:
* $Id: RelatedRecordsTree.js 171222 2010-04-21 16:10:00Z ACHIEVO\alan.hu $.
*  Revision History
*  Date,           Who,        What
*  2014/04/22     Alan Hu     Initial.
* </pre>
*/

//Expand/Collapse CAP tree by click tree node
function CapTreeAction(elementID) {
    var $captreeTr = $('tr[id^=' + elementID + '_]');

    var lnk = document.getElementById('img' + elementID);
    var lnkObj = document.getElementById('lnk' + elementID);

    if (lnk.className == "ACA_CapTree_Expand") {
        lnk.className = "ACA_CapTree_Collapse";
        Collapsed(lnk, CTreeTop, altExpanded);
        AddTitle(lnkObj, altExpanded, null);
        $captreeTr.hide();
    }
    else {
        lnk.className = "ACA_CapTree_Expand";
        Expanded(lnk, ETreeTop, altCollapsed);
        AddTitle(lnkObj, altCollapsed, null);

        $captreeTr.show();

        $capImg = $('img[id=img'+elementID+']');

        $capImg.addClass('ACA_CapTree_Expand');
        $capImg.attr("src", ETreeTop);
    }
}