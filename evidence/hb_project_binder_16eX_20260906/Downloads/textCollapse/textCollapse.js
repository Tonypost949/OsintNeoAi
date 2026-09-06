/**
* <pre>
* 
*  Accela Citizen Access
*  File: textCollapse.js
* 
*  Accela, Inc.
*  Copyright (C): 2010-2014
* 
*  Description:
* 
*  Notes:
* $Id: textCollapse.js 266252 2014-02-20 10:26:50Z ACHIEVO\james.shi $.
*  Revision History
*  &lt;Date&gt;,    &lt;Who&gt;,    &lt;What&gt;
* </pre>
*/
(function ($) {
    $.fn.Collapse = function (o) {
        var Container = getParentDocument().getElementById(o.containerId);

        if (o.line == 0) {
            return;
        }
        o = $.extend({}, $.fn.Collapse.defaults, o);

        return this.each(function () {
            var a = $(this), text = a.text(), originalCount = text.length;
            var h;
            var contentHeight = a.outerHeight();
            var isHidden = contentHeight == 0;

            if (!$(this).is(':visible')) {
                $(this).attr('IsHiddenEllipsis', 'y');
            }

            if (isHidden || (typeof (a.attr("isFinished")) != "undefined" && a.attr("isFinished") == "true")) {
                return;
            }

            //collapse link
            var hidecontent = $('<span class="ACA_LinkButton"><a id="lnkCollapse' + a.attr("id") + '" class="NotShowLoading" href="javascript:void(0);">' + o.collapse + '</a></span>');

            //ellipsis link
            var readmore = $('<span class="ACA_LinkButton"><a id="lnkExpand' + a.attr("id") + '" class="NotShowLoading" href="javascript:void(0);">' + o.readMore + '</a></span>');

            a.css({ display: "block", "word-wrap": "break-word" });
            var lineHeight = parseFloat(a.css("line-height"));

            if (isNaN(lineHeight) || lineHeight == 1) {
                replaceWithPartialText(1);
                lineHeight = a.outerHeight();
            }

            h = lineHeight * o.line * 1.1;

            //if content doesn't over flow the default line, will not cut the content
            if (contentHeight <= h) {
                a.text(text);
            }
            else {
                run();
            }

            function replaceWithPartialText(endIndex) {
                var str = text.substring(0, endIndex);
                a.text(str + o.instead);
                a.append('&nbsp;');
                a.append(readmore);

                $('#lnkExpand' + a.attr("id")).bind('click', function () {
                    if (o.isExpand) {
                        var beforeEllipsisHeight = $(a).parents("td").outerHeight();
                        a.text(text);
                        a.append('&nbsp;');
                        a.append(hidecontent);
                        $('#lnkCollapse' + a.attr("id")).bind('click', function () {
                            if (!o.isExpand) {
                                o.isExpand = true;
                                var beforeCollapseHeight = $(a).parents("td").outerHeight();
                                run();
                                var afterCollapseHeight = $(a).parents("td").outerHeight();
                                $('#lnkExpand' + a.attr("id")).focus();

                                if (Container != null) {
                                    Container.height = Container.offsetHeight - (beforeCollapseHeight - afterCollapseHeight);
                                }
                            }
                        });
                        o.isExpand = false;
                        var afterEllipsisHeight = $(a).parents("td").outerHeight();
                        $('#lnkCollapse' + a.attr("id")).focus();

                        if (Container != null) {
                            Container.height = Container.offsetHeight + (afterEllipsisHeight - beforeEllipsisHeight);
                        }
                    }
                });
            }

            function run() {
                var count = originalCount;
                var minIndex = 0;
                var maxIndex = count - 1;
                var index = maxIndex;

                while (count > 1) {
                    replaceWithPartialText(index);

                    if (a.outerHeight() > h) {
                        maxIndex = index;
                        index = Math.ceil((minIndex + maxIndex) / 2);
                    }
                    else {
                        minIndex = index;
                        index = Math.floor((minIndex + maxIndex) / 2);
                    }

                    if ((maxIndex - minIndex) <= 2) {
                        if (index > 2) {
                            replaceWithPartialText(index - 2);
                        }
                        break;
                    }

                    count--;
                }
            }

            if (contentHeight != 0) {
                a.attr("isFinished", true);
            }
        });
    };

    $.fn.Collapse.defaults = {
        // insead of over flow text
        instead: "...",
        // need to display line
        line: 2,
        // read more link
        readMore: "Read more",
        // cllapse link
        collapse: "Collapse",
        //expand or collapse
        isExpand: true
    };
})(jQuery);

function RebuildEllipsis(p) {
    $("[IsHiddenEllipsis='y']").each(function () {
        $(this).Collapse({ readMore: p.readMore, collapse: p.collapse, containerId: p.containerId });
    });
};