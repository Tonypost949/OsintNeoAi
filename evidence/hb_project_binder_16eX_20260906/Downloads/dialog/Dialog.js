


var Class = {
    create: function() {
        return function () { this.initialize.apply(this, arguments); };
    }
};

var ACADialog = Class.create();
ACADialog.id = "dvACADialogLayer";
ACADialog.maskId = "dvACADialogLayerMask";
ACADialog.iframe_id = "ACADialogFrame";
ACADialog.close_id = "ACADialog_closebtn";
ACADialog.header_maskId = "dvACADialogHeaderMask";
ACADialog.isOpened = true;
ACADialog.GetOffsetLeft = function(){
    var offsetLeft=0;
    var elem = getParentDocument().getElementById("ACAFrame");
    while (elem) {
        offsetLeft += elem.offsetLeft;
        elem = elem.offsetParent;
    }
    return offsetLeft;
};

ACADialog.GetOffsetTop = function() {
    var offsetTop = 0;
    var elem = getParentDocument().getElementById("ACAFrame");
    while (elem) {
        offsetTop += elem.offsetTop;
        elem = elem.offsetParent;
    }
    return offsetTop;
};

ACADialog.getPopupTop = function () {
    return getPopupTop();
};

ACADialog.close = function () {
    ACADialog.isOpened = false;
    var mask = document.getElementById(ACADialog.maskId);

    if (mask)
    {
        document.body.removeChild(mask);
    }

    var el = document.getElementById(ACADialog.id);
    el.className = "ACA_Hide";

    if (ACADialog.focusObject) {
        var object = ACADialog.focusObject;

        if (typeof ACADialog.focusObject === 'string') {
            //get object by object ID.
            object = $get(ACADialog.focusObject);
        }

        if (object) {
            /*
            In order to keep the focus for section 508 compatibility,
            when user click the Actions menu in the attachment list to popped up the dialog,
            the clicked dom object will be passed to dialog object (ACADialog.focusObject).
            But attachment list behand in a iframe, and the iframe will be refreshed if some documents in pending status.
            So the foxusObject will be released, add try-catch logic to avoid the js error.
            */
            try {
                //After closing the dialog, focusing on the status messages for ADA complience issue
                //object.focus();
            }
            catch (e) {
                console.log(e);
            } 
        }

        ACADialog.focusObject = null;
    }

    var interval4CheckLoading = setInterval(function () {
        // Check whether show loading is running and whether new dialog open agained in specified intervals, if not then clear dialog iframe src.
        if (!$("#divGlobalLoading").is(":visible") && !ACADialog.isOpened) {
            var dialogIframe = $get(ACADialog.iframe_id);

            if (dialogIframe && !ACADialog.notDispose) {
                //Clear the iframe's src to trigger the contentWindow's unload event and to dispose the relational resources.
                dialogIframe.src = '';
            }

            clearInterval(interval4CheckLoading);
        }
    }, 500);

    if (window.location.href.indexOf('isPopup') > -1) {
        ACADialog.showHeaderMask(false);
    }

    var topWindow = window.document;
    try {
        var doc = parent.document;
        if (!doc)
            throw new Error('Unaccessible');
        else
            topWindow = parent.document;
        // accessible
    } catch (e) {
        // not accessible
    }

    if (topWindow.ACADialog == null || topWindow == window) {
        return;
    }

    // reset the height when close its child dialog popup.
    var parentDialog = $("#dvACADialogLayer").parent();
    if (parentDialog.length > 0) {
        parentDialog.css("height", "");
    }
};

ACADialog.hide = function () {
    window.document.getElementById(ACADialog.id).style.display = "none";
    window.document.getElementById(ACADialog.maskId).style.display = "none";
};

