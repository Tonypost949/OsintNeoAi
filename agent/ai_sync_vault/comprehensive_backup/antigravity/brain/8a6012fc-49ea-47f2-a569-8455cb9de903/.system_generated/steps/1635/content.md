Title: Live Content

Description: Fetched live

Source: https://data.egovoc.com/js/controllers.js

---

var openocControllers = angular.module('openocControllers', []);
var currentData = [];
var currentChart = "";

function priceFormatter(value) {
    if (value) {
        //return '<div><i class="glyphicon glyphicon-usd"></i>' + value.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,') + '</div>';
        return value.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,');
    }
    else
        return null;
}

function totalTextFormatter(data) {
	return 'Total';
}

function netCostTextFormatter(data) {
	return 'Difference';
}

function netCostPriceFormatter(data) {
	var expense = 0;
	var revenue = 0;
	var total = 0;
	var field = this.field;
	$.each(data, function (i, row) {
		if( row.name.indexOf(">Expenses<") > -1 ) {
			expense = row[field];
		}
		if( row.name.indexOf(">Revenue<") > -1 ) {
			revenue = row[field];
		}
	});
	
	total = expense - revenue;
	return total.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,');
}

function totalPriceFormatter(data) {
	var total = 0;
	var field = this.field;
	$.each(data, function (i, row) {
		if(!isNaN(row[field])) {
			total += row[field];
		}
	});
	return total.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,');
}

function cleanupNav() {
    $("#topNav").children().removeClass('active');
    $("#budgetNav").children().removeClass('active');
}

function createDisplay(dataurl, $http, $chartType, totalTypeNet) {
    $http.get(dataurl).success(function (data) {
        currentData = data;
        optDollars.chart.renderTo = 'graphContainer';
        optDollars.chart.type = 'area';
        optDollars.xAxis.categories = data.categories;
        optDollars.series = data.series;
        optPercent.xAxis.categories = data.categories;
        optPercent.series = data.series;
        optLine.xAxis.categories = data.categories;
        optLine.series = data.series;
        $("#ChartType").children().removeClass('active');
        $("#PieRange").empty();
        switch ($chartType) {
            case 'line':
                $("#btnLine").addClass('active');
                optLine.chart.renderTo = 'graphContainer';
                optLine.chart.type = 'line';
                var myChart = new Highcharts.Chart(optLine);
                break;
            case 'bar':
                $("#btnBar").addClass('active');
                optDollars.chart.renderTo = 'graphContainer';
                optDollars.chart.type = 'column';
                var myChart = new Highcharts.Chart(optDollars);
                break;
            case 'area':
                $("#btnArea").addClass('active');
                optDollars.chart.renderTo = 'graphContainer';
                optDollars.chart.type = 'area';
                var myChart = new Highcharts.Chart(optDollars);
                break;
            case 'barp':
                $("#btnBarP").addClass('active');
                optPercent.chart.renderTo = 'graphContainer';
                optPercent.chart.type = 'column';
                var myChart = new Highcharts.Chart(optPercent);
                break;
            case 'areap':
                $("#btnAreaP").addClass('active');
                optPercent.chart.renderTo = 'graphContainer';
                optPercent.chart.type = 'area';
                var myChart = new Highcharts.Chart(optPercent);
                break;
            case 'pie':
                $("#btnPie").addClass('active');
                for (var cat in data.categories) {
                    var field = data.categories[cat];
                    var button = '<button type="button" class="btn btn-default" colid="' + cat + '">' + field + '</button>';
                    if (cat == 0) {
                        button = '<button type="button" class="btn btn-default active" colid="' + cat + '">' + field + '</button>';
                    }
                    $("#PieRange").append(button);
                }
                var newData = [];
                for (var row in data.series) {
                    newData.push({
                        name: data.series[row].name,
                        y: data.series[row].data[0],
                        cid: data.series[row].cid,
                        cty: data.series[row].cty
                    });
                }
                optPie.series = [{
                    name: "BudgetData",
                    colorByPoint: true,
                    data: newData
                }
                ];

                optPie.chart.renderTo = 'graphContainer';
                var myChart = new Highcharts.Chart(optPie);

                $("#PieRange").on('click', '*', function () {
                    $("#PieRange").children().removeClass('active');
                    $(this).addClass('active');
                    var swapData = [];
                    for (var row in data.series) {
                        swapData.push({
                            name: data.series[row].name,
                            y: data.series[row].data[$(this).attr("colid")],
                            cid: data.series[row].cid,
                            cty: data.series[row].cty
                        });
                    }
                    optPie.series = [{
                        name: "BudgetData",
                        colorByPoint: true,
                        data: swapData
                    }
                    ];
                    optPie.chart.renderTo = 'graphContainer';
                    var myChart = new Highcharts.Chart(optPie);
                });
                break;
            default:
                $("#btnArea").addClass('active');
                var myChart = new Highcharts.Chart(optDollars);
        }
		
        var tableData = [];
        var columnData = [];
		if(totalTypeNet)
		{
			columnData.push({
				field: 'name',
				title: 'Name',
				align: 'center',
				valign: 'middle',
				sortable: true,
				footerFormatter: netCostTextFormatter
			});
			for (var cat in data.categories) {
				var field = data.categories[cat];
				columnData.push({
					field: data.categories[cat],
					title: data.categories[cat],
					align: 'center',
					valign: 'middle',
					sortable: true,
					formatter: priceFormatter,
					footerFormatter: netCostPriceFormatter
				});
			}
		}
		else
		{
	        columnData.push({
				field: 'name',
				title: 'Name',
				align: 'center',
				valign: 'middle',
				sortable: true,
				footerFormatter: totalTextFormatter
			});
			for (var cat in data.categories) {
				var field = data.categories[cat];
				columnData.push({
					field: data.categories[cat],
					title: data.categories[cat],
					align: 'center',
					valign: 'middle',
					sortable: true,
					formatter: priceFormatter,
					footerFormatter: totalPriceFormatter
				});
			}

		}
        for (var row in data.series) {
            //console.log(data.series[row].name);
            var result = {};
            if (data.series[row].cty == 'dept' || data.series[row].cty == 'revcat' || data.series[row].cty == 'table' || data.series[row].cty == 'prog') {
                result["name"] = '<a href="' + window.location.href + '/' + data.series[row].cid + '">' + data.series[row].name + '</a>';
            } else {
                result["name"] = data.series[row].name;
            }

            for (var i = 0; i < data.categories.length; i++) {
                result[data.categories[i]] = data.series[row].data[i];
            }
            //console.log(result);
            tableData.push(result);
        }

        $('#dataTable').bootstrapTable({
            data: tableData,
            columns: columnData,
            search: true,
            showExport: true,
            exportDataType: "all",
			showFooter: true,
			striped: true,
			pagination: false,
			classes: 'table table-hover table-condensed',
			height: '100%'
        });
    });
}

