/**
 * <pre>
 * 
 *  Accela
 *  File: pagination.js
 * 
 *  Accela, Inc.
 *  Copyright (C): 2008-2014
 * 
 *  Description:
 * 
 *  Notes:
 * $Id: pagination.js 79503 2007-11-08 07:04:56Z ACHIEVO\jackie.yu $.
 *  Revision History
 *  &lt;Date&gt;,		&lt;Who&gt;,			&lt;What&gt;
 * </pre>
 */
/*
var navBar=new pagination(_records);
var navBar=new pagination(_records,_pagesize);
var navBar=new pagination(_records,_pagesize,_navLength);
navBar.type=0 || 1;//0--ajax, 1--normal type
navBar.styleType=0 || others number;//select one css style for navigation bar
navBar.create(_currentPage);
*/

var pagination = function (_records, _pagesize, _navLength) {
    //
    //page setting
    //
    this.records = parseInt(_records) || 0,
    this.pagesize = parseInt(_pagesize) || 20,
    this.navLength = parseInt(_navLength) || 10,
    this.pageCount = 0, // records/pagesize
    this.currentPage = 1,
    this.goNextOrPrevBar = 0, //-1 prevBar, 1 nextBar
    //this.type=0,//not support
    //this.isMiddleType=false,//not support

    //
    //layout setting
    //note:will not display if the value is empty
    //
    this.pageId = "pageid",
    this.navContainerId = "navContainer",

    this.firstPageText = '', //First
    this.prePageText = "&lt;Prev",
    this.preNavText = "...",
    this.nextNavText = "...",
    this.nextPageText = "Next&gt;",
    this.lastPageText = "", //Last
    this.leftFormat = "", //"["
    this.rightFormat = "", //"]"
    this.styleType = 0, //which config to select for style setting

    this.isAlwaysDisplayPreNavText = false, //if false, we will not show preNavText/nextNavTex when current page less then this.navLength
    this.isAlwaysDisplayNextNavText = false,
    this.isAlwaysDisplayPreText = true,
    this.isAlwaysDisplayNextText = true,

    //
    //message
    //the first and last page show in msgtext,just like "showing 4-13 of 100"
    //
		this.msgText = "Showing {0}-{1} of {2}",
    this.firstPageId = 1,
    this.lastPageId = 1,
    this.extensionText = "Additional Results:",

    //
    //methods
    //
    this.getMsg = function () {
        if (this.records == 0) {
            return "";
        }
        var first = (this.currentPage - 1) * this.pagesize + 1;

        var tmp = (this.currentPage) * this.pagesize;
        var last = tmp > this.records ? this.records : tmp;
        return this.msgText.format(first, last, this.records);
    },

    this.setMsg = function () {
        var msg = document.getElementById("inspectionMsg");
        if (msg) {
            msg.innerHTML = this.getMsg();
        }
    },

    this.getFirst = function () {
        if (this.firstPageText == "") {
            return "";
        }

        if (this.currentPage == 1) {
            return this.getTextItem(this.firstPageText);
        } else {
            return this.getLinkItem(this.firstPageText, 1);
        }

    },

    this.getExtension = function () {
        if (this.extensionText == "") {
            return "";
        }

        return this.getTextItem(this.extensionText);
    },

    this.getPreNav = function () {
        if (this.preNavText == "") {
            return "";
        }

        var isShow = false;
        var _offset = Math.ceil(this.navLength / 2);

        if (_offset < this.currentPage) {
            return this.getLinkItem(this.preNavText, this.currentPage - _offset);
        }

        if (this.isAlwaysDisplayPreNavText) {
            return this.getTextItem(this.preNavText, this.currentPage - _offset);
        }

        return "";
    },

    this.getPre = function () {
        if (this.prePageText == "") {
            return "";
        }

        if (this.currentPage > 1) {
            return this.getLinkItem(this.prePageText, this.currentPage - 1);
        }

        if (this.isAlwaysDisplayPreText) {
            return this.getTextItem(this.prePageText, 1);
        }

        return "";
    },

    this.getBar = function () {
        var html = '';

        var temp = Math.ceil(this.currentPage / this.navLength) - 1;
        var count = this.navLength * (temp + 1);
        var len = Math.ceil(this.navLength / 2) - 1;
        html += '<table role="presentation" border="0" nowrap="true"><tr>';

        if (this.currentPage <= len) {
            for (var i = temp * this.navLength + 1; i <= count; i++) {

                if (i > this.pageCount) {
                    break;
                }
                html += '<td class="aca_pagination_td">';
                if (i == this.currentPage) {
                    html += this.getTextItem(i);
                } else {
                    html += this.getLinkItem(i, i);
                }
                html += '</td>';
            }
        } else if (this.currentPage > (this.pageCount - len)) {
            for (var i = this.pageCount - len; i <= this.pageCount; i++) {
                if (i > this.pageCount) {
                    break;
                }
                html += '<td class="aca_pagination_td">';
                if (i == this.currentPage) {
                    html += this.getTextItem(i);
                } else {
                    html += this.getLinkItem(i, i);
                }
                html += '</td>';
            }
        } else {
            var temp1 = parseInt(this.currentPage - len);
            for (var i = temp1; i < this.currentPage; i++) {
                if (i > this.pageCount) {
                    break;
                }
                html += '<td class="aca_pagination_td">';
                html += this.getLinkItem(i, i);
                html += '</td>';
            }
            var temp2 = parseInt(this.currentPage + len);
            for (var i = this.currentPage; i <= temp2; i++) {
                if (i > this.pageCount) {
                    break;
                }
                html += '<td class="aca_pagination_td">';
                if (i == this.currentPage) {
                    html += this.getTextItem(i);
                } else {
                    html += this.getLinkItem(i, i);
                }
                html += '</td>';
            }
        }

        html += '</tr></table>';
        return html;
    },

    this.getNext = function () {
        if (this.nextPageText == "") {
            return "";
        }

        if (this.currentPage < this.pageCount) {
            return this.getLinkItem(this.nextPageText, this.currentPage + 1);
        }

        if (this.isAlwaysDisplayNextText) {
            return this.getTextItem(this.nextPageText);
        }

        return "";
    },

    this.getNextNav = function () {
        if (this.nextNavText == "") {
            return "";
        }

        if (this.pageCount <= this.navLength) {
            if (this.isAlwaysDisplayNextNavText) {
                return this.getTextItem(this.nextNavText, 0);
            }

            return "";
        }

        var _offset = Math.ceil(this.navLength / 2) + this.currentPage;
        var _lastpage = _offset > this.pageCount ? this.pageCount : _offset

        if (_lastpage < this.pageCount) {
            return this.getLinkItem(this.nextNavText, _lastpage);
        }

        if (this.isAlwaysDisplayNextNavText) {
            return this.getTextItem(this.nextNavText, _lastpage);
        }

        return "";
    },

    this.getLast = function () {
        if (this.lastPageText == "") {
            return "";
        }

        if (this.currentPage == this.records) {
            return this.getTextItem(this.lastPageText);
        }

        return this.getLinkItem(this.lastPageText, this.records);
    },

    this.getLinkText = function (txt) {
        var re = new RegExp(/^[1-9]{1}$/);
        if (re.test(txt)) {
            return this.leftFormat + txt + this.rightFormat;
        } else {
            return txt;
        }

    },

    this.getLinkItem = function (txt, i) {
        return '<a href="javascript:void(0);" onclick="linkClick(' + i + ')" class="' +
    					 config[this.styleType].linkClass + '" style="' + config[this.styleType].linkStyle + '"' +
    					 '">' + this.getLinkText(txt) + '</a>';
    },
    //current page item
    this.getTextItem = function (txt) {
        return '<span class="' + config[this.styleType].textClass + '" style="' + config[this.styleType].textStyle + '">' + txt + '</span>';
    },

    this.getFirstPageId = function () {
        return Math.ceil(this.currentPage / this.pagesize) * this.pagesize - this.pagesize + 1;
    },

    this.getLastPageId = function () {
        var tmp = Math.ceil(this.currentPage / this.pagesize) * this.pagesize;
        return tmp < this.pageCount ? tmp : this.pageCount;
    },

    this.setNextOrPrevBar = function () {
        if (this.currentPage == this.lastPageId) {
            this.goNextOrPrevBar = 1;
        } else if (this.currentPage == this.firstPageId && this.currentPage != 1) {
            this.goNextOrPrevBar = -1;
        } else {
            this.goNextOrPrevBar = 0;
        }
    },

    this.output = function () {
        if (this.pageCount < 2) {
            return;
        }
        if (this.records == 0) {
            return "";
        }
        var navBox = document.getElementById(this.navContainerId);
        if (!navBox) {
            alert('Can not find navContainer.');
        }
        //navBox.innerHTML=this.getFirst()+this.getPre()+this.getPreNav()+" "+this.getExtension()+this.getBar()+this.getNextNav()+this.getNext()+this.getLast();
        navBox.innerHTML = this.formatTable();
    },

    this.formatTable = function () {
        var table = "<center><table role='presentation' class='ACA_Table_Pages ACA_Table_Pages_FontSize'><tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr></table></center>";
        return table.format(
    							this.getFirst() + this.getPre(),
    							this.getPreNav(),
    							this.getBar(),
    							this.getNextNav(),
    							this.getNext() + this.getLast()
    					 );
    }

}