ACADialog.popup = function (opts) {
    ACADialog.focusObject = opts.objectTarget;
	ACADialog.isOpened = true;
    var popupMask = document.getElementById(ACADialog.maskId);

    if (popupMask === null) {
        popupMask = document.createElement('div');
        popupMask.id = ACADialog.maskId;
        document.body.appendChild(popupMask);

        var iframeInMask = document.createElement('iframe');
        iframeInMask.className = 'mask_iframe';
        iframeInMask.title = getText.masked_iframe_title;
        iframeInMask.innerHTML = getText.iframe_nonsrc_nonsupport_message;
        popupMask.appendChild(iframeInMask);
    }
    popupMask.className = "ACA_MaskDiv";

    var container = document.getElementById(ACADialog.id);
    if (container == null && !opts.parentId) {
        container = document.createElement("div");
        container.id = ACADialog.id;
        document.body.appendChild(container);
    }
    else if (container == null && opts.parentId ) {
        container = document.createElement("div");
        container.id = ACADialog.id;
        document.getElementById(opts.parentId).appendChild(container);
        document.getElementById(opts.parentId).style.display = "";
    }

    container.className = "ACA_Dialog";

    //Adjust the location for the container and popup mask;
    ACAGlobal.Dialog.adjustPosition(container, popupMask, "px", opts);

    if (isPopup) {
        ACADialog.showHeaderMask(true);
    }

    if (opts.url != null) {
        ACADialog._popupFrame(opts, container);
    }
    else {
        ACADialog._popupDiv(opts, container);
    }

    if (typeof iframeAutoFit == 'function') {
        //Expand parent iframe immediately.
        iframeAutoFit();
    }
};

ACADialog.popupWithForm = function (htmlForm) {
    var accelaAdapterPayDiv = document.getElementById("accelaAdapterPay");
    if (accelaAdapterPayDiv == null) {
        accelaAdapterPayDiv = document.createElement("div");
        accelaAdapterPayDiv.id = "accelaAdapterPay";
        document.body.appendChild(accelaAdapterPayDiv);
    }
    var paymentPageSubmitButton = document.getElementById("ctl00_PlaceHolderMain_Payment_lnkSubmitPaymentPage_container");
    if (paymentPageSubmitButton != null && paymentPageSubmitButton.style != null) {
        paymentPageSubmitButton.style.visibility = "hidden";
    }
    accelaAdapterPayDiv.innerHTML = htmlForm;
    if (document.getElementById("accelaAdapterPayIsForte")) {
        ShowLoading();
    }
};

ACADialog._popupDiv = function(opts, container) {
    var arr = [];
    arr.push("<a id='lnkBeginFocus' href='#' class='ACA_FLeft NotShowLoading' title='" + ACADialog.begin_alt + "' onkeydown='OverrideTabKey(event, true, \"" + ACADialog.close_id + "\")'>");
    arr.push("<img alt='' src='" + ACADialog.spacer_image_url + "' class='ACA_NoBorder' />");
    arr.push("</a>");
    arr.push("<div id='ACA_Dialog_Header'>");
    arr.push("<h1 class='ACA_Dialog_Title'><span id='ACA_Dialog_Title'>" + opts.title + "</span></h1>");
    arr.push("<div class='ACA_Dialog_Close_Div'>");
    arr.push("<a id='" + ACADialog.close_id + "' href='#' title='" + ACADialog.close_alt + "' onclick=\"ACADialog.close();return false;\" class=\"NotShowLoading\">");
    arr.push("<img alt='" + ACADialog.close_alt + "' class=\"ACA_Dialog_Close_Image\" src='" + ACADialog.close_image_url + "' />");
    arr.push("</a>");
    arr.push("</div>");
    arr.push("<div style='clear:both;height:0px'></div>");
    arr.push("</div>");
    arr.push("<div class='ACA_Dialog_Frame_DIV ACA_Dialog_Content_Padding'>");
    arr.push("<div id='ACA_Dialog_Content'>");
    var str = document.getElementById(opts.id).innerHTML;
    document.getElementById(opts.id).parentNode.removeChild(document.getElementById(opts.id));
    arr.push(str);
    arr.push("</div>");
    if (opts.buttonId != null) {
        arr.push("<div id='ACA_Dialog_Bottom'>");
        arr.push(document.getElementById(opts.buttonId).innerHTML);
        arr.push("</div>");
    }

    arr.push("</div>");
    arr.push("<a id='lnkEndFocus' class='NotShowLoading' href='#' title='" + ACADialog.end_alt + "' onkeydown='OverrideTabKey(event, false, \"lnkBeginFocus\")'>");
    arr.push("<img alt='' src='" + ACADialog.spacer_image_url + "' class='ACA_NoBorder' />");
    arr.push("</a>");
    container.innerHTML = arr.join('\n');
};

