function ShowAnnouncementByTimer() {
    if ($get("divAnnouncement") == undefined) {
        return;
    }
    Accela.ACA.Web.WebService.AnnouncementService.GetAnnouncementByTimer(RecieveAnnouncements);
}

function ShowAnnouncementInit() {
    if ($get("divAnnouncement") == undefined) {
        return;
    }
    Accela.ACA.Web.WebService.AnnouncementService.GetAnnouncementOfSession(PageAnnouncementInitial);
}

function UpdateAnnouncementStatus(announcementId) {
    Accela.ACA.Web.WebService.AnnouncementService.UpdateAnnouncementStatus(announcementId, RecieveAnnouncements);
}

function UpdateAnnouncementCount(announcementId) {
    Accela.ACA.Web.WebService.AnnouncementService.UpdateAnnouncementStatus(announcementId, SetAnnouncementInformation);
}

function RecieveAnnouncements(info) {
    PopupMessage(info);
    if (OnAnnouncementList.toLowerCase() == "true" && IsNeedPopupAnnouncement()) {
        RefreshAnnouncementList();
    }
}

function PopupMessage(info) {
    SetAnnouncementInformation(info);
    if (info != null && IsNeedPopupAnnouncement()) {
        $("#divAnnouncement").show();       
        SetDirection();
    }
}

function IsNeedPopupAnnouncement() {
    if ($("#winAnnouncement").is(':visible')) {
        return false;
    }
    return true;
}

function SetAnnouncementInformation(info) {
    if (info) {
        info = info.replace(/(<([^>]+)>)/gi, ""); //Strip the XML formatting the JSON comes wrapped in
        var json = JSON.parse(info);
        if (info != null && (json.IsDisplay) == "true") {
            $("#announcementCount").html(JsonDecode(json.AnnouncementCount));
            $("#announcementId").html(JsonDecode(json.AnnouncementId));
            $("#announcementContentPart").html("<a onmouseout=\"this.style.textDecoration ='none'\" onmousemove=\"this.style.textDecoration ='underline'\" onclick=\"ShowDetailWindowInPopup();\" href=\"javascript:void(0);\" class=\"SectionTextDecoration NotShowLoading\">" + JsonDecode(json.AnnouncementContentPart) + "</a>");
            SetOpenLinkInNewWindow("announcementContentPart");
            $("#announcementContentFull").html(JsonDecode(json.AnnouncementContentFull));
            $("#announcementContentTitle").html(JsonDecode(json.AnnouncementContentTitle));
            $("#divExpandAnnouncement").show();
            $("#spanAnnouncementCount").show();
        }
        else {
            ClearAnnouncement();
        }
    }
}

function RefreshAnnouncementList() {
    var c = "ctl00_PlaceHolderMain_AnnouncementListComponent_btnRefreshAnnouncementList";
    var annlist = document.getElementById(c);

    if (annlist != null) {
        var reg = /_/igm;
        var id = c.replace(reg, '$');
        __doPostBack(id, null);
        return true;
    }
    return false;
}

function ClearAnnouncement() {
    $("#announcementCount").html("0");
    $("#announcementContentPart").html("No Announcement.");
    $("#announcementId").html("");
    $("#divExpandAnnouncement").hide();
    $("#spanAnnouncementCount").hide();
    $("#divAnnouncement").hide();    
}

function MarkAsReadOfAnnouncement() { 
    var announcementId = $("#announcementId").html();    
    if (announcementId != "") {
        CloseAnnouncement(announcementId);
    }
    else {
        $("#divAnnouncement").hide();               
    }
}

function PageAnnouncementInitial(info) {
    PopupMessage(info);
}

function OpenAnnouncementAuto() {
    if ($("#divAnnouncement").is(':visible')) {
        $("#divAnnouncement").hide();    
    }
    else {
        $("#divAnnouncement").show();         
        SetDirection();
    }
}

