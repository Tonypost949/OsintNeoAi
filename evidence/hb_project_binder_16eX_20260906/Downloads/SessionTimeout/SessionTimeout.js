/**
* <pre>
* 
*  Accela
*  File: SessionTimeout.js
* 
*  Accela, Inc.
*  Copyright (C): 2014-2015
* 
*  Description:
*  
*  Notes:
* $Id: SessionTimeout.js 185465 2014-11-04 ACHIEVO\grady.lu $.
*  Revision History
*  &lt;Date&gt;,    &lt;Who&gt;,    &lt;What&gt;
* </pre>
*/

(function ($) {
    var localLatestTime;
    var warningTime;
    var waitingTime;
    var expiryTime;
    var runningTime;
    var isOpened = false;
    var warnMsgTime = 0;
    var timeoutTimerId;
    var refreshWarnMsgId;
    var opts = {};

    function showClassicExpiryDialog() {
        // if the dialog has been opened, then without opening again.
        if (isOpened) {
            return;
        }

        warningTime = opts.WarningTime;
        //Set refresh warning message.
        refreshWarnMsgId = setInterval(refreshWarnTime, 1000 * 60);
        var content = opts.MsgWarn.replace("\{0\}", warningTime);
        warningTime--;

        var maktemp = '<div id="markdiag" class="ACA_MaskDiv"></div>';
        var tempstr = '<div class="divSessionTimeoutDialog" id="centerBox">' +
                        '<div class="boxTitle">' +
                            '<span id="expiry_title" class="titleText" aria-label="' + opts.WarnTitle + '">' + opts.WarnTitle + '</span><a id="btnClose" href="#" aria-label="' + opts.CloseTitle + '" class="btnClose tabbables ACA_Hide"><img alt="' + opts.CloseTitle + '" src="' + opts.UrlCloseImg + '" class="ACA_Dialog_Close_Image" /></a>' +
                        '</div>' +
                        '<div class="boxEntry">' +
                            '<div class="entryContent" id="expiry_message" tabindex="0" aria-label="' + content + '">' + content + '</div>' +
                        '</div>' +
                        '<div class="boxEntry">' +
                            '<div class="entryBtun">' +
                                '<input id="btnOk" type="button" class="tabbables" value="' + opts.BtnOK + '" />&nbsp;&nbsp;' +
                                '<input id="btnCancel" type="button" class="tabbables" value="' + opts.BtnCancel + '" />' +
                                '<input id="btnLogin" type="button" value="' + opts.BtnLogin + '" class="tabbables ACA_Hide" />' +
                            '</div>' +
                        '</div>' +
                      '</div>';
        $("body").append(maktemp);
        $("body").append(tempstr);
        initEventListener();

        //Set the status of dialog is opened.
        isOpened = true;

        //Adjust the dialog
        adjustDialog();

        function adjustDialog() {
            var popupMask = document.getElementById("markdiag");
            var container = document.getElementById("centerBox");

            ACAGlobal.Dialog.adjustPosition(container, popupMask, "em", opts);

            //Set the timeout dialog on the top level
            var timeoutDialog = $("#centerBox");
            var timeoutDialogMask = $("#markdiag");
            timeoutDialog.css('z-index', 9001);
            timeoutDialog.css('top', '40%');
            timeoutDialogMask.css('z-index', 9000);

            if (isFireFox()) {
                window.location.hash = "warningDialog";
            } else {
                $("#expiry_message").focus();
            }
        }
    }

    function refreshWarnTime() {

        if (warningTime <= 0) {
     
            if (timeoutTimerId) {
                clearInterval(timeoutTimerId);
            }

            if (refreshWarnMsgId !== null) {
                clearInterval(refreshWarnMsgId);
            }

            //Change title and conent;
            $("#expiry_title").text(opts.ExpiredTitle).attr("aria-label", opts.ExpiredTitle);
            $('#expiry_message').text(opts.MsgExpired).attr("aria-label", opts.MsgExpired).focus().attr("tabindex", "-1");

            $("#btnClose").removeClass("ACA_Hide");
            $("#btnLogin").removeClass("ACA_Hide");
            $("#btnOk").addClass("ACA_Hide");
            $("#btnCancel").addClass("ACA_Hide");

            userExpiredSignOut();

            $("#btnLogin").click(function () {
                isOpened = false;

                closeClassicDialog();
                redirectToHome();
            });

            $("#btnClose").click(function () {
                isOpened = false;
                redirectToHome();
            });
        }
        else {
            // refresh time message when user will be expired
            var newMessage = opts.MsgWarn.replace("\{0\}", warningTime);
            $('#expiry_message').text(newMessage).attr("aria-label", newMessage).focus();
            
            warningTime--;
        }
    }

    function initEventListener() {
        $("#btnOk").click(function () {
            // reset the default value for WarningTime
            $('#expiry_message').text(opts.MsgWarn.replace("\{0\}", opts.WarningTime));
            refreshSessionRequest();
            //Closing the Warning popup and resetiing the warnMesgTime
            closeClassicDialog();
            warnMsgTime = parseInt(opts.WarningTime) * 1000 * 60;
        });

        $("#btnCancel").click(function () {
            //Resetting warnMsgtime to 60 seconds to close Warn popup to completed signout process
            warnMsgTime = 60000;
            userExpiredSignOut();
            isOpened = false;
            opts.UrlWelcome;
            closeClassicDialog();
            redirectToHome();
        });

        $("#centerBox").keydown(function (event) {
            SetTabbableInDialog(event, "centerBox");
        });
    }

    function refreshSessionRequest() {
        $.ajax({
            type: "GET",
            url: opts.UrlLogic,
            data: "action=UPDATE_LASTEST_REQUEST_TIME",
            async: false,
            cache: false,
            success: function () {

                if (refreshWarnMsgId !== null) {
                    clearInterval(refreshWarnMsgId);
                }

                isOpened = false;

				 /* her - 661  . Comment out this code and using $('#WillTimeOutDialog').remove() instead of modal('hide')
                opts.IsNewUiTemplate ? $('#WillTimeOutDialog').modal("hide") : closeClassicDialog();		                opts.IsNewUiTemplate ? $('#WillTimeOutDialog').modal("hide") : closeClassicDialog();
                */
                opts.IsNewUiTemplate ? $('#WillTimeOutDialog').remove() : closeClassicDialog();
            }
        });
    }

    function closeClassicDialog() {
        if ($("#centerBox").length > 0) {
            $("#centerBox").remove();
        }

        if ($("#markdiag").length > 0) {
            $("#markdiag").remove();
        }

        if (refreshWarnMsgId !== null) {
            clearInterval(refreshWarnMsgId);
        }
    }

    function userExpiredSignOut() {
        $.ajax({
            type: 'GET',
            dataType: "json",
            async: false,
            url: opts.ApplicationRoot + "api/publicuser/sign-out",
            success: function () {                
            }
        });
    }

    function redirectToHome() {
        if (typeof (SetNotAsk) !== 'undefined') {
            SetNotAsk(true);
        }

        parent.window.location.href = opts.ApplicationRoot + "?culture=" + opts.Culture;
    }

    function timeoutTimer() {

        function preShowWarnDialog() {

            $.ajax({
                type: 'GET',
                dataType: "json",
                async: false,
                cache: false,
                url: opts.UrlLogic,
                data: "action=GET_LASTEST_REQUEST_TIME",
                success: function (result) {
                    var lastestRequestTime = parseInt(result);
                    showClassicExpiryDialog();
                }
            });
        }
        if (runningTime >= expiryTime && !isOpened && (warnMsgTime <= 0)) {
            preShowWarnDialog();
        } else {
            runningTime = runningTime + 1000;
            warnMsgTime = warnMsgTime - 1000;
        }
    };

    function getLatestRequestTime() {
        $.ajax({
            type: 'GET',
            dataType: "json",
            async: false,
            cache: false,
            url: opts.UrlLogic,
            data: "action=GET_LASTEST_REQUEST_TIME",
            success: function (result) {
                localLatestTime = parseInt(result);
                waitingTime = (opts.TimeoutTime - opts.WarningTime) * 1000 * 60;
                expiryTime = localLatestTime + waitingTime;
                /* 
                    Note: 
                    1: +3000 because preShowWarnDialog need to get the latest request time in service side. NetWork communication will spend some time.
                    2: Before the client on the service time out.
                */
                runningTime = localLatestTime + 3000;
                timeoutTimerId = setInterval(timeoutTimer, 1000);
            }
        });
    }

    $.fn.SessionTimeoutTimer = function (options) {
        opts = $.extend($.fn.SessionTimeoutTimer.defaults, options);
        if (timeoutTimerId !== null) {
            clearInterval(timeoutTimerId);
        }

        let userLoggedIn = false;
        fetch(opts.UrlUserStatus)
            .then(response => response.json())
            .then(response => {
                userLoggedIn = (response.toString().toLowerCase() === 'true');
                if (userLoggedIn) {
                    $.ajax({
                        type: 'GET',
                        async: false,
                        cache: false,
                        url: opts.UrlLogic,
                        data: "action=GET_CULTURE",
                        success: function (culture) {
                            opts.Culture = culture;
                            getLatestRequestTime();
                        }
                    });

                }
            });

    };

    $.fn.SessionTimeoutTimer.defaults = {
        width: 450,
        IsNewUiTemplate: false,
        TimeoutTime: 60,
        WarningTime: 5,
        WarnTitle: "Warning",
        ExpiredTitle: "Session Expired",
        CloseTitle: "Close",
        MsgWarn: "Your session will time out in {0} minute(s). Would you like to continue?",
        MsgExpired: "Your session has been timed out due to inactivity. Please click on Login to access your account.",
        MsgHelp: "Please press the Tab key to move the focus to the OK or Cancel button.",
        BtnOK: "OK",
        BtnLogin: "Login",
        BtnCancel: "Cancel",
        UrlWelcome: '/Welcome.aspx',
        UrlLogin: '/Login.aspx',
        UrlLogic: '/Handlers/SessionTimeOutHandler.ashx',
        ApplicationRoot: "/",
        Culture: "en-US"
    };

    $(document).on('mousemove keypress', function (e) {
        resetTheClock(e);
    });

    window.addEventListener("message", function (e) {
        resetTheClock(e);
    });

    function resetTheClock(e) {
        //Resetting session time when user not in idle state
        if (warnMsgTime <= 0) {
            expiryTime = runningTime + waitingTime;
        }
    }
})(jQuery); 