var lineChart = function () {
    $("#ChartType").children().removeClass('active');
    $("#btnLine").addClass('active');
    $("#PieRange").empty();
    currentChart = "line";
    optLine.chart.renderTo = 'graphContainer';
    optLine.chart.type = 'line';
    var myChart = new Highcharts.Chart(optLine);
};

var barChart = function () {
    $("#ChartType").children().removeClass('active');
    $("#btnBar").addClass('active');
    $("#PieRange").empty();
    currentChart = "bar";
    optDollars.chart.renderTo = 'graphContainer';
    optDollars.chart.type = 'column';
    var myChart = new Highcharts.Chart(optDollars);
};

var areaChart = function () {
    $("#ChartType").children().removeClass('active');
    $("#btnArea").addClass('active');
    $("#PieRange").empty();
    currentChart = "area";
    optDollars.chart.renderTo = 'graphContainer';
    optDollars.chart.type = 'area';
    var myChart = new Highcharts.Chart(optDollars);
};

var areaPercent = function () {
    $("#ChartType").children().removeClass('active');
    $("#btnAreaP").addClass('active');
    $("#PieRange").empty();
    currentChart = "areap";
    optPercent.chart.renderTo = 'graphContainer';
    optPercent.chart.type = 'area';
    var myChart = new Highcharts.Chart(optPercent);
};

var barPercent = function () {
    $("#ChartType").children().removeClass('active');
    $("#btnBarP").addClass('active');
    $("#PieRange").empty();
    currentChart = "barp";
    optPercent.chart.renderTo = 'graphContainer';
    optPercent.chart.type = 'column';
    var myChart = new Highcharts.Chart(optPercent);
};

