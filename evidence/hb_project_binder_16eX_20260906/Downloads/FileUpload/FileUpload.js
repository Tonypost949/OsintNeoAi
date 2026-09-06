/**
* <pre>
* 
*  Accela
*  File: FileUpload.js
* 
*  Accela, Inc.
*  Copyright (C): 2014
* 
*  Description:
*  Upload file in html5
*  Notes:
*  $Id: FileUpload.js 
*  
*  &lt;Date&gt;,    &lt;Who&gt;,    &lt;What&gt;
*  07/08/2014     	 Leeson.li				Initial.
* </pre>
*/

var fileUploaderCollection = {};

var FileUploader = function () {
    this.register4UploadController = register4UploadController;             //register control
    this.initFileUploadControl = initFileUploadControl;                     //init
    this.selectCompleted = selectCompleted;
    this.startUpload = startUpload;
    this.removeSingleFile = removeSingleFile;
    this.removeAllFiles = removeAllFiles;

    this.selectCompletedCallBack = null;                                    //selectCompleted event callback
    this.startUploadCallBack = null;                                        //startUpload event callback
    this.allFilesFinishedCallBack = null;                                   //allFileFinished event callback
    this.singleFinishCallBack = null;                                       //singleFileFinished event callback
    this.removeSingleCallBack = null;                                       //removeSingleFile event callback
    this.removeAllCallBack = null;                                          //removeAllFiles event callback

    this.filesArray = [];                                                   //the all files array(include file content)
    this.fileInfoArray = [];                                                //all fileInfo array
    this.parentContainerId = "";                                            //the container includes the button
    this.fileInputObjId = "";                                               //the real file input object 
    this.isAllFinished = false;                                              //whether all file have finished
    
    var errorMsgId = "";                                                    //the error message container id.
    var disallowedFileTypes = "";                                           //upload disallowed file types.
    var maxFileSizeByByte = 20 * 1024 * 1024;                               //max allowed file size by byte
    var typeErrorPattern = "";                                              //type error message
    var sizeErrorPattern = "";                                              //size error message
    var zeroSizeErrorPattern = "";                                          //zero file error message
    var agencyCode = "";                                                    //agencyCode for resubmit
    var documentNo = "";                                                    //document no for resubmit
    var browserNotSupportMsg = "Your browser does not support Html5.";
    var uploadCommonErrorMsg = "";                                          // default error message
    var timeoutErrorMsg = "An error occured while uploading your file(s). Please try uploading one file at a time or using a faster internet connection.";
    var fileUploadTimeout = 3600;                                           //in seconds

    var fileReaderArray = {};                                               //the file readers used in the file uploading.
    var failedUploads = [];                                                 //array of files that failed during uploading
    
    function register4UploadController(containerId, labelText, isMultipleUpload, cssClass) {
        var html = FileUploadUtil.getUploadControlHtml(containerId, labelText, isMultipleUpload, cssClass);
        $('#' + containerId).html(html);

        this.parentContainerId = containerId;
        this.fileInputObjId = 'fileInput_' + containerId;
        fileUploaderCollection[containerId] = this;
    }

    function initFileUploadControl(errorMsgSpanId, disallowedTypes, maxSizeByByte, typeErrorMsgPattern, sizeErrorMsgPattern, zeroErrorMsgPattern,
                               parentAgencyCode, parentDocumentNo, browserNotSupportMessage, uploadCommonErrorMessage, timeoutErrorMessage) {
        errorMsgId = errorMsgSpanId;
        disallowedFileTypes = disallowedTypes;
        maxFileSizeByByte = maxSizeByByte;
        typeErrorPattern = typeErrorMsgPattern;
        sizeErrorPattern = sizeErrorMsgPattern;
        zeroSizeErrorPattern = zeroErrorMsgPattern;
        agencyCode = parentAgencyCode;
        documentNo = parentDocumentNo;
        browserNotSupportMsg = browserNotSupportMessage;
        uploadCommonErrorMsg = uploadCommonErrorMessage;

        if (timeoutErrorMessage.length)
            timeoutErrorMsg = timeoutErrorMessage;

        FileUploadUtil.isSupportedBrowser(errorMsgId, browserNotSupportMsg);
    }

    function selectCompleted() {
        var fileInputObj = $('#' + this.fileInputObjId)[0];
        if (fileInputObj.files && fileInputObj.files.length > 0) {

            //  only used for Resubmit link in attachment list iframe.
            var errorContainer = !$.exists('#' + errorMsgId) ? $('#' + errorMsgId, parent.document) : $('#' + errorMsgId);

            if (errorContainer) {
                if (!hasFailedUploads())
                    errorContainer.html('');
                else
                    return false;
            }
            
            var allowedFiles = isPassValidation(fileInputObj.files);

            if (allowedFiles.length == 0) {
                FileUploadUtil.clearFileInput(fileInputObj);
                return false;
            }

            var newFileinfoArray = [];
            for (var i = 0; i < allowedFiles.length; i++) {
                var userFile = allowedFiles[i];
                this.filesArray.push(userFile);
                var fileInfo = convertUserFileToFileInfo(userFile);
                this.fileInfoArray.push(fileInfo);
                newFileinfoArray.push(fileInfo);
            }

            if (newFileinfoArray.length > 0) {
                if (typeof (this.selectCompletedCallBack) != "undefined" && this.selectCompletedCallBack != null) {
                    //the second parameter especailly for cross iframe issue, need transform uploader name.
                    this.selectCompletedCallBack(window.Sys.Serialization.JavaScriptSerializer.serialize(newFileinfoArray), "upload_" + this.parentContainerId);
                }
            }

            FileUploadUtil.clearFileInput(fileInputObj);
        }
    }

    function startUpload(fileId, uploadUrl, progressBarContainer) {
        if (this.fileInfoArray.length == 0) {
            return;
        }

        this.isAllFinished = false;

        for (var i = 0; i < this.fileInfoArray.length; i++) {
            if (this.fileInfoArray[i].FileId == fileId) {
                uploadSingleFile(this.filesArray[i], this.fileInfoArray[i], uploadUrl, progressBarContainer, this.parentContainerId);
                break;
            }
        }

        if (this.startUploadCallBack != null && typeof (this.startUploadCallBack) != "undefined") {
            this.startUploadCallBack();
        }
    }

    function removeSingleFile(fileId) {
        var isUploading = false;

        for (var i = 0; i < this.fileInfoArray.length; i++) {
            if (this.fileInfoArray[i].FileId == fileId) {

                if (this.fileInfoArray[i].StateString != "Finished") {
                    isUploading = true;
                }

                Array.remove(this.filesArray, this.filesArray[i]);
                Array.remove(this.fileInfoArray, this.fileInfoArray[i]);

                if (typeof (fileReaderArray[fileId]) != "undefined") {
                    var fileReaderAbort = FileReader.abort || FileReader.prototype.abort;
                    fileReaderAbort.call(fileReaderArray[fileId]);

                    delete fileReaderArray[fileId];
                }

                break;
            }
        }

        if (typeof (this.removeSingleCallBack) != "undefined" && this.removeSingleCallBack != null) {
            this.removeSingleCallBack();
        }

        //if all file has removed, execute removeAllCallBack
        if (this.fileInfoArray.length == 0 && this.removeAllCallBack) {
            this.removeAllCallBack();
        }

        //if the file removed is uploading, need check whether all file is finished.
        if (isUploading) {
            var isAllFileFinished = FileUploadUtil.isAllFileFinished(this.fileInfoArray);

            if (isAllFileFinished && this.allFilesFinishedCallBack) {
                this.allFilesFinishedCallBack();
            }
        }
    }

    function removeAllFiles() {
        this.filesArray = [];
        this.fileInfoArray = [];
        fileReaderArray = {};

        if (typeof (this.removeAllCallBack) != "undefined" && this.removeAllCallBack != null) {
            this.removeAllCallBack();
        }
    }

    //it prompt error message, some correct file continute to upload.
    function isPassValidation(files) {
        var errorMessage = "";
        var disallowedTypes = disallowedFileTypes;
        var disallowedTypeArray = disallowedTypes.split(";");
        var limitSize = maxFileSizeByByte;
        var typeErrorCount = 0;
        var typeErrorContent = "";
        var sizeErrorCount = 0;
        var sizeErrorContent = "";
        var zeroSizeErrorCount = 0;
        var zeroSizeErrorContent = "";
        var allowedFiles = [];

        if (disallowedTypeArray.length > 0) {
            for (var k = 0; k < disallowedTypeArray.length; k++) {
                if (String.IsNullOrEmpty(disallowedTypeArray[k])) {
                    continue;
                }

                if (disallowedTypeArray[k].indexOf(".") != 0) {
                    disallowedTypeArray[k] = "." + disallowedTypeArray[k];
                }
            }
        }

        for (var j = 0; j < files.length; j++) {
            var isDisallowed = false;
            var fileName = files[j].name;

            if (disallowedTypeArray.length > 0) {

                var dotIndex = fileName.lastIndexOf(".");

                if (dotIndex > -1) {
                    var suffix = fileName.substring(dotIndex, fileName.length).toLowerCase();

                    if (disallowedTypeArray.contains(suffix)) {
                        isDisallowed = true;
                        typeErrorCount++;
                        typeErrorContent += fileName + "; ";
                    }
                }
            }

            if (files[j].size == 0 && !isDisallowed) {
                isDisallowed = true;
                zeroSizeErrorCount++;
                zeroSizeErrorContent += fileName + "; ";
            }

            if (!isDisallowed && parseInt(limitSize) > 0 && files[j].size > parseInt(limitSize)) {
                isDisallowed = true;
                sizeErrorCount++;
                sizeErrorContent += fileName + "; ";
            }

            if (!isDisallowed) {
                allowedFiles.push(files[j]);
            }
        }

        if (typeErrorCount > 0) {
            var typeErrorMsgPattern = typeErrorPattern;
            errorMessage = String.format(typeErrorMsgPattern, typeErrorCount, typeErrorContent);
            errorMessage += "<br/>";
        }

        if (sizeErrorCount > 0) {
            var sizeErrorMsgPattern = sizeErrorPattern;
            errorMessage += String.format(sizeErrorMsgPattern, sizeErrorCount, sizeErrorContent);
            errorMessage += "<br/>";
        }

        if (zeroSizeErrorCount > 0) {

            var zeroSizeErrorMsgPattern = zeroSizeErrorPattern;
            errorMessage += String.format(zeroSizeErrorMsgPattern, zeroSizeErrorCount, zeroSizeErrorContent);
            errorMessage += "<br/>";
        }

        if (errorMessage.length == 0) {
            return allowedFiles;
        }

        // used in attachment list iframe for Resubmit link button.
        if (!$.exists('#' + errorMsgId)) {
            parent.showMessage(errorMsgId, errorMessage, "Error", true, 1, true);
        }
        else {
            showMessage(errorMsgId, errorMessage, "Error", true, 1, true);
        }

        return allowedFiles;
    }

    //send XHR request with the file. timeout is in seconds
    function sendFileAsXHRRequest(xhr, url, data, timeout, onTimeout) {
        xhr.open("POST", url, true);

        if (timeout) {
            xhr.timeout = timeout * 1000;//convert it to milliseconds
            xhr.ontimeout = function (evt) {
                if (onTimeout)
                    onTimeout();
            };
        }

        xhr.send(data);
    }

    function uploadSingleFile(file, fileInfo, uploadUrl, progressBarContainer, containerId) {
        var errorContainerId = errorMsgId;
        var commonErrorMsg = uploadCommonErrorMsg;

        //check if browser supports FormData
        if (typeof (window.FormData) == 'undefined') {
            showMessage(errorContainerId, browserNotSupportMsg, "Error", true, 1, true);
            return;
        }

        var xhr = new XMLHttpRequest();
        var timeout = fileUploadTimeout;//set it to 1 hour in case of very large files or very slow connections.

        xhr.upload.addEventListener("error", function (evt) {
            processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId);
        }, false);

        xhr.addEventListener("abort", function (evt) {
            processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId);
        }, false);

        xhr.upload.addEventListener("progress", function (evt) {
            if (hasFailedUploads())
                xhr.abort();
            else
                streamUploadProgress(evt, progressBarContainer);
        }, false);

        var onTimeout = function () {
            processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId, true);
        };
        
        xhr.onreadystatechange = function (evt) {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    var finalXhr = new XMLHttpRequest();

                    finalXhr.upload.addEventListener("error", function (evt) {
                        processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId);
                    }, false);

                    finalXhr.addEventListener("abort", function (evt) {
                        processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId);
                    }, false);

                    finalXhr.onreadystatechange = function (finalXhrEvt) {
                        if (finalXhr.readyState == 4) {
                            if (finalXhr.status == 200) {
                                FileUploadUtil.updateProgressBar(progressBarContainer, 100);

                                executeSingleFileFinished(containerId, fileInfo.FileId);
                            }
                            else {
                                processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId);
                            }
                        }
                    }

                    var finalFormData = new FormData();
                    timeout = 30;//in seconds. set it as 30 seconds for the final request

                    finalFormData.append("fileName", file.name);
                    finalFormData.append("fileId", fileInfo.FileId);
                    finalFormData.append("responseId", xhr.responseText);

                    url = uploadUrl + "/finish";

                    sendFileAsXHRRequest(finalXhr, url, finalFormData, timeout, onTimeout);
                }
                else {
                    if (xhr.status != 0)
                        processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId);
                }
            }
        }

        var url = uploadUrl + "/post";

        var pFormData = new FormData();      

        pFormData.append("file", file);
        sendFileAsXHRRequest(xhr, url, pFormData, timeout, onTimeout);
    }

    //updates file uploading progress
    function streamUploadProgress(evt, progressBarContainer) {
        if (evt.lengthComputable) {
            var percentComplete = Math.round(evt.loaded * 100 / evt.total);

            if (percentComplete < 100)
                FileUploadUtil.updateProgressBar(progressBarContainer, percentComplete);
        }
        else {
            console.error('Unable to compute file upload progress');
        }
    }

    //adds fileId to the array if uploading failed
    function processSingleFileFailed(fileInfo, containerId, progressBarContainer, errorContainerId, isTimeout) {
        //add file id to the array of failed uploads
        if (failedUploads)
            failedUploads.push(fileInfo.FileId);

        if (fileUploaderCollection
            && fileUploaderCollection[containerId]
            && fileUploaderCollection[containerId].fileInfoArray) {
            var filesArray = fileUploaderCollection[containerId].fileInfoArray;

            var matchCount = filesArray.filter(function (el) {
                return el.FileId === fileInfo.FileId;
            });

            if (matchCount > 0) {
                filesArray[idx].StateString = 'Failed';
            }
        }

        //Continue button should be disabled
        DisableFinishButton(true);

        //update progress for the failed file to 0
        FileUploadUtil.updateProgressBar(progressBarContainer, 0);
        executeSingleFileFinished(containerId, fileInfo.FileId);

        //mark file row as failed
        var fileRow = $('#' + fileInfo.FileId).parent();

        if (fileRow) {
            fileRow.addClass('fileWarning');
        }

        //display error message
        if (isTimeout)
            showMessage(errorContainerId, timeoutErrorMsg, "Error", true, 1, true);
        else
            showMessage(errorContainerId, uploadCommonErrorMsg, "Error", true, 1, true);
    }

    //returns true if any of the files failed uploading
    function hasFailedUploads() {
        return failedUploads && failedUploads.length;
    }

    //when upload single file finished
    function executeSingleFileFinished(key, fileId) {
        var fileUploader = fileUploaderCollection[key];
        if (typeof (fileUploader) == "undefined" || fileUploader == null && fileUploader.fileInfoArray.length == 0) {
            return;
        }

        var count = 0;

        for (var i = 0; i < fileUploader.fileInfoArray.length; i++) {

            if (fileUploader.fileInfoArray[i].FileId == fileId && fileUploader.fileInfoArray[i].StateString != "Finished" && fileUploader.fileInfoArray[i].StateString != "Failed") {
                fileUploader.fileInfoArray[i].StateString = "Finished";

                if (fileUploader.singleFinishCallBack != null && typeof (fileUploader.singleFinishCallBack) != "undefined") {
                    fileUploader.singleFinishCallBack(fileUploader.fileInfoArray[i]);
                }
            }

            if (fileUploader.fileInfoArray[i].StateString == "Finished") {
                count++;
            }
        }

        if (count == fileUploader.fileInfoArray.length && !fileUploader.isAllFinished) {
            fileUploader.isAllFinished = true;

            if (fileUploader.allFilesFinishedCallBack != null && typeof (fileUploader.allFilesFinishedCallBack) != "undefined") {
                fileUploader.allFilesFinishedCallBack();
            }
        }
    }

    //Convert IUserFile defined in Silverlight to FileUploadInfo.
    function convertUserFileToFileInfo(userFile) {
        var fileInfo = null;

        if (userFile) {
            fileInfo = new Object();
            fileInfo.FileId = FileUploadUtil.getGuid();
            fileInfo.FileSize = userFile.size;
            fileInfo.FileName = userFile.name;
            fileInfo.StateString = "Pending";
            fileInfo.MaxFileSize = maxFileSizeByByte;

            //added for resubmit link that need search parent document model by parent document number
            fileInfo.ParentAgencyCode = agencyCode;
            fileInfo.ParentDocumentNo = documentNo;
        }

        return fileInfo;
    }
};