ACADialog._popupFrame = function (opts, container) {
    var scrollString = opts.scroll == false ? "scrolling = 'no'" : "scrolling = 'auto'";

    var arr = [];
    arr.push("<a id='lnkBeginFocus' href='#' class='ACA_FLeft NotShowLoading' title='" + ACADialog.begin_alt + "' onkeydown='OverrideTabKey(event, true, \"" + ACADialog.close_id + "\")'>");
    arr.push("<img alt='' src='" + ACADialog.spacer_image_url + "' class='ACA_NoBorder' />");
    arr.push("</a>");
    arr.push("<div id='ACA_Dialog_Header'>");
    arr.push("<h1 class='ACA_Dialog_Title'><span id='ACA_Dialog_Title'></span></h1>");
    arr.push("<div class='ACA_Dialog_Close_Div'>");
    arr.push("<a id='" + ACADialog.close_id + "' href='#' title='" + ACADialog.close_alt + "' onclick=\"ACADialog.close();return false;\" class=\"NotShowLoading\">");
    arr.push("<img alt='" + ACADialog.close_alt + "' class=\"ACA_Dialog_Close_Image\" src='" + ACADialog.close_image_url + "' />");
    arr.push("</a>");
    arr.push("</div>");
    arr.push("<div class='ACA_MaskDiv ACA_Hide' id='ACA_Dialog_Header_Mask'></div>");
    arr.push("<div style='clear:both;height:0px'></div>");
    arr.push("</div>");
    arr.push("<div id='ACA_Dialog_Frame_DIV' class='ACA_Dialog_Frame_DIV'>");
    arr.push("<iframe class='ACA_Dialog_Frame' id='" + ACADialog.iframe_id + "' name='" + ACADialog.iframe_id + "' frameborder='0' style='min-height: " + opts.height + "px; width:100%' " + scrollString + " title='" + ACADialog.iframe_title + "'></iframe>");
    arr.push("</div>");
    arr.push("<a id='lnkEndFocus' class='NotShowLoading' href='#' title='" + ACADialog.end_alt + "' onkeydown='OverrideTabKey(event, false, \"lnkBeginFocus\")'>");
    arr.push("<img alt='' src='" + ACADialog.spacer_image_url + "' class='ACA_NoBorder' />");
    arr.push("</a>");
    container.innerHTML = arr.join('\n');
    // show loading
    ProcessLoadingUtil.NotNeedHide = true;
    showDialogLoading();
    var iframe = window.document.getElementById(ACADialog.iframe_id);

    // the process loading need this argument to judge it is popup or not.
    if (opts.url.indexOf('isPopup') == -1) {
        var urlSplit = '?';

        if (opts.url.indexOf('?') != -1) {
            urlSplit = '&';
        }

        opts.url = opts.url + urlSplit + 'isPopup=Y';
    }

    //transfer agency code to popup iframe page to resolve not get sub agency code.
    var regex = /[&|?]agencyCode/i;

    if (!regex.test(opts.url)) {
        urlSplit = '?';

        if (opts.url.indexOf('?') != -1) {
            urlSplit = '&';
        }

        opts.url = opts.url + urlSplit + 'agencyCode=' + ACADialog.agencyCode;
    }

    iframe.src = opts.url;
    iframe.innerHTML = getText.iframe_nonsupport_message.replace(/\{0\}/g, opts.url);
    var p = new ProcessLoading();

    if (!/*@cc_on!@*/0) {
        //if not IE 
        iframe.onload = function () {
            ProcessLoadingUtil.NotNeedHide = false;
            p.hideLoading();
            ACADialog.setFocus();
        };
    } else {
        iframe.onreadystatechange = function () {
            if (iframe.readyState == "complete") {
                ProcessLoadingUtil.NotNeedHide = false;
                p.hideLoading();
                ACADialog.setFocus();
            }
        };
    }
};

