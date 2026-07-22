Title: Live Content

Description: Fetched live

Source: https://data.egovoc.com/js/app.js

---

Highcharts.setOptions({
    lang: {
        decimalPoint: '.',
        thousandsSep: ','
    }
});

$(window).resize(function() {
   $('#dataTable').bootstrapTable('resetView');
});

var drillDown = function () {
    if( this.series.options.cty == "dept" || this.series.options.cty == 'revcat' || this.series.options.cty == 'table' || this.series.options.cty == 'prog' )
        location.href = window.location.href+'/'+this.series.options.cid;
};

var drillDownPie = function () {
    if( this.options.cty == "dept" || this.options.cty == 'revcat' || this.options.cty == 'table' || this.options.cty == 'prog' )
        location.href = window.location.href+'/'+this.options.cid;
};

var optPie = {
    chart: {
        type: 'pie'
    },
    title: {
        text: ''
    },
    credits: {
        enabled: false
    },
    plotOptions: {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: drillDownPie
                }
            },
            dataLabels: {
                enabled: true,
                format: '{point.name}: ${point.y:,.0f}'
            },
            showInLegend: true
        }
    },
    tooltip: {
        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>${point.y:,.0f}</b><br/>'
    },
    series: [],
	exporting: {
		sourceHeight: 1024,
		sourceWidth: 2048
	}
};

var optDollars = {
    chart: {},
    title: {
        text: ''
    },
    credits: {
        enabled: false
    },
    xAxis: {
        categories: [],
    },
    yAxis: {
        title: {
            text: 'Dollars'
        },
        labels: {
            formatter: function () {
                var ret = '',
                    multi,
                    axis = this.value,
                    numericSymbols = ['k', 'M', 'B', 'T'],
                    i = numericSymbols.length;
                while (i-- && ret === '') {
                    multi = Math.pow(1000, i + 1);
                    if (multi < this.value && numericSymbols[i] !== null) {
                        ret = Highcharts.numberFormat(this.value / multi, -1) + numericSymbols[i];
                    }
                }
                return ret;
            }
        }
    },
    series: [],
    tooltip: {
        //shared : true,
        pointFormat: '<span style="color:{point.color}">\u25CF</span> {series.name}: <b>${point.y:,.0f}</b><br/>'
    },
    plotOptions: {
        series: {
            cursor: 'pointer',
            trackByArea: true,
            point: {
                events: {
                    click: drillDown
                }
            },
            stacking: 'normal',
            dataLabels: {
                enabled: false
            },
            shadow: false
        }
    },
	exporting: {
		sourceHeight: 1024,
		sourceWidth: 2048
	}
};

var optPercent = {
    chart: {},
    title: {
        text: ''
    },
    credits: {
        enabled: false
    },
    xAxis: {
        categories: [],
    },
    yAxis: {
        title: {
            text: 'Percent'
        }
    },
    series: [],
    tooltip: {
        //shared : true,
        pointFormat: '<span style="color:{point.color}">\u25CF</span> {series.name}: <b>${point.y:,.0f}</b><br/>'
    },
    plotOptions: {
        series: {
            cursor: 'pointer',
            trackByArea: true,
            point: {
                events: {
                    click: drillDown
                }
            },
            stacking: 'percent',
            dataLabels: {
                enabled: false
            },
            shadow: false
        }
    },
	exporting: {
		sourceHeight: 1024,
		sourceWidth: 2048
	}
};

var optLine = {
    chart: {},
    title: {
        text: ''
    },
    credits: {
        enabled: false
    },
    xAxis: {
        categories: [],
    },
    yAxis: {
        title: {
            text: 'Dollars'
        },
        labels: {
            formatter: function () {
                var ret = '',
                    multi,
                    axis = this.value,
                    numericSymbols = ['k', 'M', 'B', 'T'],
                    i = numericSymbols.length;
                while (i-- && ret === '') {
                    multi = Math.pow(1000, i + 1);
                    if (multi < this.value && numericSymbols[i] !== null) {
                        ret = Highcharts.numberFormat(this.value / multi, -1) + numericSymbols[i];
                    }
                }
                return ret;
            }
        }
    },
    series: [],
    tooltip: {
        pointFormat: '<span style="color:{point.color}">\u25CF</span> {series.name}: <b>${point.y:,.0f}</b><br/>'
    },
    plotOptions: {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: drillDown
                }
            },
            dataLabels: {
                enabled: false
            }
        }
    },
	exporting: {
		sourceHeight: 1024,
		sourceWidth: 2048
	}
};

var openocApp = angular.module('openocApp', [
    'ngRoute',
    'openocControllers'
]);

openocApp.config(['$routeProvider',
    function ($routeProvider) {
        $routeProvider.
            when('/Main', {
                templateUrl: 'view/main.html',
                controller: 'MainCtrl'
            }).
            when('/Download', {
                templateUrl: 'view/download.html',
                controller: 'DownloadCtrl'
            }).
            when('/t0/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 't0Ctrl'
            }).
            when('/t1/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 't1Ctrl'
            }).
            when('/t2/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 't2Ctrl'
            }).
            when('/t3/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 't3Ctrl'
            }).
            when('/t4/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 't4Ctrl'
            }).
            when('/t5/:drillID?', {
                templateUrl: 'view/t0.html',
                controller: 't5Ctrl'
            }).
            when('/t6/:drillID?', {
                templateUrl: 'view/t0.html',
                controller: 't6Ctrl'
            }).
            when('/t7', {
                templateUrl: 'view/t0.html',
                controller: 't7Ctrl'
            }).
            when('/t8', {
                templateUrl: 'view/t0.html',
                controller: 't8Ctrl'
            }).
            when('/t9/:table?/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 't9Ctrl'
            }).
			when('/t10', {
                templateUrl: 'view/t0.html',
                controller: 't10Ctrl'
            }).
			when('/t11', {
                templateUrl: 'view/t0.html',
                controller: 't11Ctrl'
            }).
			when('/t12', {
                templateUrl: 'view/t0.html',
                controller: 't12Ctrl'
            }).
            when('/b0/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b0Ctrl'
            }).
            when('/b1/:drillID?', {
                templateUrl: 'view/t0.html',
                controller: 'b1Ctrl'
            }).
            when('/b2/:drillID?', {
                templateUrl: 'view/t0.html',
                controller: 'b2Ctrl'
            }).
            when('/b3/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b3Ctrl'
            }).
            when('/b4/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b4Ctrl'
            }).
            when('/b5/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b5Ctrl'
            }).
            when('/b6/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b6Ctrl'
            }).
            when('/b7/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b7Ctrl'
            }).
            when('/b8/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b8Ctrl'
            }).
            when('/b9/:table?/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b9Ctrl'
            }).
			when('/b10/:prog?/:dept?', {
                templateUrl: 'view/t0.html',
                controller: 'b10Ctrl'
            }).
			when('/b11', {
                templateUrl: 'view/t0.html',
                controller: 'b11Ctrl'
            }).
			when('/b12', {
                templateUrl: 'view/t0.html',
                controller: 'b12Ctrl'
            }).
            otherwise({
                redirectTo: '/Main'
            });
    }
]);