var FileUploadUtil = new function () {
    this.getUploadControlHtml = getUploadControlHtml;
    this.getGuid = getGuid;
    this.clearFileInput = clearFileInput;
    this.updateProgressBar = updateProgressBar;
    this.isAllFileFinished = isAllFileFinished;
    this.selectFile = selectFile;
    this.isSupportedBrowser = isSupportedBrowser;

    function getUploadControlHtml(parentContainerId, labelText, isMultipleUpload, cssClass) {
        var html = String.format('<div class="{0}"><a tabindex="0" class="btnBrowser_html5 NotShowLoading" href="javascript:void(0);" onclick="event.stopPropagation();if (typeof(SetNotAskForSPEAR)!=\'undefined\') SetNotAskForSPEAR();invokeClick($(\'#fileInput_{2}\')[0]);"><span>{1}</span><input class="ACA_Hide" tabindex="-1" title="{1}" type="file" id="fileInput_{2}" onchange="FileUploadUtil.selectFile(\'{2}\')" {3} /></a></div>',
                    cssClass, labelText, parentContainerId, isMultipleUpload ? ' multiple="multiple"' : ' ');

        return html;
    }

    function getGuid() {
        var guid = '';
        for (var i = 1; i <= 8; i++) {
            guid += Math.floor((1 + Math.random()) * 0x10000).toString(16);
        }
        return guid;
    };

    function clearFileInput(fileObj) {
        //should override it's outerHtml(if not, it can't upload file A -> file A), so that it can upload the same file all the time.
        fileObj.outerHTML += "";
        fileObj.value = "";
    }

    function updateProgressBar(progressBarContainer, percent) {

        var pbHtml = getProcessBarHtml(percent);

        //  only used for Resubmit link in attachment list iframe.
        if (!$.exists('#' + progressBarContainer)) {
            if ($('#' + progressBarContainer, parent.document).find('#divProgressBar').length) {
                $('#' + progressBarContainer, parent.document).find('#divProgressBar').html(pbHtml);
            }
            if ($('#' + progressBarContainer, parent.document).find('.divProgressBar').length) {
                $('#' + progressBarContainer, parent.document).find('.divProgressBar').html(pbHtml);
            }
        } else {
            if ($('#' + progressBarContainer).find('#divProgressBar').length) {
                $('#' + progressBarContainer).find('#divProgressBar').html(pbHtml);
            }
            if ($('#' + progressBarContainer).find('.divProgressBar').length) {
                $('#' + progressBarContainer).find('.divProgressBar').html(pbHtml);
            }
        }

    }

    function getProcessBarHtml(percent) {
        percent = (percent >= 100 ? 100 : Math.round(percent)).toString() + '%';

        var result =
            '<div class="html5ProgressBar">' +
                '<div class="bgColor" style="width:' + percent + '"></div>' +
                '<font>' + percent + '</font>' +
            '</div>';

        return result;
    }

    function isAllFileFinished(fileInfoArray) {
        var finishedCount = 0;
        for (var i = 0; i < fileInfoArray.length; i++) {
            if (fileInfoArray[i].StateString == "Finished") {
                finishedCount++;
            }
        }

        if (finishedCount == fileInfoArray.length) {
            return true;
        } else {
            return false;
        }
    }

    function selectFile(controlIndentyId) {
        fileUploaderCollection[controlIndentyId].selectCompleted();
        $('#' + fileUploaderCollection[controlIndentyId].fileInputObjId).parent().focus();
    }

    function isSupportedBrowser(errorMsgId, errorMsg) {
        if (typeof (File) == 'undefined' || typeof (FileReader) == 'undefined') {
            showMessage(errorMsgId, errorMsg, "Error", true, 1, true);
            return false;
        }
    }
};

//uses web worker to calculate md5 hash. This is allows non-blocking, time-consuming task to run in parallel with the main thread
var FileUploadHashGenerator = function (fileId, finishedCallback) {
    var worker;

    this.isSupported = function () {
        return window.Worker ? true : false;
    };

    this.calculateMD5 = function (content, isLast) {
        if (this.isSupported && worker) {
            //send file ciontent to the worker
            worker.postMessage({ fileContent: content, isLast: isLast });
        }
    };

    //immediately terminates worker
    this.stop = function () {
        if (worker) {
            worker.terminate();
        }
    };

    //check if browser supports Web Worker
    if (this.isSupported) {
        worker = new Worker(GLOBAL_APPLICATION_ROOT + "Scripts/WebWorkers/CalculateMD5.js");

        worker.onmessage = function (event) {
            //when workers returns value, execute callback
            if (event.data.messageType === 'hash') {
                if (finishedCallback)
                    finishedCallback(event.data.messageData);
            } else if (event.data.messageType === 'error') {
                worker.terminate();
            }
        };
    }
};