var pieChart = function () {
    $("#ChartType").children().removeClass('active');
    $("#btnPie").addClass('active');
    $("#PieRange").empty();
    currentChart = "pie";
    for (var cat in currentData.categories) {
        var field = currentData.categories[cat];
        var button = '<button type="button" class="btn btn-default" colid="' + cat + '">' + field + '</button>';
        if (cat == 0) {
            button = '<button type="button" class="btn btn-default active" colid="' + cat + '">' + field + '</button>';
        }
        $("#PieRange").append(button);
    }
    var newData = [];
    for (var row in currentData.series) {
        newData.push({
            name: currentData.series[row].name,
            y: currentData.series[row].data[0],
            cid: currentData.series[row].cid,
            cty: currentData.series[row].cty
        });
    }
    optPie.series = [{
        name: "BudgetData",
        colorByPoint: true,
        data: newData
    }
    ];

    optPie.chart.renderTo = 'graphContainer';
    var myChart = new Highcharts.Chart(optPie);

    $("#PieRange").on('click', '*', function () {
        $("#PieRange").children().removeClass('active');
        $(this).addClass('active');
        var swapData = [];
        for (var row in currentData.series) {
            swapData.push({
                name: currentData.series[row].name,
                y: currentData.series[row].data[$(this).attr("colid")],
                cid: currentData.series[row].cid,
                cty: currentData.series[row].cty
            });
        }
        optPie.series = [{
            name: "BudgetData",
            colorByPoint: true,
            data: swapData
        }
        ];
        optPie.chart.renderTo = 'graphContainer';
        var myChart = new Highcharts.Chart(optPie);
    });
};

openocControllers.controller('MainCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $("#topNav").children().removeClass('active');
        $scope.PageTitle = 'OpenOC Data Tool';
    }
]);

openocControllers.controller('DownloadCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $("#topNav").children().removeClass('active');
        $scope.PageTitle = 'OpenOC Data Tool';
    }
]);