pagination.prototype.create=function(_currentPage){
		this.pageCount=Math.ceil(this.records/this.pagesize);
		this.firstPageId=this.getFirstPageId();
		this.lastPageId=this.getLastPageId();
		this.currentPage=_currentPage;
		this.setNextOrPrevBar();
		this.setMsg();
		this.output();

}

//
//style setting
//
var config=new Object();
config[0]={
    textClass: 'aca_simple_text font11px',
	textStyle:'',
	linkClass: 'aca_simple_text font11px',
	linkStyle:''
};

//
//utility
//

//var myText="showing {0} - {1} of {3}";
//var result=myText.format('abc', 'def', 'ghi');
//return "showing {abc} - {def} of {ghi}".
String.prototype.format = function () {

    if (arguments.length == 0) {
        return this;
    }
    var strOutput = '';
    for (var i = 0; i < this.length - 1; ) {
        if (this.charAt(i) == '{' && this.charAt(i + 1) != '{') {
            var index = 0, indexStart = i + 1;
            for (var j = indexStart; j <= this.length - 2; ++j) {
                var ch = this.charAt(j);
                if (ch < '0' || ch > '9') {
                    break;
                }
            }
            if (j > indexStart) {
                if (this.charAt(j) == '}' && this.charAt(j + 1) != '}') {
                    for (var k = j - 1; k >= indexStart; k--) {
                        index += (this.charCodeAt(k) - 48) * Math.pow(10, j - 1 - k);
                    }
                    var swapArg = arguments[index];
                    strOutput += swapArg;
                    i += j - indexStart + 2;
                    continue;
                }
            }
            strOutput += this.charAt(i);
            i++;
        } else {
            if ((this.charAt(i) == '{' && this.charAt(i + 1) == '{')
              || (this.charAt(i) == '}' && this.charAt(i + 1) == '}')) {
                i++;
            }
            strOutput += this.charAt(i);
            i++;
        }
    }
    strOutput += this.substr(i);
    return strOutput;
} 
 
 //
 // click url to redirect or call ajax
 //
 var rowCount=0;
function linkClick(_currentPage){
 	  //var nav=new pagination(rowCount);
      nav.create(_currentPage);
      FillInspection(_currentPage);
}