function ShowDetailWindowInPopup() {
    if (typeof (SetNotAskForSPEAR) != 'undefined') {
        SetNotAskForSPEAR();
    }

    var annContentFull = $("#announcementContentFull").html();
    var annContentTitle = $("#announcementContentTitle").html();
    var announcementId = $("#announcementId").html();
    if (OnAnnouncementList.toLowerCase() == "true") {
        ShowDetailWindowInList(annContentFull, announcementId, annContentTitle, true);
    }
    else {
        CloseAnnouncement(announcementId);
        ShowDetailWindow(annContentFull, annContentTitle);
    }
}

function ShowDetailWindowInList(content, announcementId, title, isUpdateCount) {
    if (isUpdateCount) {
        UpdateAnnouncementCount(announcementId);
    }
    ShowDetailWindow(JsonDecode(content), JsonDecode(title));
}

function ShowDetailWindow(content, title) {
    $("#divAnnouncement").hide();
    $("#winAnnouncementContentAll").html(content);
    SetOpenLinkInNewWindow("winAnnouncementContentAll")
    $("#winAnnouncementContentTitle").html(title);
    $("#overlayAnnouncement").show();
    $("#winAnnouncement").show();       
    $("#winAnnouncement").focus();
}

function SetOpenLinkInNewWindow(objId) {
    var linkObjects = $("#" + objId + " a:not([href^='javascript:'])");
    linkObjects.attr("target", "_blank");
}

function CloseAnnouncement(announcementId) {
    $("#divAnnouncement").hide();     
    if (announcementId != "") {
        UpdateAnnouncementStatus(announcementId);
    }
    var annCount = $("#announcementCount").html(); 
    if (annCount == 1) {
        ClearAnnouncement();
    }
}

function SetDirection() {
    var divExpandAnnouncementIcon = $get("divExpandAnnouncement");
    var expandAnnouncementPos = getOffsetPos(divExpandAnnouncementIcon);
    var ptOffset = 12;
    var tl_space = getTLSpace(divExpandAnnouncementIcon, window);
    var br_space = getBRSpace(divExpandAnnouncementIcon, window);
    var l_space = tl_space.ls;
    var r_space = br_space.rs;
    var divAnnouncementObj = $get("divAnnouncement");
    var l_havespace = l_space >= divAnnouncementObj.offsetWidth;
    var r_havespace = r_space >= divAnnouncementObj.offsetWidth;

    if (l_havespace && !r_havespace) {
        divAnnouncementObj.style.left = expandAnnouncementPos.l - divAnnouncementObj.offsetWidth + ptOffset + 'px';
    }

    if (!l_havespace && r_havespace && $.global.isRTL) {
        divAnnouncementObj.style.left = expandAnnouncementPos.l  + 'px';
    }
}

function getOffsetPos(obj) {
    var top = obj.offsetTop;
    var left = obj.offsetLeft;

    var parentobj = obj.offsetParent;
    while (parentobj) {
        if (parentobj.offsetTop) {
            top += parentobj.offsetTop;
        }
        if (parentobj.offsetLeft) {
            left += parentobj.offsetLeft;
        }
        parentobj = parentobj.offsetParent;
    }

    var parentnode = obj.parentNode;
    while (parentnode && parentnode != parentobj && parentnode.tagName) {
        if (parentnode.tagName == 'BODY') {
            break;
        }
        if (parentnode.style.position.toLowerCase() == 'fixed') {
            continue;
        }
        if (parentnode.scrollTop) {
            top -= parentnode.scrollTop;
        }
        if (parentnode.scrollLeft) {
            left -= parentnode.scrollLeft;
        }
        parentnode = parentnode.parentNode;
    }
    return { t: top, l: left };
}

function getTLSpace(obj, win) {
    var rect = this.getRectPos(obj);
    var ts = rect.t;
    var ls = rect.l;

    while (win != win.parent) {
        if (isCrossDomain(win)) {
            break;
        }

        var iframeObjs = win.parent.document.getElementsByTagName('iframe');

        for (var i = 0; i < iframeObjs.length; i++) {
            var fra = iframeObjs.item(i);
            if (fra.contentWindow == win) {
                var fraRect = this.getRectPos(fra);
                if (fraRect.t < 0) {
                    ts += fraRect.t;
                }

                if (fraRect.l < 0) {
                    ls += fraRect.l;
                }
            }
            else {
                continue;
            }
        }

        win = win.parent;
    }

    return { ts: ts, ls: ls };
}