openocControllers.controller('t0Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't0';
        var title = 'Total Annual County Expenditures';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t1Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't1';
        var title = 'Total Salaries & Benefits Expenditures';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t2Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't2';
        var title = 'Total Services & Supplies Expenditures';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t3Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't3';
        var title = 'Capital Assets Expenditures';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t4Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't4';
        var title = 'Total Annual County Revenues - By department';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/data.php?ds=' + ds + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t5Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't5';
        var title = 'Total Annual County Revenues - By revenue type';
        $("#" + ds).addClass('active');
        if (!($routeParams.drillID == "undefined" || $routeParams.drillID == null)) {
            $http.get('db/revcat.php?id=' + $routeParams.drillID).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/data.php?ds=' + ds + '&revcat=' + $routeParams.drillID, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t6Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't6';
        var title = 'General Purpose Revenue';
        $("#" + ds).addClass('active');
        if (!($routeParams.drillID == "undefined" || $routeParams.drillID == null)) {
            $http.get('db/revcat.php?id=' + $routeParams.drillID).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/data.php?ds=' + ds + '&revcat=' + $routeParams.drillID, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t7Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't7';
        var title = 'Property Tax Revenue';
        $("#" + ds).addClass('active');
        // single layer
        createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
        $scope.PageTitle = title;

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t8Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't8';
        var title = 'Public Safety Sales Tax Revenue';
        $("#" + ds).addClass('active');
        // single layer
        createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
        $scope.PageTitle = title;

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t9Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 't9';
        var title = 'Net County Cost';
        $("#" + ds).addClass('active');
        if ((!($routeParams.table == "undefined" || $routeParams.table == null)) && (!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = $routeParams.table + ' -- ' + progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/data.php?ds=' + ds + '&table=' + $routeParams.table + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if ((!($routeParams.table == "undefined" || $routeParams.table == null)) && (!($routeParams.prog == "undefined" || $routeParams.prog == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading =  $routeParams.table + ' -- ' + data[0];
                createDisplay('db/data.php?ds=' + ds + '&table=' + $routeParams.table + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        } else if (!($routeParams.table == "undefined" || $routeParams.table == null)) {
            $scope.PageTitle = title;
            $scope.SubHeading = $routeParams.table;
            createDisplay('db/data.php?ds=' + ds + '&table=' + $routeParams.table, $http, currentChart, false);
        }
        else {
            createDisplay('db/data.php?ds=' + ds, $http, currentChart, true);
            $scope.PageTitle = title;
        }

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t10Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
		var ds = 't10';
        var title = 'Realignment Revenue';
        $("#" + ds).addClass('active');
        // single layer
        createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
        $scope.PageTitle = title;

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t11Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
		var ds = 't11';
        var title = 'Mental Health Services Act Revenue';
        $("#" + ds).addClass('active');
        // single layer
        createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
        $scope.PageTitle = title;

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('t12Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
		var ds = 't12';
        var title = 'Orange County Opioid Settlement Fund Revenue';
        $("#" + ds).addClass('active');
        // single layer
        createDisplay('db/data.php?ds=' + ds, $http, currentChart, false);
        $scope.PageTitle = title;

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);


openocControllers.controller('b0Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b0';
        var title = 'Total County Revenues (Excluding FBU and Changes to Reserves)';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b1Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b1';
        var title = 'General Fund Revenue';
        $("#" + ds).addClass('active');
        if (!($routeParams.drillID == "undefined" || $routeParams.drillID == null)) {
            $http.get('db/revcat.php?id=' + $routeParams.drillID).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&revcat=' + $routeParams.drillID, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b2Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b2';
        var title = 'General Purpose Revenue';
        $("#" + ds).addClass('active');
        if (!($routeParams.drillID == "undefined" || $routeParams.drillID == null)) {
            $http.get('db/revcat.php?id=' + $routeParams.drillID).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&revcat=' + $routeParams.drillID, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b3Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b3';
        var title = 'Property Tax Revenue';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b4Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b4';
        var title = 'Public Safety Sales Tax Revenue';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b5Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b5';
        var title = 'Total County Expenditures (Excluding Changes to Reserves)';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b6Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b6';
        var title = 'Salaries & Employee Benefits Expenditures';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b7Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b7';
        var title = 'Services & Supplies Expenditures';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b8Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b8';
        var title = 'Capital Assets Expenditures';
        $("#" + ds).addClass('active');
        if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }
        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b9Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
        var ds = 'b9';
        var title = 'Net County Cost';
        $("#" + ds).addClass('active');
        if ((!($routeParams.table == "undefined" || $routeParams.table == null)) && (!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = $routeParams.table + ' -- ' + progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&table=' + $routeParams.table + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if ((!($routeParams.table == "undefined" || $routeParams.table == null)) && (!($routeParams.prog == "undefined" || $routeParams.prog == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading =  $routeParams.table + ' -- ' + data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&table=' + $routeParams.table + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        } else if (!($routeParams.table == "undefined" || $routeParams.table == null)) {
            $scope.PageTitle = title;
            $scope.SubHeading = $routeParams.table;
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&table=' + $routeParams.table, $http, currentChart, false);
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, true);
            $scope.PageTitle = title;
        }

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b10Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
		var ds = 'b10';
        var title = 'Realignment Revenue';
        $("#" + ds).addClass('active');
		if ((!($routeParams.prog == "undefined" || $routeParams.prog == null)) && (!($routeParams.dept == "undefined" || $routeParams.dept == null))) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (progData) {
                $scope.PageTitle = title;
                $http.get('db/dept.php?id=' + $routeParams.dept).success(function (deptData) {
                    $scope.SubHeading = progData[0] + ' -- ' + deptData[0];
                    createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog + '&dept=' + $routeParams.dept, $http, currentChart, false);
                });
            });
        } else if (!($routeParams.prog == "undefined" || $routeParams.prog == null)) {
            $http.get('db/prog.php?id=' + $routeParams.prog).success(function (data) {
                $scope.PageTitle = title;
                $scope.SubHeading = data[0];
                createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp + '&prog=' + $routeParams.prog, $http, currentChart, false);
            });
        }
        else {
            createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
            $scope.PageTitle = title;
        }

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b11Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
		var ds = 'b11';
        var title = 'Mental Health Services Act Revenue';
        $("#" + ds).addClass('active');
        // single layer
        createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
        $scope.PageTitle = title;

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);

openocControllers.controller('b12Ctrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        if (currentChart == "")
            currentChart = "area";
        cleanupNav();
		var ds = 'b12';
        var title = 'Orange County Opioid Settlement Fund Revenue';
        $("#" + ds).addClass('active');
        // single layer
        createDisplay('db/quarter.php?ds=' + ds + '&fy=' + timePeriod.fy + '&fp=' + timePeriod.fp, $http, currentChart, false);
        $scope.PageTitle = title;

        $scope.line = lineChart;
        $scope.bar = barChart;
        $scope.area = areaChart;
        $scope.barp = barPercent;
        $scope.areap = areaPercent;
        $scope.pie = pieChart;
    }
]);