ACADialog.setTitle = function (title) {
	//sets Iframe title for screenreaders
	var dialogTitle = title + " Dialog";
	document.getElementById(ACADialog.iframe_id).title = dialogTitle;
	ACADialog.iframe_title = dialogTitle; 

	var t = document.getElementById("ACA_Dialog_Title"); 
    if (t != null) {
		t.innerHTML = title;
    }
};

ACADialog.showHeaderMask = function (display) {

    var topWindow = window.document;
    try {
        var doc = parent.document;
        if (!doc)
            throw new Error('Unaccessible');
        else
            topWindow = parent.document;
        // accessible
    } catch (e) {
        // not accessible
    }
    var divHeader = $("#ACA_Dialog_Header", topWindow);

    if (divHeader.length > 0) {
        var headerMask = $("#" + ACADialog.header_maskId, topWindow);

        if (headerMask.length == 0) {
            headerMask = $("<div id='" + ACADialog.header_maskId + "'/>", topWindow);

            headerMask.addClass("ACA_MaskDiv_Header").height(divHeader.height()).appendTo(divHeader);
        }

        if (display) {
            headerMask.show();
        }
        else {
            headerMask.hide();
        }
    }
};

ACADialog.fixHeight = function () {
    var dialogContainer = $("#" + ACADialog.id);
    var dvHeader = $("#ACA_Dialog_Header");
    var dialgIframe = $("#ACADialogFrame");
    var height = dialogContainer.height() - dvHeader.height();

    if ($.detectedBrowser.mozilla) {
        height -= 21;
    }
    else if ($.detectedBrowser.safari) {
        height -= 30;
    }
    else if (!$.detectedBrowser.msie) {
        height -= 35;
    }
    dialgIframe.height(height);
};

ACADialog.setInstruction = function(instruction) {
    var dialogInstruction = document.getElementById("ACA_Dialog_instruction");
    if (dialogInstruction != null) {
        dialogInstruction.innerHTML = instruction;    
    }
};