function getBRSpace(obj, win) {
    var tlspace = this.getTLSpace(obj, win);
    var bs = this.getVisualHeight(win.document) - (tlspace.ts + obj.offsetHeight);
    var rs = this.getVisualWidth(win.document) - (tlspace.ls + obj.offsetWidth);

    while (win != win.parent) {
        if (isCrossDomain(win)) {
            break;
        }

        var iframeObjs = win.parent.document.getElementsByTagName('iframe');

        for (var i = 0; i < iframeObjs.length; i++) {
            var fra = iframeObjs.item(i);
            if (fra.contentWindow == win) {
                var fraTLSpace = this.getTLSpace(fra, win.parent);
                var fraBRSpace = this.getBRSpace(fra, win.parent);
                if (fraTLSpace.ts < 0) {
                    bs += fraTLSpace.ts;
                }
                if (fraTLSpace.ls < 0) {
                    rs += fraTLSpace.ls;
                }
                if (fraBRSpace.bs < 0) {
                    bs += fraBRSpace.bs;
                }
                if (fraBRSpace.rs < 0) {
                    rs += fraBRSpace.rs;
                }
            }
            else {
                continue;
            }
        }

        win = win.parent;
    }

    return { bs: bs, rs: rs };
}

function getVisualHeight(doc) {
    var height = 0;
    height = doc.body.clientHeight;
    return height;
}

function getVisualWidth(doc) {
    var width = 0;
    if (this._hasDocType && (this._isFirefox || this._isSafari)) {
        width = doc.body.offsetWidth;
    }
    else {
        width = doc.body.clientWidth;
    }
    return width;
}
function getRectPos(obj) {
    var rect = obj.getBoundingClientRect();
    return { t: rect.top, l: rect.left };
}

//Move the layer when the mouse drag the window
$(document).ready(function () {
    var oWin = document.getElementById("winAnnouncement");
    var oLay = document.getElementById("overlayAnnouncement");
    var oAnnContent = document.getElementById("winAnnouncementContentAll");
    var oClose = document.getElementById("close");
    var oWinHeader = document.getElementById("announcementWindowHeader");
    var bDrag = false;
    var disX = 0;
    var disY = 0;

    oClose.onclick = function () {
        oLay.style.display = "none";
        oWin.style.display = "none";
        RefreshAnnouncementList();
        var $currentAnnCount = $("#announcementCount");
        if ($currentAnnCount && $currentAnnCount.html() != "0" && $currentAnnCount.html() != "") {
            $currentAnnCount.show();
        }
    };

    oClose.onmousedown = function (event) {
        (event || window.event).cancelBubble = true;
    };

    oWinHeader.onmousedown = function (event) {
        event = event || window.event;
        bDrag = true;
        disX = event.clientX - oWin.offsetLeft;
        disY = event.clientY - oWin.offsetTop;
        this.setCapture && this.setCapture();
        return false;
    };

    document.onmousemove = function (event) {
        if (!bDrag) return;
        event = event || window.event;
        var iL = event.clientX - disX;
        var iT = event.clientY - disY;
        var maxL = document.documentElement.clientWidth - oWin.offsetWidth;
        var maxT = document.documentElement.clientHeight - oWin.offsetHeight;
        iL = iL < 0 ? 0 : iL;
        iL = iL > maxL ? maxL : iL;
        iT = iT < 0 ? 0 : iT;
        iT = iT > maxT ? maxT : iT;

        oWin.style.marginTop = oWin.style.marginLeft = 0;
        oWin.style.left = iL + "px";
        oWin.style.top = iT + "px";
        return false;
    };

    document.onmouseup = window.onblur = oWinHeader.onlosecapture = function() {
        bDrag = false;
        oWinHeader.releaseCapture && oWinHeader.releaseCapture();
    };
});