ACADialog.autoHeight = function (opts) {
    var ifrm = document.getElementById("ACADialogFrame");
    var dvDialog = document.getElementById("dvACADialogLayer");
    var dialogHeader = document.getElementById("ACA_Dialog_Header");
    var dialogMask = document.getElementById("dvACADialogLayerMask");

    var bHeight = ifrm.contentWindow.document.body.scrollHeight;
    var dHeight = ifrm.contentWindow.document.documentElement.scrollHeight;
    var height = Math.min(bHeight, dHeight);

    if (opts != null) {
        if (opts.maxHeight != null && height > opts.maxHeight && window.location.href.indexOf('isPopup') < 0) {
            height = opts.maxHeight;
        }

        if (opts.minHeight != null && height < opts.minHeight) {
            height = opts.minHeight;
        }

        if (opts.isAutoHeight && typeof (opts.maxHeight) == "undefined") {
            var iframeObj = $("#" + ACADialog.iframe_id)[0];

            if (typeof iframeObj != "undefined") {
                if (iframeObj.attributes["scrolling"].value != "no") {
                    iframeObj.setAttribute("scrolling", "auto");
                }
            }
        }
    }

    // set the max height if the popup page has sub popup page.
    var childPopupBox = $(ifrm.contentWindow.document).find(".PopUpDlg");
    $(childPopupBox).each(function () {
        if ($(this).is(":visible")) {
            var childHeight = $(this).position().top + $(this).height();

            if (childHeight > height) {
                height = childHeight + $("#ACA_Dialog_Header").height();
            }

            // at a time there is only one popup layer, so break.
            return false;
        }
    });

    if ($.detectedBrowser.mozilla) {
        height = parseInt(height) + 10;
    }

    if ($.detectedBrowser.safari) {
        height = parseInt(height) + 10;
    }

    dvheight = parseInt(height) + parseInt(dialogHeader.scrollHeight);
    dvDialog.style.height = dvheight + "px";
    dvDialog.style.minHeight = dvheight + "px";

    // To resolved the popup dialog shake up and down issue, if dialog do not have the vertical scroll bar, it needn't to fix the dialog's top.
    if (!$.detectedBrowser.msie && ($(ifrm.contentWindow.document).height() === $(ifrm.contentWindow).height())) {
        var parentIfrm = getParentDocument().getElementById("ACAFrame");

        if (parentIfrm) {
            var currentHeight = $(parentIfrm.contentWindow.document).height();

            if (!isFireFox()) {
                parentIfrm.style.height = currentHeight;
            }
            else {
                parentIfrm.height = currentHeight;
            }
        }

        return;
    }

    ifrm.style.height = height + "px";
    var elem = getParentDocument().getElementById("ACAFrame");

    if (elem && dvDialog.top) {
        if (elem.clientHeight < (dvDialog.top + dvheight + 5)) {
            var top = elem.clientHeight - dvheight - 5;
            if (top < 10) {
                top = 10;
            }

            dvDialog.style.top = top + "px";
            dvDialog.top = top;
        }
    }

    if (window.location.href.indexOf('isPopup') > -1 && dvDialog.top && dialogMask) {
        var parentDialogHeight = getOwnIframe(window).contentWindow.document.body.scrollHeight;
        var dialogTop = dvDialog.top;
        var parentMaskHeight = Math.max(parentDialogHeight, parseInt(dvheight) + parseInt(dialogTop));
        dialogMask.style.height = parentMaskHeight + "px";

        var parentDialog = dvDialog.parentElement;
        if (parentDialog) {
            var parentHeight = $(parentDialog).height();

            if ($.detectedBrowser.safari) {
                parentMaskHeight = parentMaskHeight - 4;
            }
            
            if (parentHeight < parentMaskHeight) {
                parentDialog.style.height = parentMaskHeight + "px";
            }
        }
    }
};

ACADialog.fixWidth = function (width) {
    var viewportData = getTopAccesibleFrameViewport();
    var dvDialog = document.getElementById("dvACADialogLayer");

    if (width <= viewportData.width) {
        dvDialog.style.width = width + "px";
    }
    else {
        dvDialog.style.width = "100%"; //set to width of container if requested size is bigger than the viewpoet.
    }
};

ACADialog.fix = function () {
    ACADialog.setTitle("");
    ACADialog.setInstruction("");
    ACADialog.fixHeight();
};

ACADialog.autoFixTop = function () {
    var viewportData = getTopAccesibleFrameViewport();
    var win = viewportData.winRef;

    var ifra = getOwnIframe(win);
    var isPopup = win.location.href.indexOf('isPopup') > -1;

    if (isPopup && ifra) {
        win = ifra.contentWindow;
    }

    var dheight = $("#" + ACADialog.iframe_id).height();
    var clientHeight;
    var scrollTop;

    if (viewportData.ref.compatMode == "BackCompat") {
        clientHeight = viewportData.ref.body.clientHeight;
        scrollTop = viewportData.ref.body.scrollTop;
    } else {
        clientHeight = viewportData.ref.documentElement.clientHeight;
        //Chrome & Opera need get body.scrollTop.
        scrollTop = viewportData.ref.documentElement.scrollTop || viewportData.ref.body.scrollTop;
    }

    var dTop = scrollTop + (clientHeight - dheight) / 2 - ACADialog.GetOffsetTop();

    if (dTop < 10) {
        dTop = 10;
    }

    if (isPopup) {
        var screenHeight = window.screen.height;
        if (screenHeight >= clientHeight) {
            var dialogHeader = getParentDocument().getElementById("ACA_Dialog_Header");
            dTop = dTop - parseInt(dialogHeader.scrollHeight) / 2;
        }
        else{
            dTop = getPopupTop();
        }
    }

    var container = document.getElementById(ACADialog.id);
    container.style.top = dTop + "px";
    container.top = dTop;
};

ACADialog.autoFixLeft = function() {
    var dwidth = $("#" + ACADialog.id).width();
    var containter = document.getElementById(ACADialog.id);
    containter.style.left = parseInt(($(document.body).width() - dwidth) / 2) + "px";
};

ACADialog.setFocus = function() {
    var containterHeader = document.getElementById("lnkBeginFocus");
    if ($(containterHeader).is(':visible')) {
        containterHeader.focus();
    }
};

function showDialogLoading(title) {
    var p = new ProcessLoading();
    p.createLoading();

    if (typeof title != "undefined" && title != "") {
        p.setTitle(title);
    }

    var loading = $('#' + p.loadingId);
    var loadingMask = $('#' + p.loadingMaskId);
    var loadingImg = $('#' + p.loadingImgId);

    if ($.exists(loading)) {
        var popupBox = $('#' + ACADialog.id);

        // adjust the position
        var left = (popupBox.width() - loading.width()) / 2 + parseInt(popupBox.get(0).offsetLeft) + 'px';
        var top = (popupBox.height() - loading.height()) / 2 + parseInt(popupBox.get(0).offsetTop) + 'px';
        var boxZindex = popupBox.css('z-index');

        loading.css('left', left).css('top', top);
        loading.css('z-index', parseInt(boxZindex) + 2);

        loading.show();
        loading.corner();
    }

    if ($.exists(loadingMask)) {
        loadingMask.css('z-index', parseInt(boxZindex) + 1);
        loadingMask.show();

        if (typeof iframeAutoFit == 'function') {
            //Expand parent iframe immediately.
            iframeAutoFit();
        }

        var ifra = getOwnIframe(window);

        if (ifra && ifra.offsetHeight) {
            loadingMask.height(ifra.offsetHeight);
        }
        else {
            bodyHeight = $('body').height();
            loadingMask.height(bodyHeight);
        }
    }

    if ($.exists(loadingImg)){
        loadingImg.focus();
        loadingImg.keydown(function (event) {
            var ev = event || window.event;
            if (ev.keyCode == 9) {
                return false;
            }
        });
    }
}

function getPopupTop() {
    var viewportData = getTopAccesibleFrameViewport();
    var win = viewportData.ref.defaultView;

    var ifra = getOwnIframe(win);
    var isPopup = win.location.href.indexOf('isPopup') > -1;

    if (isPopup && ifra) {
        win = win.contentWindow;
    }

    var dheight = $("#" + ACADialog.iframe_id).height();
    var clientHeight;

    if (win.document.compatMode == "BackCompat") {
        clientHeight = win.document.body.clientHeight;
    } else {
        clientHeight = win.document.documentElement.clientHeight;
    }   
    
    var dom = document;
    var p = parent; 
    var pTop = document.compatMode == "BackCompat" ? document.body.scrollTop : document.documentElement.scrollTop || document.body.scrollTop;

    do {
        var parentPopupScrollTop = 0;
        var currentPopupOffsetTop = 0;
        var acaDialog = $(dom).find("#dvACADialogLayer");

        if ($.exists(acaDialog) && acaDialog[0]) {
            currentPopupOffsetTop = acaDialog[0].offsetTop;
        }

        if (dom !== win.document) {
            dom = p.document;
            p = p.parent;
            parentPopupScrollTop = dom.compatMode === "BackCompat" ? dom.body.scrollTop : dom.documentElement.scrollTop || dom.body.scrollTop;
        }

        pTop += parentPopupScrollTop > currentPopupOffsetTop ? parentPopupScrollTop - currentPopupOffsetTop : 0;
    } while (dom != win.document);

    var dialogHeader = $("#ACA_Dialog_Header");
        
    if ($.exists(dialogHeader)) {
        dheight += dialogHeader.height();
    }

    var overflowHeight = clientHeight - dheight - pTop;
        
    if (overflowHeight >= 0) {
        pTop = pTop + 20;
    } else {
        pTop = pTop + overflowHeight - 20;
    }
        
    return pTop;
}

/* export for modern javscript use */
if (typeof exports !== 'undefined') {
    exports.ACADialog = ACADialog;
    exports.getPopupTop = getPopupTop;
}